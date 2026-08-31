import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from payment.models import Payment, Payout
from payment.services import (
    finalize_payment,
    mark_payout_failed,
    mark_payout_paid,
    provider_payout,
    verify_payment,
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_order_confirmation(self, course_id, email, email_verified):
    try:
        if not (email and email_verified):
            logger.info(
                "Не удалось отправить письмо по заказу %s, т. к. почта пользователя не указана",
                course_id,
            )
            return
        send_mail(
            subject=f"Заказ №{course_id} оформлен",
            message=f"Спасибо! Ваш заказ №{course_id} принят.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        logger.info("Письмо по заказу %s отправлено на %s", course_id, email)
    except Exception as exc:
        logger.error("Не удалось отправить письмо по заказу %s: %s", course_id, exc)
        return self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, retry_backoff=True)
def handle_payment_succeeded(self, external_id):
    try:
        try:
            payment = Payment.objects.select_related("course", "student").get(
                external_id=external_id
            )
        except Payment.DoesNotExist:
            return

        if payment.status == "succeeded":
            return

        if not verify_payment(payment):
            return

        finalize_payment(payment.id)
    except Exception as exc:
        logger.error("Не удалось обработать вебхук платежа %s: %s", external_id, exc)
        return self.retry(exc=exc)


@shared_task(bind=False, max_retries=3, retry_backoff=True)
def process_payout(payout_id):
    with transaction.atomic():
        try:
            payout = Payout.objects.select_for_update().select_related("method").get(id=payout_id)
        except Payout.DoesNotExist:
            logger.error("Выплата %s не найдена", payout_id)
            return

        if payout.status != "pending":
            logger.info("Выплата %s уже в состоянии %s", payout_id, payout.status)
            return

        payout.status = Payout.Status.PROCESSING
        payout.save(update_fields=["status"])

    try:
        provider_payout_id, provider_payout_status = provider_payout(
            payout=payout,
            id_key=str(payout_id),
        )
    except Exception as exc:
        logger.error("Выплата %s провалилась с ошибкой %s", payout_id, exc)
        mark_payout_failed(payout_id, str(exc))
        return

    if provider_payout_status == "succeeded":
        mark_payout_paid(payout_id, provider_payout_id)
    elif provider_payout_status == "pending":
        Payout.objects.filter(id=payout_id).update(external_id=provider_payout_id)
        logger.info("Выплата %s принята, ждём вебхук", payout_id)
    else:
        mark_payout_failed(payout_id, provider_payout_status)
