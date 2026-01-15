from django.apps import AppConfig


class FantasyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fantasy'
    
    def ready(self):
        """
        Importa las señales cuando la app está lista.
        Esto asegura que las señales se registren correctamente.
        """
        try:
            import fantasy.signals  # noqa: F401
        except ImportError:
            pass