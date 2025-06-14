from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pacifico.urls')),  # Include the pacifico app's URLs
    path('', include('tombola.urls')),  # Include the tombola app's URLs
    path('', include('capacitaciones_app.urls')),  # Include the capacitaciones_app app's URLs
    path('', include('workflow.urls')),  # Include the workflow app's URLs
    path('mantenimiento/', include('mantenimiento.urls')),  # Include the mantenimiento app's URLs
    path('accounts/', include('django.contrib.auth.urls')),  # Include the default authentication URLs
]
