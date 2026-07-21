import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy

User = get_user_model()


@pytest.mark.django_db
def test_stranger_cannot_change_other_courses(client, course, student):
    client.force_authenticate(user=student)

    res = client.patch(
        reverse_lazy("course-detail", args=[course.id]), {"title": "Взломали"}, format="json"
    )

    assert res.status_code == 403
    course.refresh_from_db()
    assert course.title == "Test Course"


@pytest.mark.django_db
def test_author_can_change_own_courses(client, course, teacher):
    client.force_authenticate(user=teacher)

    res = client.patch(
        reverse_lazy("course-detail", args=[course.id]), {"title": "Меняю свой курс"}, format="json"
    )

    assert res.status_code == 200
    course.refresh_from_db()
    assert course.title == "Меняю свой курс"
