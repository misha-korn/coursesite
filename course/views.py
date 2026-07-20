from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from course.models import Category, Course, Lesson
from course.permissions import IsAuthorOrReadOnly, IsCourseAuthorOrReadOnly, IsEnrollmentOrAuthor
from course.serializators import (
    CategorySerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseWriteSerializer,
    LessonSerializer,
)

User = get_user_model()


class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        elif self.action == "retrieve":
            return CourseDetailSerializer
        return CourseWriteSerializer

    def get_queryset(self):
        qs = Course.objects.select_related("author", "category")
        if self.action == "retrieve":
            qs = qs.prefetch_related("lessons", "reviews")
        user = self.request.user
        if user.is_authenticated and user.role == User.Role.TEACHER:
            return qs.filter(Q(author=user) | Q(status="published"))
        return qs.filter(status="published")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsCourseAuthorOrReadOnly, IsEnrollmentOrAuthor]

    def get_queryset(self):
        user = self.request.user
        return (
            Lesson.objects.select_related("course")
            .filter(Q(course__author=user) | Q(course__enrollments__student=user))
            .distinct()
        )


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Category.objects.all()
