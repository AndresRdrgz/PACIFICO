from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Celulares, Tombola, Boleto, FormularioTombola

# Register your models here.

@admin.register(Celulares)
class CelularesAdmin(ModelAdmin):
    pass

@admin.register(Tombola)
class TombolaAdmin(ModelAdmin):
    pass

@admin.register(Boleto)
class BoletoAdmin(ModelAdmin):
    pass

@admin.register(FormularioTombola)
class FormularioTombolaAdmin(ModelAdmin):
    pass
