from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from enrollment.models import Certificate, Enrollment, LessonProgress
from enrollment.serializators import (
    CertificateSerializer,
    EnrollmentSerializer,
    LessonProgressSerializer,
)
from enrollment.services import issue_certificate


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user).select_related(
            "student", "course"
        )


class LessonProgressViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = LessonProgressSerializer

    def get_queryset(self):
        return LessonProgress.objects.filter(student=self.request.user).select_related("lesson")

    def perform_create(self, serializer):
        progress = serializer.save(student=self.request.user)
        if progress.is_completed:
            issue_certificate(self.request.user, progress.lesson.course.id)

    def perform_update(self, serializer):
        progress = serializer.save()
        if progress.is_completed:
            issue_certificate(self.request.user, progress.lesson.course.id)


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CertificateSerializer

    def get_queryset(self):
        return Certificate.objects.filter(student=self.request.user).select_related("course")
