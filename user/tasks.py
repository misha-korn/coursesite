import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_reset_password_confirmation(self, email, uid, token):
    link = f"{settings.SITE_URL}/reset-password/{token}/"

    try:
        if not email:
            logger.info(
                "Не удалось отправить письмо восстановления, т. к. почта пользователя не указана",
            )
            return
        send_mail(
            subject="Восстановление пароля",
            message=(
                f"Чтобы восстановить пароль перейдите по ссылке:\n{link}\n"
                "Ссылка действительна 3 дня.\n"
                "Если вы не запрашивали смену пароля, то проигнорируйте это письмо."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        logger.info("Письмо восстановления отправлено на %s", email)
    except Exception as exc:
        logger.error("Не удалось отправить письмо восстановления: %s", exc)
        return self.retry(exc=exc)