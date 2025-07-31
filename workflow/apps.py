from django.apps import AppConfig


class WorkflowConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'workflow'
    
    def ready(self):
        """
        Importar signals cuando la aplicación esté lista
        """
        try:
            import workflow.signals_backoffice
        except ImportError:
            pass