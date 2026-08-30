from django.conf import settings
from django.db import models
from django.db.models import Q

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
    updated_at = models.DateTimeField(auto_now=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    author_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["external_id"],
                condition=~Q(external_id=""),
                name="unique_payment_external_id",
            )
        ]

    def __str__(self):
        return (
            f"Платеж студента {self.student.id} на курс {self.course.id} со статусом {self.status}"
        )


class Payout(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает"
        PROCESSING = "processing", "В обработке"
        PAID = "paid", "Оплачен"
        FAILED = "failed", "Ошибка"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payouts"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    external_id = models.CharField(max_length=200, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["author", "status"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="payout_amount_greater_than_zero",
            )
        ]

    def __str__(self):
        return f"Выплата автору {self.author_id} на сумму в {self.amount} со статусом {self.status}"


class BalanceEntry(models.Model):
    class Kind(models.TextChoices):
        EARNING = "earning", "Начисление"
        PAYOUT = "payout", "Выплата"
        REFUND = "refund", "Возврат"
        ADJUSTMENT = "adjustment", "Корректировка"

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="balance_entries"
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment = models.ForeignKey(
        Payment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="balance_entries",
    )
    payout = models.ForeignKey(
        Payout,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="balance_entries",
    )
    comment = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["author", "created_at"])]
        constraints = [
            models.UniqueConstraint(
                fields=["payment"],
                condition=Q(kind="earning"),
                name="uniq_earning_per_payment",
            ),
            models.UniqueConstraint(
                fields=["payout"],
                condition=Q(kind="payout"),
                name="uniq_payout_per_payout",
            ),
        ]

    def __str__(self):
        return f"Проводка {self.kind} автору {self.author_id} на {self.amount}"
