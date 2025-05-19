from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pacifico.urls')),           # Rutas de la app pacifico
    path('', include('tombola.urls')),            # Rutas de la app tombola
    path('', include('capacitaciones_app.urls')), # Rutas de capacitaciones_app
    path('accounts/', include('django.contrib.auth.urls')),  # Autenticación por defecto
]
