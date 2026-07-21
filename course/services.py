from django.core.cache import cache
from django.db.models import F

from course.models import Course


def register_view(course_id, user_id):
    if not course_id or not user_id:
        return
    key = f"view:{course_id}:{user_id}"
    if cache.get(key) is not None:
        return
    cache.set(key, course_id, 60*60*24*7)
    course = Course.objects.get(id=course_id)
    course.update(views=F('views') + 1)
    course.save(update_fields=['views'])