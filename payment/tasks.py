import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from enrollment.models import Enrollment
from payment.models import BalanceEntry, Payment
from payment.services import split_amount, verify_payment

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


@transaction.atomic
def finalize_payment(payment_id):
    try:
        payment = (
            Payment.objects.select_for_update()
            .select_related("course", "student", "course__author")
            .get(id=payment_id)
        )
    except Payment.DoesNotExist:
        return

    if payment.status == Payment.Status.SUCCEEDED:
        return

    rate = settings.PLATFORM_COMMISSION_RATE

    commission, author_amount = split_amount(payment.amount, rate=rate)

    payment.commission_amount = commission
    payment.author_amount = author_amount
    payment.commission_rate = rate
    payment.status = Payment.Status.SUCCEEDED

    payment.save(update_fields=["status", "commission_amount", "author_amount", "commission_rate"])

    Enrollment.objects.get_or_create(
        student=payment.student,
        course=payment.course,
        defaults={"price_paid": payment.amount},
    )
    BalanceEntry.objects.get_or_create(
        kind=BalanceEntry.Kind.EARNING,
        payment=payment,
        defaults={
            "amount": payment.author_amount,
            "author": payment.course.author,
        },
    )

    transaction.on_commit(
        lambda: send_order_confirmation.delay(
            payment.course.id,
            payment.student.email,
            payment.student.email_verified,
        )
    )
