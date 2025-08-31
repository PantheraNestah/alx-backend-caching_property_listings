from django.core.cache import cache
from .models import Property
import logging

from django_redis import get_redis_connection

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

def get_redis_cache_metrics():
    """
    Retrieve Redis cache hit/miss statistics and compute hit ratio.
    """
    try:
        conn = get_redis_connection("default")
        info = conn.info("stats")

        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total_requests = hits + misses

        hit_ratio = hits / total_requests if total_requests > 0 else 0

        metrics = {
            "hits": hits,
            "misses": misses,
            "hit_ratio": round(hit_ratio, 2),
        }

        logger.info("Redis Cache Metrics: %s", metrics)
        return metrics

    except Exception as e:
        logger.error("Failed to fetch Redis metrics: %s", str(e))
        return {"error": str(e)}