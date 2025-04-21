from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Curso,
    Modulo,
    Tema,
    ArchivoAdicional,
    ProgresoCurso,
    ProgresoTema,
)

# 🔹 Archivos adicionales por tema
class ArchivoAdicionalInline(admin.TabularInline):  # Changed to TabularInline
    model = ArchivoAdicional
    extra = 1

# 🔹 Temas dentro de un módulo (con archivos)
class TemaInline(admin.StackedInline):  # Changed to StackedInline
    model = Tema
    extra = 1
    inlines = [ArchivoAdicionalInline]  # Nested inlines are not supported natively
    fields = (
        'orden',
        'titulo',
        'contenido',
        'video_local',
        'video_youtube',
        'imagen',
        'documento',
    )

# 🔹 Módulos dentro del curso (con temas)
class ModuloInline(admin.StackedInline):  # Changed to StackedInline
    model = Modulo
    extra = 1
    inlines = [TemaInline]  # Nested inlines are not supported natively
    fieldsets = (
        (None, {'fields': ('orden', 'titulo')}),
    )

# 🔹 Cursos completos (con módulos)
class CursoAdmin(admin.ModelAdmin):  # Changed to ModelAdmin
    list_display = ('titulo', 'fecha_inicio', 'fecha_fin')
    inlines = [ModuloInline]
    search_fields = ('titulo',)
    list_filter = ('fecha_inicio',)

# 🔹 Admin individual para temas
class TemaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'modulo', 'orden', 'preview_video_youtube')
    list_filter = ('modulo',)
    search_fields = ('titulo',)

    def preview_video_youtube(self, obj):
        if obj.video_youtube:
            return format_html(f"<a href='{obj.video_youtube}' target='_blank'>🔗 Ver</a>")
        return "—"
    preview_video_youtube.short_description = "YouTube"

# 🔹 Registro final
admin.site.register(Curso, CursoAdmin)
admin.site.register(Modulo)
admin.site.register(Tema, TemaAdmin)
admin.site.register(ArchivoAdicional)
admin.site.register(ProgresoCurso)
admin.site.register(ProgresoTema)
