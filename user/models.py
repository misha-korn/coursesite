from django.contrib.auth.models import AbstractUser
from django.db import models

from user.services import user_image_path


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Студент"
        TEACHER = "teacher", "Преподаватель"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    image = models.ImageField(upload_to=user_image_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username
