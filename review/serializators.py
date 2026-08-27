from django.contrib.auth import get_user_model
from rest_framework import serializers

from enrollment.models import Enrollment
from review.models import Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ("id", "course", "rating", "student", "created_at", "description")
        read_only_fields = ("created_at", "student")
        ordering = ("-created_at", )

    def validate(self, data):
        if self.instance is None:
            course = data.get("course")
            if not Enrollment.objects.filter(
                student=self.context["request"].user, course=course
            ).exists():
                raise serializers.ValidationError("Отзыв можно оставить только на купленный курс")
            if Review.objects.filter(
                course=course,
                student=self.context["request"].user,
            ).exists():
                raise serializers.ValidationError("Нельзя оставить 2 отзыва на 1 курс")
        elif "course" in data and self.instance.course_id != data["course"]:
            raise serializers.ValidationError("Курс объекта нельзя изменить")
        return data

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Оценка должна быть от 1 до 5")
        return value