from django.contrib import admin
from .models import ClienteEntrevista, ReferenciaPersonal, ReferenciaComercial, OtroIngreso

@admin.register(ClienteEntrevista)
class ClienteEntrevistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'primer_nombre', 'primer_apellido', 'email', 'telefono', 'tipo_producto', 'fecha_entrevista')
    search_fields = ('primer_nombre', 'primer_apellido', 'email', 'telefono')
    list_filter = ('tipo_producto', 'oficial', 'fecha_entrevista')


@admin.register(ReferenciaPersonal)
class ReferenciaPersonalAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'relacion', 'direccion', 'entrevista')
    search_fields = ('nombre', 'telefono', 'relacion')


@admin.register(ReferenciaComercial)
class ReferenciaComercialAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'actividad', 'telefono', 'entrevista')
    search_fields = ('nombre', 'tipo', 'actividad', 'telefono')


@admin.register(OtroIngreso)
class OtroIngresoAdmin(admin.ModelAdmin):
    list_display = ('fuente', 'monto', 'cliente')
    search_fields = ('fuente',)
