from django.contrib import admin
from .models import Proyecto, Modulo, Prueba, ProyectoUsuario

class ModuloInline(admin.TabularInline):
    model = Modulo
    extra = 1

class ProyectoUsuarioInline(admin.TabularInline):
    model = ProyectoUsuario
    extra = 1

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'estado', 'creado_por', 'fecha_creacion', 'total_pruebas']
    list_filter = ['estado', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    inlines = [ModuloInline, ProyectoUsuarioInline]
    
    def total_pruebas(self, obj):
        return obj.total_pruebas
    total_pruebas.short_description = 'Total Pruebas'

@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'proyecto', 'fecha_creacion']
    list_filter = ['proyecto', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']

@admin.register(Prueba)
class PruebaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'proyecto', 'modulo', 'prioridad', 'resultado', 'tester', 'fecha_creacion']
    list_filter = ['proyecto', 'modulo', 'prioridad', 'resultado', 'fecha_creacion']
    search_fields = ['titulo', 'descripcion']
    readonly_fields = ['fecha_creacion', 'fecha_ejecucion', 'fecha_resolucion']

@admin.register(ProyectoUsuario)
class ProyectoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'proyecto', 'rol', 'activo', 'fecha_invitacion']
    list_filter = ['proyecto', 'rol', 'activo', 'fecha_invitacion']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'proyecto__nombre']
