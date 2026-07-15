from rest_framework import serializers

from course.models import Category, Lesson, Course
from review.serializators import ReviewSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id','name','slug', 'parent')


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ('id','title', 'number', 'duration_minutes')


class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', 'title', 'price', 'status', 'author', 'category')


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'title', 'description', 'price', 'status',
                  'author', 'category', 'lessons', 'created_at')


class CourseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'price', 'category', 'status']
        read_only_fields = ['status']