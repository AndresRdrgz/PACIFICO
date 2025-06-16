from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from capacitaciones_app.views import (
    lista_cursos,
    detalle_curso,
    ver_tema,
    marcar_tema_completado,
    quiz_modulo,
    certificado,
    asignacion_admin,
    asignar_curso_ajax,
    cursos_asignados_ajax,
    desasignar_curso_ajax,
    exportar_asignaciones_excel,
)

from .views_asignacion import historial_asignaciones_ajax
from capacitaciones_app.views_asignacion import historial_usuario
from . import views

urlpatterns = [
    # 🔐 Admin & Auth
    # path('nested_admin/', include('nested_admin.urls')),

    # 📚 Courses
    path('cursos/', lista_cursos, name='lista_cursos'),
    path('cursos/<int:curso_id>/', detalle_curso, name='detalle_curso'),

    # 📖 Topics
    path('cursos/<int:curso_id>/tema/<int:tema_id>/', ver_tema, name='ver_tema'),
    path('temas/<int:tema_id>/completado/', marcar_tema_completado, name='marcar_tema_completado'),

    # 📝 Quiz by module
    path('cursos/<int:curso_id>/modulo/<int:modulo_id>/quiz/', quiz_modulo, name='quiz_modulo'),

    # 🎓 Certificate
    path('cursos/<int:curso_id>/certificado/', certificado, name='certificado'),

    # 👨‍💼 Admin Asignación
    path('capacitaciones/asignacion/', asignacion_admin, name='asignacion_admin'),

    path('asignar-curso/', asignar_curso_ajax, name='asignar_curso_ajax'),
    path('cursos-asignados/<int:usuario_id>/', cursos_asignados_ajax, name='cursos_asignados_ajax'),
    path('desasignar-curso/', desasignar_curso_ajax, name='desasignar_curso_ajax'),
    path('exportar-asignaciones-excel/', exportar_asignaciones_excel, name='exportar_asignaciones_excel'),
    path('capacitaciones/historial_asignaciones_ajax/', historial_asignaciones_ajax, name='historial_asignaciones_ajax'),
    path('mi-progreso/', historial_usuario, name='mi_progreso'),

    # AJAX Group Views
    path('ajax/usuarios-grupo/<int:grupo_id>/', views.usuarios_grupo_ajax, name='usuarios_grupo_ajax'),
    path('ajax/quitar-usuario-grupo/', views.quitar_usuario_grupo_ajax, name='quitar_usuario_grupo_ajax'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
