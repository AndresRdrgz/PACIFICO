from django.contrib import admin
from django.utils.html import format_html
import nested_admin

from .models import (
    Curso,
    Modulo,
    Tema,
    ArchivoAdicional,
    ProgresoCurso,
    ProgresoTema,
    Quiz,
    Pregunta,
    Opcion,
    ResultadoQuiz,
    GrupoAsignacion,
    PerfilUsuario,
)

# 🔹 Opciones dentro de una pregunta
class OpcionInline(nested_admin.NestedTabularInline):
    model = Opcion
    extra = 2

# 🔹 Preguntas dentro de un quiz
class PreguntaInline(nested_admin.NestedStackedInline):
    model = Pregunta
    extra = 1
    fields = ['texto', 'puntaje', 'archivo']
    inlines = [OpcionInline]

# 🔹 Quiz dentro del módulo
class QuizInline(nested_admin.NestedStackedInline):
    model = Quiz
    extra = 0
    inlines = [PreguntaInline]
    fieldsets = (
        (None, {'fields': ('titulo', 'instrucciones', 'portada')}),
    )

# 🔹 Archivos adicionales por tema
class ArchivoAdicionalInline(nested_admin.NestedTabularInline):
    model = ArchivoAdicional
    extra = 1

# 🔹 Temas dentro de un módulo
class TemaInline(nested_admin.NestedStackedInline):
    model = Tema
    extra = 1
    inlines = [ArchivoAdicionalInline]
    fields = (
        'orden',
        'titulo',
        'contenido',
        'video_local',
        'video_youtube',
        'video_externo',
        'imagen',
        'documento',
    )

# 🔹 Módulos dentro del curso
class ModuloInline(nested_admin.NestedStackedInline):
    model = Modulo
    extra = 1
    inlines = [TemaInline, QuizInline]
    fieldsets = (
        (None, {'fields': ('orden', 'titulo')}),
    )

# 🔹 Cursos completos
class CursoAdmin(nested_admin.NestedModelAdmin):
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin')
    inlines = [ModuloInline]
    search_fields = ('titulo',)
    list_filter = ('fecha_inicio',)
    filter_horizontal = ('usuarios_asignados', 'grupos_asignados')  # ✅ Si quieres ver grupos también
    fields = ('titulo', 'descripcion', 'fecha_inicio', 'fecha_fin', 'portada', 'usuarios_asignados', 'grupos_asignados')

# 🔹 Grupos de asignación (corregido)
@admin.register(GrupoAsignacion)
class GrupoAsignacionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    filter_horizontal = ('usuarios_asignados',)  # ✅ CORREGIDO: sin cursos

# 🔹 Temas individuales
class TemaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'modulo', 'orden', 'preview_video_youtube')
    list_filter = ('modulo',)
    search_fields = ('titulo',)
    fields = (
        'modulo',
        'orden',
        'titulo',
        'contenido',
        'video_local',
        'video_youtube',
        'video_externo',
        'imagen',
        'documento',
    )

    def preview_video_youtube(self, obj):
        if obj.video_youtube:
            return format_html(f"<a href='{obj.video_youtube}' target='_blank'>🔗 Ver</a>")
        return "—"
    preview_video_youtube.short_description = "YouTube"

# 🔹 Resultados del quiz
class ResultadoQuizAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'quiz', 'puntaje', 'aprobado', 'fecha_realizacion')
    list_filter = ('aprobado',)
    search_fields = ('usuario__username',)

# 🔹 Registro final
admin.site.register(Curso, CursoAdmin)
admin.site.register(Modulo)
admin.site.register(Tema, TemaAdmin)
admin.site.register(ArchivoAdicional)
admin.site.register(ProgresoCurso)
admin.site.register(ProgresoTema)
admin.site.register(Quiz)
admin.site.register(ResultadoQuiz, ResultadoQuizAdmin)

# 🔹 Registro del perfil de usuario
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo')
    search_fields = ('user__username', 'tipo')
