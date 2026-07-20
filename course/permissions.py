from rest_framework import permissions

from enrollment.models import Enrollment


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsCourseAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.course.author == request.user


class IsEnrollmentOrAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.course.author == request.user:
            return True
        return Enrollment.objects.filter(student=request.user, course=obj.course).exists()
