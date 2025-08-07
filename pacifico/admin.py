from django.contrib import admin
from .models import Cotizacion, PeriodoPago, Aseguradora, FormPago, PruebaDario, Cliente, UserProfile, CotizacionDocumento, DebidaDiligencia, GroupProfile, Sucursal
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from .models import Politicas
from .forms import UserProfileForm  # Importamos el formulario personalizado

# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    form = UserProfileForm  # Conectamos el formulario con validación condicional
    can_delete = False
    fields = ('rol', 'oficial', 'sucursal', 'profile_picture', 'auto_save_cotizaciones', 'pruebaFuncionalidades', 'numeroColaborador')  # Añadimos 'rol' y 'numeroColaborador' explícitamente

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)

        class CustomFormset(formset):
            def get_form(self, form_index, **kwargs):
                form = super().get_form(form_index, **kwargs)
                try:
                    if obj and hasattr(obj, 'userprofile') and obj.userprofile.rol == 'Usuario':
                        form.base_fields.pop('oficial', None)
                        form.base_fields.pop('sucursal', None)
                except Exception:
                    pass
                return form

        return CustomFormset


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_filter = BaseUserAdmin.list_filter + ('email',)  # Add email filter

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

@admin.register(DebidaDiligencia)
class DebidaDiligenciaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'estado', 'fecha_solicitud', 'solicitado_por', 'fecha_completado', 'archivos_completos')
    list_filter = ('estado', 'fecha_solicitud', 'fecha_completado')
    search_fields = ('cliente__nombreCliente', 'cliente__cedulaCliente', 'solicitado_por__username')
    readonly_fields = ('created_at', 'updated_at', 'archivos_completos')
    
    fieldsets = (
        ('Información del Cliente', {
            'fields': ('cliente', 'estado')
        }),
        ('Solicitud', {
            'fields': ('solicitado_por', 'fecha_solicitud')
        }),
        ('Archivos', {
            'fields': ('busqueda_google', 'busqueda_registro_publico', 'comentarios')
        }),
        ('Completado', {
            'fields': ('completado_por', 'fecha_completado')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at', 'archivos_completos'),
            'classes': ('collapse',)
        })
    )
 

@admin.register(Politicas)
class PoliticasAdmin(admin.ModelAdmin):
    list_display = ('titulo',)
    search_fields = ('titulo',)
    list_filter = ('titulo',)


@admin.register(Sucursal)
class SucursalAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'telefono', 'activa', 'fecha_creacion')
    list_filter = ('activa', 'fecha_creacion')
    search_fields = ('codigo', 'nombre', 'direccion')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'activa')
        }),
        ('Información de Contacto', {
            'fields': ('direccion', 'telefono', 'email'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        })
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si estamos editando
            return self.readonly_fields + ('codigo',)  # No permitir cambiar el código
        return self.readonly_fields


# Configuración para GroupProfile
class GroupProfileInline(admin.StackedInline):
    model = GroupProfile
    can_delete = False
    fields = ('es_sucursal', 'sucursal_codigo', 'descripcion', 'activo')
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        class CustomGroupProfileFormset(formset):
            def get_form(self, form_index, **kwargs):
                form = super().get_form(form_index, **kwargs)
                # Agregar JavaScript para mostrar/ocultar sucursal_codigo
                form.Media.js = form.Media.js + ('admin/js/group_profile.js',)
                return form
        
        return CustomGroupProfileFormset


class GroupAdmin(BaseGroupAdmin):
    inlines = [GroupProfileInline]
    
    def get_inline_instances(self, request, obj=None):
        if obj:  # Solo mostrar inline si el grupo ya existe
            return super().get_inline_instances(request, obj)
        return []


@admin.register(GroupProfile)
class GroupProfileAdmin(admin.ModelAdmin):
    list_display = ('group', 'es_sucursal', 'get_sucursal_display', 'activo', 'fecha_creacion')
    list_filter = ('es_sucursal', 'activo', 'sucursal_codigo')
    search_fields = ('group__name', 'descripcion')
    readonly_fields = ('fecha_creacion', 'fecha_modificacion')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('group', 'descripcion', 'activo')
        }),
        ('Configuración de Sucursal', {
            'fields': ('es_sucursal', 'sucursal_codigo'),
            'description': 'Marque "Es sucursal" si este grupo representa una sucursal específica'
        }),
        ('Metadatos', {
            'fields': ('fecha_creacion', 'fecha_modificacion'),
            'classes': ('collapse',)
        })
    )
    
    def get_sucursal_display(self, obj):
        if obj.es_sucursal and obj.sucursal_codigo:
            return dict(obj._meta.get_field('sucursal_codigo').choices).get(obj.sucursal_codigo, obj.sucursal_codigo)
        return "-"
    get_sucursal_display.short_description = 'Sucursal'


# Re-registrar Group con el nuevo admin
admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)
