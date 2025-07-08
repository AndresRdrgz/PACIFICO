from django.urls import path, include
from . import views
from . import api
from .urls_workflow import urlpatterns as workflow_urlpatterns


urlpatterns = [
    # URLs existentes del formulario de entrevista
    path('entrevista/', views.entrevista_cliente_view, name='entrevista_cliente'),
    path('gracias/', views.gracias, name='formulario_gracias'),
    path('entrevistas/', views.lista_entrevistas, name='lista_entrevistas'),
    path('descargar-entrevistas-excel/', views.descargar_entrevistas_excel, name='descargar_entrevistas_excel'),
    path('entrevistas/descargar/<int:entrevista_id>/', views.descargar_entrevista_excel, name='descargar_entrevista_excel'),
    path('entrevistas/json/', api.entrevistas_json, name='entrevistas_json'),
    
    # URLs del sistema de workflow (importadas directamente)
] + [path(f'workflow/{url.pattern}', url.callback, name=f'workflow:{url.name}') for url in workflow_urlpatterns]
