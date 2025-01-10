from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Cotizacion, PeriodoPago, Aseguradora, FormPago, PruebaDario, Cliente, UserProfile
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Cotizacion)
class CotizacionAdmin(ModelAdmin):
    pass

@admin.register(Cliente)
class ClienteAdmin(ModelAdmin):
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