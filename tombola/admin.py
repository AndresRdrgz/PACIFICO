from django.contrib import admin
from .models import Tombola, Boleto, FormularioTombola, CargaMasiva

# Register your models here.
@admin.register(Tombola)
class TombolaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'fecha_evento')
    list_filter = ('fecha_evento',)
    search_fields = ('nombre',)

@admin.register(Boleto)
class BoletoAdmin(admin.ModelAdmin):
    list_display = ('id', 'tombola', 'cliente', 'canalOrigen', 'fecha_creacion')
    list_filter = ('canalOrigen', 'tombola', 'fecha_creacion')
    search_fields = ('cliente__nombreCliente', 'cliente__cedulaCliente')

@admin.register(FormularioTombola)
class FormularioTombolaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'cedulaCliente', 'celular', 'fecha_creacion')
    list_filter = ('sexo', 'sector', 'producto_interesado', 'oficial', 'tombola', 'fecha_creacion')
    search_fields = ('nombre', 'apellido', 'cedulaCliente', 'celular', 'correo_electronico')

@admin.register(CargaMasiva)
class CargaMasivaAdmin(admin.ModelAdmin):
    list_display = ('id', 'archivo', 'cantidad_registros', 'usuario', 'fecha_subida')
    list_filter = ('fecha_subida', 'usuario')
    search_fields = ('usuario',)
    ordering = ('-fecha_subida',)
