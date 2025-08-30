from django.core.cache import cache
from .models import Property
import logging

# Configure logger
logger = logging.getLogger(__name__)

def get_all_properties():
    """
    Retrieves all properties, utilizing low-level caching.
    
    - Tries to fetch the queryset from Redis cache first.
    - If it's a cache miss, it queries the database and sets the cache
      for future requests.
    
    Returns: A Django QuerySet of all Property objects.
    """
    cache_key = 'all_properties'
    
    # 1. Check Redis for the cached queryset
    properties = cache.get(cache_key)
    
    # 2. If not found (cache miss)
    if properties is None:
        logger.info(f"--- CACHE MISS for key: '{cache_key}'. Querying database. ---")
        # 3. Fetch from the database
        properties = Property.objects.all()
        # 4. Store the queryset in Redis cache for 1 hour (3600 seconds)
        cache.set(cache_key, properties, 3600)
    else:
        logger.info(f"--- CACHE HIT for key: '{cache_key}'. Serving from Redis. ---")
        
    return properties