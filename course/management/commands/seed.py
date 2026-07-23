from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import transaction

from course.models import Category, Course, Lesson

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database"

    @transaction.atomic
    def handle(self, *args, **options):
        if Course.objects.exists():
            self.stdout.write("Database Seeded")
            return

        teacher = User.objects.create_user(
            username="demo-teacher",
            password="demo-teacher123DEMO-TEACHER123",
            email="",
            role=User.Role.TEACHER,
        )

        programming = Category.objects.create(
            name="Programming",
            slug="programming",
        )

        course = Course.objects.create(
            title="Django REST API",
            description="Django rest-framework",
            status=Course.Status.PUBLISHED,
            category=programming,
            author=teacher,
            price="2990.00",
        )

        for i, title in enumerate(["Введение", "Модели и ORM", "DRF", "Деплой"], start=1):
            Lesson.objects.create(
                course=course,
                title=title,
                number=i,
                content=f"Content of lesson {title}...",
                duration_minutes=20,
            )

        return self.stdout.write(self.style.SUCCESS("Successfully created database"))
