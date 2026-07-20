import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_order_confirmation(self, course_id, email):
    try:
        if not email:
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
