from django.contrib import admin
from .models import Cotizacion, PeriodoPago, Aseguradora, FormPago, PruebaDario, Cliente, UserProfile, CotizacionDocumento
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserProfileForm  # Importamos el formulario personalizado

# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    form = UserProfileForm  # Conectamos el formulario con validación condicional
    can_delete = False

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class CustomFormset(formset):
            def get_form(self, form_index, **kwargs):
                form = super().get_form(form_index, **kwargs)
                try:
                    if obj and hasattr(obj, 'userprofile') and obj.userprofile.rol == 'Alumno':
                        form.base_fields.pop('oficial', None)
                        form.base_fields.pop('sucursal', None)
                except Exception:
                    pass
                return form

        return CustomFormset


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = (
        'NumeroCotizacion', 'nombreCliente', 'cedulaCliente', 'tipoPrestamo', 'oficial', 'sucursal', 'vendedor', 'vendedorTipo', 'created_at'
    )
    search_fields = (
        'NumeroCotizacion', 'nombreCliente', 'cedulaCliente', 'vendedor',
    )
    list_filter = (
        'tipoPrestamo', 'oficial', 'sucursal', 'vendedorTipo', 'created_at',
    )

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('cedulaCliente', 'nombreCliente', 'fechaNacimiento', 'edad', 'sexo', 'jubilado', 'created_at', 'updated_at', 'added_by', 'propietario')
    search_fields = ('cedulaCliente', 'nombreCliente', 'propietario__username', 'added_by__username')
    list_filter = ('sexo', 'jubilado', 'created_at', 'propietario', 'added_by')

@admin.register(PeriodoPago)
class PeriodoPagoAdmin(admin.ModelAdmin):
    pass

@admin.register(Aseguradora)
class AseguradoraAdmin(admin.ModelAdmin):
    pass

@admin.register(FormPago)
class FormPagoAdmin(admin.ModelAdmin):
    pass

@admin.register(PruebaDario)
class PruebaDarioAdmin(admin.ModelAdmin):
    pass

@admin.register(CotizacionDocumento)
class CotizacionDocumentoAdmin(admin.ModelAdmin):
    pass

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol', 'sucursal', 'oficial', 'auto_save_cotizaciones', 'pruebaFuncionalidades')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'rol', 'sucursal', 'oficial')
    list_filter = ('rol', 'sucursal', 'oficial', 'auto_save_cotizaciones', 'pruebaFuncionalidades')

