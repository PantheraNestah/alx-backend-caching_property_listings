# properties/management/commands/get_cache_metrics.py

from django.core.management.base import BaseCommand
from properties.utils import get_redis_cache_metrics

class Command(BaseCommand):
    help = 'Retrieves and displays Redis cache hit/miss metrics.'

    def handle(self, *args, **options):
        self.stdout.write("Fetching Redis cache metrics...")
        metrics = get_redis_cache_metrics()
        
        if metrics:
            self.stdout.write(self.style.SUCCESS('--- Cache Performance Report ---'))
            self.stdout.write(f"  Cache Hits:    {metrics['hits']}")
            self.stdout.write(f"  Cache Misses:  {metrics['misses']}")
            self.stdout.write(f"  Hit Ratio:     {metrics['hit_ratio']}")
            self.stdout.write(self.style.SUCCESS('------------------------------'))
        else:
            self.stdout.write(self.style.ERROR('Failed to retrieve cache metrics. Check Redis connection and logs.'))