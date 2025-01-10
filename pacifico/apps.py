from django.apps import AppConfig


class PacificoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pacifico"

    def ready(self):
        import pacifico.signals  # Ensure the signals are imported