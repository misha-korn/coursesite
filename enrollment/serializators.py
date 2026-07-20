from rest_framework import serializers

from enrollment.models import Certificate, Enrollment, LessonProgress


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ("id", "student", "course", "created_at", "price_paid")
        read_only_fields = ("student", "created_at", "price_paid")


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ("id", "course", "student", "issued_at", "pdf_file")
        read_only_fields = ("id", "course", "student", "issued_at", "pdf_file")


class LessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonProgress
        fields = (
            "id",
            "student",
            "lesson",
            "is_completed",
            "completed_at",
        )
        read_only_fields = ("student", "completed_at")
