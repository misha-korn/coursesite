from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Category, Course


@receiver([post_save, post_delete], sender=Category, dispatch_uid='clear_category_list_cache')
def clear_category_list_cache(sender, **kwargs):
    cache.delete('category_list')

@receiver([post_save, post_delete], sender=Course, dispatch_uid='clear_course_list_cache')
def clear_course_list_cache(sender, **kwargs):
    cache.delete('course_list')