import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from course.models import Category, Course
from payment.models import Payment

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def teacher(db):
    return User.objects.create_user("teacher1", password="pass12345", role=User.Role.TEACHER)


@pytest.fixture
def student(db):
    return User.objects.create_user("student1", password="pass12345", role=User.Role.STUDENT)


@pytest.fixture
def course(db, teacher):
    category = Category.objects.create(name="Test Category", slug="test-category")
    return Course.objects.create(
        author=teacher,
        title="Test Course",
        description="Test Course",
        status=Course.Status.PUBLISHED,
        category=category,
        price="1000.00",
    )


@pytest.fixture
def payment(db, student, course):
    return Payment.objects.create(
        student=student,
        course=course,
        amount="100.00",
        status=Payment.Status.PENDING,
        external_id="fake-123",
    )
