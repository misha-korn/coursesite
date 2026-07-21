from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Avg, Count, Q
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from course.models import Category, Course, Lesson
from course.permissions import IsAuthorOrReadOnly, IsCourseAuthorOrReadOnly, IsEnrollmentOrAuthor
from course.serializators import (
    CategorySerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    CourseWriteSerializer,
    LessonDetailSerializer,
    LessonListSerializer,
    LessonWriteSerializer,
)
from course.services import register_view

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
        qs = Course.objects.select_related("author", "category").annotate(
            avg_rating=Avg("reviews__rating"), students_count=Count("enrollments", distinct=True)
        )
        if self.action == "retrieve":
            qs = qs.prefetch_related("lessons", "reviews")
        user = self.request.user
        if user.is_authenticated and user.role == User.Role.TEACHER:
            return qs.filter(Q(author=user) | Q(status="published"))
        return qs.filter(status="published")

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def list(self, request, *args, **kwargs):
        data = cache.get("course_list")
        if data is None:
            data = self.get_serializer(self.get_queryset()).data
            cache.set("course_list", data, 60 * 15)
        page = self.paginate_queryset(data)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_authenticated:
            register_view(instance.id, request.user.id)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class LessonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsCourseAuthorOrReadOnly, IsEnrollmentOrAuthor]

    def get_queryset(self):
        user = self.request.user
        qs = (
            Lesson.objects.select_related("course")
            .filter(Q(course__author=user) | Q(course__enrollments__student=user))
            .distinct()
        )
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return LessonListSerializer
        elif self.action == "retrieve":
            return LessonDetailSerializer
        return LessonWriteSerializer

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        if course.author != self.request.user:
            raise PermissionDenied("Уроки можно добавлять только в свой курс")
        serializer.save()


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Category.objects.all()

    def list(self, request, *args, **kwargs):
        data = cache.get("category_list")
        if data is None:
            data = self.get_serializer(self.get_queryset()).data
            cache.set("category_list", data, 60*15)
        page = self.paginate_queryset(data)
        if page is not None:
            return self.get_paginated_response(page)
        return Response(data)
