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
    Connects to Redis, retrieves keyspace statistics, calculates the
    hit ratio, and logs the metrics.

    Returns:
        A dictionary containing cache metrics (hits, misses, hit_ratio).
    """
    try:
        # 1. Get a raw Redis connection
        # "default" is the alias of the cache in settings.py
        conn = get_redis_connection("default")

        # 2. Get keyspace statistics from Redis INFO command
        info = conn.info('keyspace')
        
        # The key for our cache DB is 'db1' because we used /1 in settings.py
        # If you used /0 or nothing, it would be 'db0'
        cache_db_info = info.get('db1')

        if not cache_db_info:
            logger.warning("No cache metrics found for db1. The database might be empty or unused.")
            return {"hits": 0, "misses": 0, "hit_ratio": 0.0}

        hits = cache_db_info.get('keyspace_hits', 0)
        misses = cache_db_info.get('keyspace_misses', 0)
        total_lookups = hits + misses

        # 3. Calculate hit ratio, avoiding division by zero
        if total_lookups > 0:
            hit_ratio = (hits / total_lookups) * 100
        else:
            hit_ratio = 0.0

        # 4. Log the metrics for analysis
        logger.info("--- REDIS CACHE METRICS ---")
        logger.info(f"  Total Lookups: {total_lookups}")
        logger.info(f"  Cache Hits:    {hits}")
        logger.info(f"  Cache Misses:  {misses}")
        logger.info(f"  Hit Ratio:     {hit_ratio:.2f}%")
        logger.info("---------------------------")

        metrics = {
            "hits": hits,
            "misses": misses,
            "hit_ratio": f"{hit_ratio:.2f}%"
        }
        return metrics

    except Exception as e:
        logger.error(f"Could not connect to Redis or get metrics: {e}")
        return None