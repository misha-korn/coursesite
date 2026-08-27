from rest_framework import serializers

from course.models import Category, Course, Lesson
from review.serializators import ReviewSerializer
from user.serializators import PublicSerializer


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "parent")


class LessonListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "number", "duration_minutes", "course")


class LessonDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "number", "duration_minutes", "course", "content", "video_url")


class LessonWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "number", "duration_minutes", "course", "content", "video_url")


class CourseListSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    students_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "price",
            "status",
            "author",
            "category",
            "avg_rating",
            "students_count",
        )


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)
    reviews_preview = serializers.SerializerMethodField()
    reviews_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    students_count = serializers.IntegerField(read_only=True)
    author = PublicSerializer(read_only=True)

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "description",
            "price",
            "status",
            "author",
            "category",
            "lessons",
            "created_at",
            "avg_rating",
            "students_count",
            "reviews_preview",
            "reviews_count",
        )

    def get_reviews_preview(self, obj):
        qs = obj.reviews.all()[:5]
        return ReviewSerializer(qs, many=True, context=self.context).data


class CourseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "price", "category", "status"]
