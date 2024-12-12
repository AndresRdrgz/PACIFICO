from django.contrib import admin
from .models import Cotizacion, PeriodoPago, Aseguradora, FormPago, PruebaDario

# Register your models here.
admin.site.register(Cotizacion)
admin.site.register(PeriodoPago)
admin.site.register(Aseguradora)
admin.site.register(FormPago)
admin.site.register(PruebaDario)
