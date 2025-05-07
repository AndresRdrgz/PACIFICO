from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

from capacitaciones_app.views import (
    lista_cursos,
    detalle_curso,
    ver_tema,
    marcar_tema_completado,
    quiz_modulo,
    certificado,
)

urlpatterns = [
    # 🔁 Redirect home
    path('', lambda request: redirect('lista_cursos'), name='home'),

    # 🔐 Admin & Auth
    path('admin/', admin.site.urls),
    path('nested_admin/', include('nested_admin.urls')),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='capacitaciones_app/login.html'),
        name='login'
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(next_page='login'),
        name='logout'
    ),

    # 📚 Courses
    path('cursos/', lista_cursos, name='lista_cursos'),
    path('cursos/<int:curso_id>/', detalle_curso, name='detalle_curso'),

    # 📖 Topics
    path(
        'cursos/<int:curso_id>/tema/<int:tema_id>/',
        ver_tema,
        name='ver_tema'
    ),
    path(
        'temas/<int:tema_id>/completado/',
        marcar_tema_completado,
        name='marcar_tema_completado'
    ),

    # 📝 Quiz by module
    path(
        'cursos/<int:curso_id>/modulo/<int:modulo_id>/quiz/',
        quiz_modulo,
        name='quiz_modulo'
    ),

    # 🎓 Certificate
    path(
        'cursos/<int:curso_id>/certificado/',
        certificado,
        name='certificado'
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
