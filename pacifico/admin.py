from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Cotizacion, PeriodoPago, Aseguradora, FormPago, PruebaDario

# Register your models here.
@admin.register(Cotizacion)
class CotizacionAdmin(ModelAdmin):
    pass

@admin.register(PeriodoPago)
class PeriodoPagoAdmin(ModelAdmin):
    pass

@admin.register(Aseguradora)
class AseguradoraAdmin(ModelAdmin):
    pass

@admin.register(FormPago)
class FormPagoAdmin(ModelAdmin):
    pass

@admin.register(PruebaDario)
class PruebaDarioAdmin(ModelAdmin):
    pass