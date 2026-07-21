from decimal import Decimal
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

from payment.models import Payment

User = get_user_model()


@pytest.mark.django_db
@patch("payment.views.create_provider_payment", return_value="http://pay.test/")
def test_payment_create_once_with_course_price(mock_create, client, student, course):
    client.force_authenticate(student)

    res = client.post(reverse_lazy("payment-list"), {"course": course.id}, format="json")

    assert res.status_code == 201
    assert res.data["payment_url"] == "http://pay.test/"

    payments = Payment.objects.filter(student=student, course=course)
    payment = payments.first()

    assert payments.count() == 1
    assert payment.status == Payment.Status.PENDING
    assert payment.amount == Decimal(course.price)

    mock_create.assert_called_once()


@pytest.mark.django_db
@patch("payment.views.create_provider_payment", return_value="http://pay.test/")
def test_client_cannot_set_amount(mock_create, client, student, course):
    client.force_authenticate(student)

    res = client.post(
        reverse_lazy("payment-list"), {"course": course.id, "amount": "1.00"}, format="json"
    )

    payment = Payment.objects.get(student=student, course=course)

    assert res.status_code == 201
    assert payment.amount == Decimal(course.price)
