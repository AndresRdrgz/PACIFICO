from django.urls import path
from . import views

urlpatterns = [
    path('entrevista/', views.entrevista_cliente, name='entrevista_cliente'),
    path('entrevistas/', views.lista_entrevistas, name='lista_entrevistas'),
    path('api/entrevistas/', __import__('workflow.api').api.entrevistas_json, name='api_entrevistas'),
]
