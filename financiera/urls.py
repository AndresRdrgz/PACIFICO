from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from pacifico.ViewsLogin import (
    LoginView, LogoutView, custom_password_reset_view, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, login_view
)

# Import test views for error page testing (only in DEBUG mode)
if settings.DEBUG:
    from financiera.test_views import test_error_pages

urlpatterns = [
    # Custom authentication URLs with custom templates
    path('login/', login_view, name='login'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('passwordReset/', custom_password_reset_view, name='password_reset'),
    path('passwordReset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('passwordReset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('passwordReset/complete/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('admin/', admin.site.urls),
    path('', include('pacifico.urls')),  # Include the pacifico app's URLs
    path('', include('tombola.urls')),  # Include the tombola app's URLs
    path('', include('capacitaciones_app.urls')),  # Include the capacitaciones_app app's URLs
    path('', include('workflow.urls')),  # Include the workflow interview URLs (no prefix)
    path('workflow/', include('workflow.urls_workflow', namespace='workflow')),  # Include the workflow app's URLs with namespace
    path('mantenimiento/', include('mantenimiento.urls')),  # Include the mantenimiento app's URLs
    path('proyectos/', include('proyectos.urls', namespace='proyectos')),  # Include the proyectos app's URLs
]

# Add test URL for error pages (only in DEBUG mode)
if settings.DEBUG:
    urlpatterns += [
        path('test-errors/', test_error_pages, name='test_error_pages'),
    ]

# Serve static and media files
# In development, Django serves these automatically
# In production, we need to explicitly configure media file serving
if settings.DEBUG:
    # Development: serve both static and media files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production: only serve media files (static files should be served by web server)
    # Static files in production should be served by nginx/apache, not Django
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'financiera.views.custom_404_view'
handler500 = 'financiera.views.custom_500_view'
