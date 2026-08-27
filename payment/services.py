import os
import uuid
import ipaddress
import logging

from django.conf import settings
from django.db import transaction
from yookassa import Configuration
from yookassa import Payment as YooPayment

from enrollment.models import Enrollment
from payment.models import Payment
from payment.tasks import send_order_confirmation

from decimal import Decimal

Configuration.account_id = os.environ.get("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.environ.get("YOOKASSA_SECRET_KEY")
YOOKASSA_ENABLED = os.environ.get("YOOKASSA_ENABLED") == "1"

logger = logging.getLogger("payment.services")

YOOKASSA_NETWORKS = [
    "185.71.76.0/27",
    "185.71.77.0/27",
    "77.75.153.0/25",
    "77.75.154.128/25",
    "77.75.156.11/32",
    "77.75.156.35/32",
    "2a02:5180::/32",
]


def is_yookassa_ip(ip):
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return any(addr in ipaddress.ip_network(net) for net in YOOKASSA_NETWORKS)


def verify_payment(payment):
    if not YOOKASSA_ENABLED:
        return True
    try:
        remote = YooPayment.find_one(payment.external_id)
    except Exception as exc:
        logger.error("Не удалось получить информацию по платежу %s: %s", payment.external_id, exc)
        return False

    if remote is None:
        return False

    if remote.status != "succeeded":
        logger.error("Платеж %s имеет статус: %s", payment.external_id, remote.status)
        return False

    if Decimal(remote.amount.value) != payment.amount:
        logger.error(
            "Сумма платежа у провайдера %s не совпадает с нашей: %s",
            Decimal(remote.amount.value),
            payment.amount,
        )
        return False

    return True


def create_provider_payment(payment):
    return_url = f"{settings.SITE_URL}/courses/"

    if not YOOKASSA_ENABLED:
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

    if not verify_payment(payment):
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
