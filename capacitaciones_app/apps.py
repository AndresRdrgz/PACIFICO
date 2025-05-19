
from django.apps import AppConfig


class CapacitacionesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'capacitaciones_app'

    def ready(self):
        import capacitaciones_app.signals  # 👈 Importa el archivo signals
