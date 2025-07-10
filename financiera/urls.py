from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from pacifico.ViewsLogin import (
    LoginView, LogoutView, custom_password_reset_view, CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView, login_view
)

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
    path('workflow/', include('workflow.urls', namespace='workflow')),  # Include the workflow app's URLs with namespace
    path('mantenimiento/', include('mantenimiento.urls')),  # Include the mantenimiento app's URLs
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
