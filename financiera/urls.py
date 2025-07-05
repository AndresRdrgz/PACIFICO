from django.contrib import admin
from django.urls import path, include
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
    path('', include('workflow.urls')),  # Include the workflow app's URLs
    path('', include('workflow.urls_workflow')),  # Include the custom admin URLs for workflow
    path('mantenimiento/', include('mantenimiento.urls')),  # Include the mantenimiento app's URLs
]
