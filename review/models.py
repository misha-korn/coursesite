from django.conf import settings
from django.db import models

from course.models import Course


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveIntegerField()
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    class Meta:
        unique_together = ("student", "course")
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name="rating_between_1_and_5",
            )
        ]

    def __str__(self):
        return f"Отзыв студента {self.student.id} на курс {self.course.id} с оценкой {self.rating}"
