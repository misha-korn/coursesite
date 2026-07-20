import logging
from datetime import timedelta
from io import BytesIO

from celery import shared_task
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.utils import timezone
from reportlab.pdfgen import canvas

from enrollment.models import Certificate, Enrollment, LessonProgress

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, retry_backoff=True)
def generate_pdf_certificate(self, certificate_id):
    try:
        cert = Certificate.objects.select_related("student", "course").get(id=certificate_id)
        course = cert.course

        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 700, "Сертификат")
        p.drawString(100, 670, f"Выдан: {cert.student.username}")
        p.drawString(100, 640, f"Курс: {course.title}")
        p.drawString(100, 610, f"Дата: {cert.issued_at:%Y-%m-%d %H:%M:%S}")
        p.showPage()
        p.save()

        cert.pdf_file.save(f"certificate_{cert.id}.pdf", ContentFile(buffer.getvalue()))
        logger.info("Сертификат %s сгенерирован", cert.id)
    except Exception as exc:
        logger.error("Ошибка генерации сертификата %s: %s", certificate_id, exc)
        return self.retry(exc=exc)


@shared_task()
def send_abandoned_reminders():
    threshold = timezone.now() - timedelta(days=7)
    enrollments = Enrollment.objects.filter(created_at__lt=threshold).select_related(
        "student", "course__lessons"
    )

    count = 0

    for enrollment in enrollments:
        total = enrollment.course.lessons.count()
        done = LessonProgress.objects.filter(
            student=enrollment.student,
            lesson__course=enrollment.course,
            is_completed=True,
        ).count()

        if total and done < total:
            send_reminder_email.delay(enrollment.student.name, enrollment.course.title)
            count += 1
    logger.info("Отправлено напоминаний %s", count)


@shared_task(bind=True, max_retries=3, retry_backoff=True)
def send_reminder_email(self, email, title):
    try:
        if not email:
            logger.info(
                "Не удалось отправить письмо-напоминание, т. к. почта пользователя не указана"
            )
            return
        send_mail(
            subject=f"Продолжите курс {title}",
            message="Вы давно не заходили. Курс вас ждет!",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        logger.info("Письмо-напоминание отправлено на %s", email)
    except Exception as exc:
        logger.error("Не удалось отправить письмо-напоминание: %s", exc)
        return self.retry(exc=exc)
