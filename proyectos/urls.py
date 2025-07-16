from django.urls import path
from . import views

app_name = 'proyectos'

urlpatterns = [
    # Dashboard and main views
    path('', views.dashboard, name='dashboard'),
    path('proyectos/', views.proyecto_list, name='proyecto_list'),
    path('proyecto/nuevo/', views.proyecto_create, name='proyecto_create'),
    path('proyecto/<int:proyecto_id>/', views.proyecto_detail, name='proyecto_detail'),
    
    # Test case views
    path('prueba/<int:prueba_id>/', views.prueba_detail, name='prueba_detail'),
    path('prueba/<int:prueba_id>/editar/', views.prueba_edit, name='prueba_edit'),
    path('proyecto/<int:proyecto_id>/prueba/nueva/', views.prueba_create, name='prueba_create'),
    
    # Project management (admin only)
    path('proyecto/<int:proyecto_id>/invitar-usuario/', views.invitar_usuario, name='invitar_usuario'),
    path('proyecto/<int:proyecto_id>/crear-modulo/', views.crear_modulo, name='crear_modulo'),
    
    # API endpoints
    path('api/proyecto/<int:proyecto_id>/stats/', views.api_proyecto_stats, name='api_proyecto_stats'),
    path('api/prueba/<int:prueba_id>/update-result/', views.api_update_result, name='api_update_result'),
    path('api/prueba/<int:prueba_id>/mark-resolved/', views.api_mark_resolved, name='api_mark_resolved'),
    path('api/archivo/<int:archivo_id>/eliminar/', views.api_eliminar_archivo, name='api_eliminar_archivo'),
    
    # Export endpoints
    path('proyecto/<int:proyecto_id>/export-excel/', views.export_pruebas_excel, name='export_pruebas_excel'),
] 