from django.conf import settings
from django.db import models

from course.models import Course


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает"
        SUCCEEDED = "succeeded", "Оплачен"
        FAILED = "failed", "Ошибка"

    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="payments")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    external_id = models.CharField(max_length=200, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Платеж студента {self.student.id} на курс {self.course.id} со статусом {self.status}"
        )
