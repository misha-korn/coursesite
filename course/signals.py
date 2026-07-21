from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from enrollment.models import Enrollment
from review.models import Review

from .models import Category, Course


@receiver([post_save, post_delete], sender=Category, dispatch_uid="clear_category_list_cache")
def clear_category_list_cache(sender, **kwargs):
    cache.delete("category_list")


@receiver([post_save, post_delete], sender=Course, dispatch_uid="clear_course_list_cache")
def clear_course_list_cache(sender, **kwargs):
    cache.delete("course_list")


@receiver([post_save, post_delete], sender=Review, dispatch_uid="clear_course_list_cache_on_review")
def clear_on_review(sender, **kwargs):
    cache.delete("course_list")


@receiver(
    [post_save, post_delete],
    sender=Enrollment,
    dispatch_uid="clear_course_list_cache_on_enrollment",
)
def clear_on_enrollment(sender, **kwargs):
    cache.delete("course_list")
