import os
import uuid

from django.conf import settings
from django.db import transaction
from yookassa import Configuration
from yookassa import Payment as YooPayment

from enrollment.models import Enrollment
from payment.models import Payment
from payment.tasks import send_order_confirmation

Configuration.account_id = os.environ.get("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.environ.get("YOOKASSA_SECRET_KEY")
USE_REAL = os.environ.get("YOOKASSA_ENABLED") == "1"


def create_provider_payment(payment):
    return_url = f"{settings.SITE_URL}/courses/"

    if not USE_REAL:
        payment.external_id = f"fake-{uuid.uuid4()}"
        payment.save(update_fields=["external_id"])
        return return_url

    yoo = YooPayment.create(
        {
            "amount": {"value": f"{payment.amount:.2f}", "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": f"Курс #{payment.course_id}",
            "metadata": {"payment_id": payment.id},
        },
        uuid.uuid4(),
    )

    payment.external_id = yoo.id
    payment.save(update_fields=["external_id"])
    return yoo.confirmation.confirmation_url


@transaction.atomic
def handle_payment_succeeded(external_id):
    try:
        payment = (
            Payment.objects.select_for_update()
            .select_related("course", "student")
            .get(external_id=external_id)
        )
    except Payment.DoesNotExist:
        return

    if payment.status == "succeeded":
        return

    payment.status = "succeeded"
    payment.save(update_fields=["status"])

    Enrollment.objects.get_or_create(
        student=payment.student,
        course=payment.course,
        defaults={"price_paid": payment.amount},
    )

    transaction.on_commit(
        lambda: send_order_confirmation.delay(
            payment.course.id,
            payment.student.email,
        )
    )
