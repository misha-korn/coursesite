import ipaddress
import logging
import os
import uuid
from decimal import ROUND_HALF_UP, Decimal

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from yookassa import Configuration
from yookassa import Payment as YooPayment

from enrollment.models import Enrollment
from payment.models import BalanceEntry, Payment, Payout, PayoutMethod

Configuration.account_id = os.environ.get("YOOKASSA_SHOP_ID")
Configuration.secret_key = os.environ.get("YOOKASSA_SECRET_KEY")
YOOKASSA_ENABLED = os.environ.get("YOOKASSA_ENABLED") == "1"
YOOKASSA_PAYOUTS_ENABLED = os.environ.get("YOOKASSA_PAYOUTS_ENABLED") == "1"
YOOKASSA_PAYOUT_AGENT_ID = os.environ.get("YOOKASSA_PAYOUT_AGENT_ID")
YOOKASSA_PAYOUT_SECRET_KEY = os.environ.get("YOOKASSA_PAYOUT_SECRET_KEY")

PAYOUT_API_URL = "https://api.yookassa.ru/v3/payouts"

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

TWO_PLACES = Decimal(10) ** -2

User = get_user_model()


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

    from payment.tasks import send_order_confirmation

    transaction.on_commit(
        lambda: send_order_confirmation.delay(
            payment.course.id,
            payment.student.email,
            payment.student.email_verified,
        )
    )


def split_amount(amount: Decimal, rate: Decimal):
    commission = (amount * rate / Decimal(100)).quantize(TWO_PLACES, ROUND_HALF_UP)
    author_amount = amount - commission
    return commission, author_amount


def get_balance(user_id):
    balance = BalanceEntry.objects.filter(author_id=user_id).aggregate(
        total=Coalesce(Sum("amount"), Decimal("0.00"))
    )

    return balance["total"]


@transaction.atomic
def request_payout(author, amount):
    User.objects.select_for_update().get(id=author.id)

    if amount <= Decimal("0.00"):
        raise ValidationError("Cумма должна быть больше нуля")
    if amount > get_balance(author.id):
        raise ValidationError("Недостаточно средств")

    method = (
        PayoutMethod.objects.filter(author=author, is_active=True, is_default=True)
        .exclude(verified_at=None)
        .first()
    )

    if method is None:
        raise ValidationError("Привяжите и подтвердите реквизит для выплаты с баланса")

    payout = Payout.objects.create(
        author=author,
        amount=amount,
        method=method,
    )

    BalanceEntry.objects.create(
        payout=payout,
        kind=BalanceEntry.Kind.PAYOUT,
        amount=-amount,
        author=author,
    )

    from payment.tasks import process_payout

    transaction.on_commit(lambda: process_payout.delay(payout.id))

    return payout


@transaction.atomic
def mark_payout_paid(payout_id, external_id):
    payout = Payout.objects.select_for_update().get(id=payout_id)

    if payout.status == Payout.Status.PAID:
        return

    payout.status = Payout.Status.PAID
    payout.external_id = external_id
    payout.paid_at = timezone.now()
    payout.save(update_fields=["status", "paid_at", "external_id"])

    return payout


@transaction.atomic
def mark_payout_failed(payout_id, reason):
    payout = Payout.objects.select_for_update().get(id=payout_id)

    if payout.status == Payout.Status.FAILED:
        return

    payout.status = Payout.Status.FAILED
    payout.save(update_fields=["status"])

    BalanceEntry.objects.get_or_create(
        payout=payout,
        kind=BalanceEntry.Kind.ADJUSTMENT,
        defaults={
            "amount": Decimal(payout.amount),
            "author": payout.author,
            "comment": f"Возврат по неудачной выплате {payout.id}: {reason}"[:255],
        },
    )

    return payout


@transaction.atomic
def set_default_payout_method(method_id, author_id):
    method = PayoutMethod.objects.select_for_update().get(
        id=method_id, author_id=author_id, is_active=True
    )
    (
        PayoutMethod.objects.filter(author_id=author_id, is_active=True)
        .exclude(pk=method_id)
        .update(is_default=False)
    )

    method.is_default = True
    method.save(update_fields=["is_default"])
    return method


def provider_payout(payout, id_key):
    if not YOOKASSA_PAYOUTS_ENABLED:
        return f"fake-payout-{payout.id}", "succeeded"
    if payout.method is None:
        raise ValidationError(f"У выплаты {payout.id} отсутствуют реквизиты")

    body = {
        "amount": {"value": f"{payout.amount:.2f}", "currency": "RUB"},
        "payout_token": payout.method.token,
        "description": f"Выплата по заявке {payout.id}",
        "metadata": {"payout_id": str(payout.id)},
    }

    response = requests.post(
        PAYOUT_API_URL,
        json=body,
        auth=(YOOKASSA_PAYOUT_AGENT_ID, YOOKASSA_PAYOUT_SECRET_KEY),
        headers={"Idempotence-Key": id_key},
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    return data["id"], data["status"]


def verify_payout_method(method):
    if not YOOKASSA_PAYOUTS_ENABLED:
        method.verified_at = timezone.now()
        method.save(update_fields=["verified_at"])
        return
    ...
