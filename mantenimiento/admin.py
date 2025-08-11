from django.contrib import admin
from .models import Patrono, Promocion, TargetPromocion, Agencias

@admin.register(Patrono)
class PatronoAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Patrono._meta.fields]
    search_fields = ['codigo', 'descripcion', 'agrupador']
    list_filter = ['selectDescuento', 'disketCentral', 'agrupador']


class TargetPromocionInline(admin.TabularInline):
    model = TargetPromocion
    extra = 1  # Number of empty forms to display


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Promocion._meta.fields]
    search_fields = ['descripcion', 'producto', 'incentivo']
    list_filter = ['activa', 'producto', 'dirigido_a']
    date_hierarchy = 'fecha_inicio'
    ordering = ['-fecha_inicio']
    list_per_page = 20
    actions = ['activate_promotions', 'deactivate_promotions']
    list_editable = ['activa']
    list_display_links = ['descripcion']
    inlines = [TargetPromocionInline]

@admin.register(Agencias)
class AgenciasAdmin(admin.ModelAdmin):
    list_display = ['secuencia', 'razon_social']
    search_fields = ['secuencia', 'razon_social']
    ordering = ['secuencia']
    list_per_page = 20
