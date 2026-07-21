from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model

from enrollment.models import Enrollment
from payment.models import Payment
from payment.services import handle_payment_succeeded

User = get_user_model()


@pytest.mark.django_db
@patch("payment.services.send_order_confirmation")
def test_webhook_creates_enrollment(mock_email, payment, student, course):
    handle_payment_succeeded("fake-123")
    payment.refresh_from_db()
    assert payment.status == Payment.Status.SUCCEEDED
    assert Enrollment.objects.filter(student=student, course=course).count() == 1


@pytest.mark.django_db
@patch("payment.services.send_order_confirmation")
def test_webhook_is_idempotent(mock_email, payment, student, course):
    handle_payment_succeeded("fake-123")
    handle_payment_succeeded("fake-123")

    payment.refresh_from_db()

    assert Enrollment.objects.filter(student=student, course=course).count() == 1
    assert Payment.objects.filter(status="succeeded", student=student, course=course).count() == 1


@pytest.mark.django_db
@patch("payment.services.send_order_confirmation")
def test_webhook_unknown_id_does_nothing(mock_email, payment, student, course):
    handle_payment_succeeded("no-id")
    assert Enrollment.objects.filter(student=student, course=course).count() == 0
