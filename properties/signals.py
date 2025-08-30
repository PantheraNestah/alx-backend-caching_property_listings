# properties/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property
import logging

logger = logging.getLogger(__name__)

@receiver([post_save, post_delete], sender=Property)
def invalidate_all_properties_cache(sender, instance, **kwargs):
    """
    Invalidates (deletes) the 'all_properties' cache key whenever a
    Property object is created, updated, or deleted.
    """
    cache_key = 'all_properties'
    
    if cache.has_key(cache_key):
        cache.delete(cache_key)
        logger.info(f"CACHE INVALIDATED: Deleted '{cache_key}' from Redis due to model change.")