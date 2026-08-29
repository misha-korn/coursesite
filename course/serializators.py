import environ
from rest_framework import serializers

from config.settings.base import BASE_DIR
from course.models import Category, Course, CourseImage, Lesson, LessonImage
from review.serializators import ReviewSerializer
from user.serializators import PublicSerializer

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / ".env")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "parent")


class LessonImageSerializer(serializers.ModelSerializer):
    MAX_COUNT_LESSON_IMAGES = env.int("MAX_COUNT_LESSON_IMAGES")

    class Meta:
        model = LessonImage
        fields = (
            "id",
            "lesson",
            "image",
            "is_main",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def validate(self, data):
        if self.instance:
            lesson = self.instance.lesson
        else:
            lesson = data["lesson"]
        if self.context["request"].user != lesson.course.author:
            raise serializers.ValidationError("Нельзя загрузить фото к чужому ресурсу")
        if lesson.lesson_images.count() >= self.MAX_COUNT_LESSON_IMAGES and not self.instance:
            raise serializers.ValidationError("К ресурсу можно загрузить максимум 5 фото")

        return data


class LessonListSerializer(serializers.ModelSerializer):
    image_preview = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ("id", "title", "number", "duration_minutes", "course", "image_preview")

    def get_image_preview(self, obj):
        lesson_image = obj.lesson_images.filter(is_main=True).first()
        if lesson_image is None:
            return None
        if self.request:
            return self.request.build_absolute_uri(lesson_image.image)
        return lesson_image.image.url


class LessonDetailSerializer(serializers.ModelSerializer):
    lesson_images = LessonImageSerializer(many=True, read_only=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "number",
            "duration_minutes",
            "course",
            "content",
            "video_url",
            "lesson_images",
        )


class LessonWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "title", "number", "duration_minutes", "course", "content", "video_url")


class CourseImageSerializer(serializers.ModelSerializer):
    MAX_COUNT_COURSE_IMAGES = env.int("MAX_COUNT_COURSE_IMAGES")

    class Meta:
        model = CourseImage
        fields = (
            "id",
            "course",
            "image",
            "is_main",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def validate(self, data):
        if self.instance:
            course = self.instance.course
        else:
            course = data["course"]
        if self.context["request"].user != course.author:
            raise serializers.ValidationError("Нельзя загрузить фото к чужому ресурсу")
        if course.course_images.count() >= self.MAX_COUNT_COURSE_IMAGES and not self.instance:
            raise serializers.ValidationError("К ресурсу можно загрузить максимум 5 фото")

        return data


class CourseListSerializer(serializers.ModelSerializer):
    avg_rating = serializers.FloatField(read_only=True)
    students_count = serializers.IntegerField(read_only=True)
    image_preview = serializers.SerializerMethodField()

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
            "image_preview",
        )

    def get_image_preview(self, obj):
        course_image = obj.course_images.filter(is_main=True).first()
        if course_image is None:
            return None
        if self.request:
            return self.request.build_absolute_uri(course_image.image)
        return course_image.image.url


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonListSerializer(many=True, read_only=True)
    reviews_preview = serializers.SerializerMethodField()
    reviews_count = serializers.IntegerField(read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    students_count = serializers.IntegerField(read_only=True)
    author = PublicSerializer(read_only=True)
    course_images = CourseImageSerializer(many=True, read_only=True)

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
            "course_images",
        )

    def get_reviews_preview(self, obj):
        qs = obj.reviews.all()[:5]
        return ReviewSerializer(qs, many=True, context=self.context).data


class CourseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "title", "description", "price", "category", "status"]
