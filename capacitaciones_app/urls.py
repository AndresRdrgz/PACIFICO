from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

from . import views

urlpatterns = [


    # Cursos
    path('cursos/', views.lista_cursos, name='lista_cursos'),
    path('cursos/<int:curso_id>/', views.detalle_curso, name='detalle_curso'),

    # Temas
    path('cursos/<int:curso_id>/tema/<int:tema_id>/', views.ver_tema, name='ver_tema'),
    path('temas/<int:tema_id>/completado/', views.marcar_tema_completado, name='marcar_tema_completado'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
