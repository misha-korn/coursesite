from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Category


@receiver([post_save, post_delete], sender=Category, dispatch_uid="clear_category_list_cache")
def clear_category_list_cache(sender, **kwargs):
    cache.delete("category_list")
