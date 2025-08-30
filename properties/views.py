from django.shortcuts import render
from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from .models import Property
import logging
from .utils import get_all_properties

# Create your views here.

# Set up a logger to see cache hits/misses
logger = logging.getLogger(__name__)

@cache_page(60 * 15)  # Cache this view for 15 minutes
def property_list(request):
    """
    This view retrieves all properties from the database.
    The first time it's accessed, it hits the DB and its response is cached.
    Subsequent requests within 15 minutes will receive the cached response.
    """
    #properties = Property.objects.all()
    properties = get_all_properties()
    
    # This log will only appear on a "cache miss"
    logger.warning("DATABASE HIT: The property_list view was executed.")
    
    context = {
        'properties': properties
    }

    # Serialize the QuerySet into a list of dictionaries
    data = {
        "properties": list(properties.values(
            "id", "title", "description", "price", "location", "created_at"
        ))
    }

    #return render(request, 'properties/property_list.html', context)
    return JsonResponse({
        "properties": list(properties.values(
            "id", "title", "description", "price", "location", "created_at"
        ))
    })
