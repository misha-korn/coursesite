import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_register_create_user(client):
    res = client.post(
        reverse_lazy("register"),
        {"username": "Gregoriy", "email": "", "password": "verystrongpass123"},
        format="json",
    )

    assert res.status_code == 201
    assert User.objects.filter(username="Gregoriy").exists()

@pytest.mark.django_db
def test_register_weak_password_user(client):
    res = client.post(
        reverse_lazy("register"),
        {"username": "Peter", "email": "", "password": "123"},
        format="json",
    )

    assert res.status_code == 400

@pytest.mark.django_db
def test_login_blocked_after_5_wrong_passwords(client, student):
    res = client.post(
        reverse_lazy("login"),
        {"username": "student1", "email": "", "password": "pass12345"},
        format="json",
    )

    assert res.status_code == 200

    for i in range(5):
        res = client.post(
            reverse_lazy("login"),
            {"username": "student1", "email": "", "password": "pass54321"},
            format="json",
        )

        assert res.status_code == 401

    res = client.post(
        reverse_lazy("login"),
        {"username": "student1", "email": "", "password": "pass12345"},
        format="json",
    )

    assert res.status_code != 200