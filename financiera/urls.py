from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from pacifico.ViewsLogin import (
    LoginView, LogoutView, custom_password_reset_view, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, login_view
)
from financiera.views import SecureMediaView

# Import test views for error page testing (only in DEBUG mode)
test_error_pages = None
if settings.DEBUG:
    try:
        from financiera.test_views import test_error_pages
    except ImportError:
        pass

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
if settings.DEBUG and test_error_pages is not None:
    urlpatterns += [
        path('test-errors/', test_error_pages, name='test_error_pages'),
    ]

# Serve static and media files
# Always serve media files (both debug and production)
# Static files in production should be served by nginx/apache, not Django
if settings.DEBUG:
    # Development: serve static files through Django
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Always serve media files through Django (both debug and production)
# You can choose between the standard static serving or the secure view
if settings.DEBUG:
    # Use standard static serving in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Use secure media view in production
    urlpatterns += [
        path('media/<path:path>', SecureMediaView.as_view(), name='secure_media'),
    ]

# Custom error handlers
handler404 = 'financiera.views.custom_404_view'
handler500 = 'financiera.views.custom_500_view'
