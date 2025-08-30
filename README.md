
---

# Django Property Listings with Multi-Level Redis Caching

## Overview

This project is a comprehensive demonstration of a Django-based property listing application that implements multi-level caching strategies using Redis. It is designed to showcase how to build high-performance, scalable web applications by significantly reducing database load through intelligent caching.

The entire development environment is containerized using Docker, providing a clean, reproducible, and production-ready setup with PostgreSQL as the database and Redis as the cache backend. The project serves as a practical blueprint for real-world applications where read-heavy operations need to be optimized, such as e-commerce sites, real estate platforms, or content management systems.

## Key Concepts & Learning Objectives

This project is an excellent resource for learning and implementing the following concepts:

-   **Multi-Level Caching:**
    -   **View-Level Caching:** Caching entire HTTP responses for frequently accessed, static pages using Django's `@cache_page` decorator.
    -   **Low-Level QuerySet Caching:** Granular control over caching by explicitly caching database query results to avoid redundant database hits for complex or expensive queries.
-   **Efficient Cache Invalidation:** Maintaining data consistency by automatically clearing stale cache entries when the underlying data changes (create, update, delete) using Django Signals (`post_save`, `post_delete`).
-   **Containerized Development:** Using `Docker` and `docker-compose` to manage and run isolated services (PostgreSQL, Redis), ensuring a consistent environment from development to production.
-   **Database Optimization:** Demonstrating how caching acts as a crucial layer to absorb traffic and protect the database, leading to faster response times and lower infrastructure costs.
-   **Cache Performance Analysis:** Utilizing logging and the Redis CLI to monitor cache hits, misses, and overall cache effectiveness.
-   **Scalable Django Project Structure:** Organizing a Django project in a clean, maintainable, and scalable way.

## Technology Stack

-   **Backend:** Django
-   **Database:** PostgreSQL
-   **Cache:** Redis
-   **Containerization:** Docker & Docker Compose
-   **Python Libraries:**
    -   `django-redis`: For seamless Redis integration as a Django cache backend.
    -   `psycopg2-binary`: PostgreSQL adapter for Python.

## Project Structure

```
alx-backend-caching_property_listings/
├── alx-backend-caching_property_listings/
│   ├── settings.py         # Project settings, DB and cache configuration
│   ├── urls.py             # Root URL configuration
│   └── ...
├── properties/
│   ├── models.py           # Property data model
│   ├── views.py            # Application logic, caching implementation
│   ├── urls.py             # App-specific URLs
│   ├── signals.py          # Cache invalidation logic
│   ├── apps.py             # App configuration to connect signals
│   └── migrations/
├── manage.py               # Django's command-line utility
├── docker-compose.yml      # Defines and configures Docker services
├── requirements.txt        # Python package dependencies
└── README.md               # You are here
```

## Setup and Installation

Follow these steps to get the project running on your local machine.

### Prerequisites

-   [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
-   [Python 3.8+](https://www.python.org/downloads/)
-   [Git](https://git-scm.com/downloads/)

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd alx-backend-caching_property_listings
```

### 2. Create and Activate a Virtual Environment

It is highly recommended to use a virtual environment to manage project dependencies.

```bash
# For Unix/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```
*(You will need to create a `requirements.txt` file)*
```bash
pip freeze > requirements.txt
```

### 4. Start the Docker Services

This command will build and start the PostgreSQL and Redis containers in the background.

```bash
docker-compose up -d
```

-   **PostgreSQL** will be accessible on `localhost:5432`.
-   **Redis** will be accessible on `localhost:6379`.

### 5. Run Database Migrations

Apply the database schema defined in the models.

```bash
python manage.py makemigrations properties
python manage.py migrate
```

### 6. Create a Superuser (Optional)

To access the Django admin panel, create a superuser.

```bash
python manage.py createsuperuser
```

### 7. Run the Django Development Server

```bash
python manage.py runserver
```

The application will be running at `http://127.0.0.1:8000/`.

## Caching Implementation Details

### 1. View-Level Caching (`@cache_page`)

View-level caching is applied to pages that are frequently accessed and show the same content to all users. The entire rendered page is stored in the cache for a specified duration.

-   **Property List Page:** The main listing page is cached for 15 minutes. The first visit hits the database, but subsequent visits within the timeframe will receive a near-instant response directly from Redis.

    ```python
    # properties/views.py
    from django.views.decorators.cache import cache_page

    @cache_page(60 * 15) # Cache for 15 minutes
    def property_list(request):
        # ... view logic ...
    ```

-   **Property Detail Page:** Each property's detail page is also cached.

### 2. Low-Level QuerySet Caching

For more granular control, we use low-level caching. This is ideal for caching the results of expensive or complex database queries that are used in multiple places. The pattern is simple: **"check the cache first, and if it's a miss, hit the database and then populate the cache."**

-   **Example: Caching a single property query:**

    ```python
    # properties/views.py
    from django.core.cache import cache

    def property_detail(request, property_id):
        cache_key = f'property_{property_id}'
        property_obj = cache.get(cache_key) # 1. Check cache first

        if not property_obj: # 2. Cache miss
            property_obj = get_object_or_404(Property, pk=property_id) # 3. Hit DB
            cache.set(cache_key, property_obj, timeout=60 * 60) # 4. Set cache
            # timeout is in seconds (1 hour)

        return render(request, 'properties/property_detail.html', {'property': property_obj})
    ```

### 3. Cache Invalidation with Django Signals

To prevent stale data, we must invalidate (delete) cache entries when the original data changes. We use Django signals for this.

-   When a `Property` is **saved** (created or updated) or **deleted**, signals are triggered.
-   These signals call a function that precisely deletes the relevant cache keys, such as the property list view cache and the specific property detail cache.

```python
# properties/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Property

@receiver([post_save, post_delete], sender=Property)
def invalidate_property_cache(sender, instance, **kwargs):
    """
    Invalidates cache for a specific property and the property list.
    """
    # Invalidate the detail view cache for the specific property
    cache.delete(f'property_{instance.id}')

    # Invalidate the list view cache
    # Note: This requires a more advanced technique to find the exact key,
    # or clearing all list-related caches.
    cache.delete('property_list_view_cache_key') # Assuming a known key
```

To connect the signals, we import them in the `ready()` method of our app's configuration:

```python
# properties/apps.py
from django.apps import AppConfig

class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'

    def ready(self):
        import properties.signals
```

## How to Monitor Caching

You can verify that caching is working in several ways:

1.  **Check Django Server Logs:** Add `print()` or `logging` statements in your views to indicate a "CACHE HIT" or "CACHE MISS." You will notice that database queries are only logged on a cache miss.

2.  **Use the Redis CLI:** Connect to the Redis container and inspect the keys.

    ```bash
    # Get the ID of your Redis container
    docker ps

    # Connect to the container
    docker exec -it <redis_container_id_or_name> redis-cli

    # Inside Redis CLI
    > KEYS *          # List all keys in the cache
    > GET <key_name>  # Get the value of a specific key
    > TTL <key_name>  # Check the remaining time-to-live for a key
    > FLUSHDB         # Clear the current database
    ```

3.  **Use Django Shell:** Monitor the number of database queries executed per request using `django.db.connection.queries`. The query count should drop to zero on subsequent visits to a cached page.