from django.contrib import admin
from .models import ClienteEntrevista, ReferenciaPersonal, ReferenciaComercial, OtroIngreso

@admin.register(ClienteEntrevista)
class ClienteEntrevistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'primer_nombre', 'primer_apellido', 'email', 'telefono', 'tipo_producto', 'fecha_entrevista')
    list_display_links = ('id', 'primer_nombre', 'primer_apellido')
    search_fields = ('primer_nombre', 'primer_apellido', 'email', 'telefono')
    list_filter = ('tipo_producto', 'oficial', 'fecha_entrevista')
    list_per_page = 25


@admin.register(ReferenciaPersonal)
class ReferenciaPersonalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'relacion', 'direccion', 'entrevista')
    list_display_links = ('nombre',)
    search_fields = ('nombre', 'telefono', 'relacion')
    list_per_page = 25


@admin.register(ReferenciaComercial)
class ReferenciaComercialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'actividad', 'telefono', 'entrevista')
    list_display_links = ('nombre',)
    search_fields = ('nombre', 'tipo', 'actividad', 'telefono')
    list_per_page = 25


@admin.register(OtroIngreso)
class OtroIngresoAdmin(admin.ModelAdmin):
    list_display = ('fuente', 'monto', 'cliente')
    list_display_links = ('fuente',)
    search_fields = ('fuente',)
    list_per_page = 25
