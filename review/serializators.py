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

    def validate(self, data):
        course = data.get("course")
        if not Enrollment.objects.filter(
            student=self.context["request"].user, course=course
        ).exists():
            raise serializers.ValidationError("Отзыв можно оставить только на купленный курс")
        return data
