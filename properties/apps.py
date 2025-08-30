from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'

    def ready(self):
        """
        This method is called when the app is ready.
        We import our signals module here to ensure the signal
        handlers are connected when Django starts.
        """
        import properties.signals
