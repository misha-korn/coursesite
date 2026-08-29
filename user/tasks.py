import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_reset_password_confirmation(self, email, email_verified, token):
    link = f"{settings.SITE_URL}/reset-password/{token}/"

    try:
        if not (email and email_verified):
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

@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_change_email_confirmation(self, new_email, token):
    link = f"{settings.SITE_URL}/change-email/{token}/"

    try:
        if not new_email:
            logger.info(
                "Не удалось отправить письмо восстановления, т. к. почта пользователя не указана",
            )
            return
        send_mail(
            subject="Подтверждения нового адреса",
            message=(
                f"Чтобы привязать этот адрес к аккаунту перейдите по ссылке:\n{link}\n"
                "Ссылка действительна 1 день.\n"
                "Если вы не запрашивали смену почты, то проигнорируйте это письмо."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[new_email],
        )
        logger.info("Письмо смены почты отправлено на %s", new_email)
    except Exception as exc:
        logger.error("Не удалось отправить письмо смены почты: %s", exc)
        return self.retry(exc=exc)

@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_change_email_warning(self, old_email, old_email_verified, new_email):
    try:
        if not (old_email and old_email_verified):
            logger.info(
                "Не удалось отправить оповещения, т. к. почта пользователя не указана",
            )
            return
        send_mail(
            subject="Запрошена смена почты на вашем аккаунте",
            message=(
                f"Была запрошена смена почты для вашего аккаунта на {new_email}.\n"
                "Если это вы, то ничего не делайте.\n"
                "Если это не вы, то срочно смените пароль от своего аккаунта."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[old_email],
        )
        logger.info("Письмо оповещения отправлено на %s", old_email)
    except Exception as exc:
        logger.error("Не удалось отправить письмо оповещения: %s", exc)
        return self.retry(exc=exc)

@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_verify_email_confirmation(self, email, token):
    link = f"{settings.SITE_URL}/verify-email/{token}/"

    try:
        if not email:
            logger.info(
                "Не удалось отправить письмо подтверждения почты, т. к. почта пользователя не указана",
            )
            return
        send_mail(
            subject="Подтверждения почтового адреса",
            message=(
                f"Чтобы привязать этот адрес к аккаунту перейдите по ссылке:\n{link}\n"
                "Ссылка действительна 1 день.\n"
                "Если вы не запрашивали подтверждение почты, то проигнорируйте это письмо."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        logger.info("Письмо подтверждения почты отправлено на %s", email)
    except Exception as exc:
        logger.error("Не удалось отправить письмо подтверждения почты: %s", exc)
        return self.retry(exc=exc)