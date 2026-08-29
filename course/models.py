from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True, related_name="children"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="courses/%Y/%m", null=True, blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PUBLISHED = "published", "Опубликован"

    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses"
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="enrollment.Enrollment", related_name="enrolled_courses"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=["status", "price"], name="course_status_price_i"),
            models.Index(fields=["status", "-created_at"], name="course_status_-created_at_i"),
            models.Index(fields=["status", "views"], name="course_status_views_i"),
        ]


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=100)
    number = models.PositiveIntegerField()
    content = models.TextField()
    video_url = models.URLField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "number",
        ]
        unique_together = ("course", "number")

    def __str__(self):
        return self.title
