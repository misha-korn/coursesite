from django.contrib.auth import get_user_model
from rest_framework import serializers
from review.models import Review

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'course', 'rating', 'student', 'created_at', 'description')
        read_only_fields = ('created_at', 'student')

