import django_filters

from course.models import Course


class CourseFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category_id = django_filters.NumberFilter(field_name="category__id")
    author_id = django_filters.NumberFilter(field_name="author__id")

    class Meta:
        model = Course
        fields = ["price_min", "price_max", "category_id", "author_id"]
