from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Sala, Reserva, Participante, Notificacion


@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Sala.
    
    Permite a los administradores gestionar las salas de trabajo,
    incluyendo su información básica, estado y equipamiento.
    """
    
    list_display = [
        'nombre', 
        'ubicacion', 
        'capacidad', 
        'estado', 
        'mostrar_foto',
        'created_at'
    ]
    list_filter = ['estado', 'capacidad', 'created_at']
    search_fields = ['nombre', 'ubicacion', 'descripcion']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'ubicacion', 'capacidad', 'estado')
        }),
        ('Descripción y Equipamiento', {
            'fields': ('descripcion', 'equipamiento'),
            'classes': ('collapse',)
        }),
        ('Imagen', {
            'fields': ('foto',),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def mostrar_foto(self, obj):
        """Muestra una miniatura de la foto de la sala"""
        if obj.foto:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.foto.url
            )
        return "Sin foto"
    mostrar_foto.short_description = "Foto"
    
    def get_queryset(self, request):
        """Optimiza las consultas incluyendo las reservas relacionadas"""
        return super().get_queryset(request).prefetch_related('reserva_set')


class ParticipanteInline(admin.TabularInline):
    """
    Inline para mostrar y editar participantes de una reserva.
    
    Permite agregar, editar y eliminar participantes directamente
    desde la vista de edición de una reserva.
    """
    
    model = Participante
    extra = 1
    readonly_fields = ['fecha_invitacion', 'fecha_confirmacion']
    fields = ['usuario', 'estado_asistencia', 'fecha_invitacion', 'fecha_confirmacion']


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Reserva.
    
    Permite a los administradores gestionar las reservas de salas,
    incluyendo la información de la reunión y los participantes.
    """
    
    list_display = [
        'titulo', 
        'sala', 
        'usuario_creador', 
        'fecha_inicio', 
        'fecha_fin', 
        'estado',
        'duracion_display',
        'participantes_count'
    ]
    list_filter = [
        'estado', 
        'sala', 
        'fecha_inicio', 
        'usuario_creador'
    ]
    search_fields = [
        'titulo', 
        'descripcion', 
        'sala__nombre', 
        'usuario_creador__username',
        'usuario_creador__first_name',
        'usuario_creador__last_name'
    ]
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'duracion_display',
        'participantes_count'
    ]
    date_hierarchy = 'fecha_inicio'
    inlines = [ParticipanteInline]
    
    fieldsets = (
        ('Información de la Reunión', {
            'fields': ('titulo', 'descripcion', 'estado')
        }),
        ('Sala y Organizador', {
            'fields': ('sala', 'usuario_creador')
        }),
        ('Horario', {
            'fields': ('fecha_inicio', 'fecha_fin', 'duracion_display')
        }),
        ('Estadísticas', {
            'fields': ('participantes_count',),
            'classes': ('collapse',)
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def duracion_display(self, obj):
        """Muestra la duración de la reserva en formato legible"""
        return f"{obj.duracion_minutos} minutos"
    duracion_display.short_description = "Duración"
    
    def participantes_count(self, obj):
        """Cuenta el número de participantes de la reserva"""
        return obj.get_participantes().count()
    participantes_count.short_description = "Participantes"
    
    def get_queryset(self, request):
        """Optimiza las consultas incluyendo las relaciones"""
        return super().get_queryset(request).select_related(
            'sala', 'usuario_creador'
        ).prefetch_related('participante_set__usuario')
    
    def save_formset(self, request, form, formset, change):
        """Maneja el guardado de los participantes inline"""
        instances = formset.save(commit=False)
        
        for instance in instances:
            if isinstance(instance, Participante):
                # Si es un nuevo participante, enviar notificación
                if not instance.pk:
                    # Aquí se enviaría la notificación de invitación
                    pass
            instance.save()
        
        formset.save_m2m()


@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Participante.
    
    Permite a los administradores gestionar los participantes
    de las reservas de forma independiente.
    """
    
    list_display = [
        'usuario', 
        'reserva', 
        'estado_asistencia', 
        'fecha_invitacion',
        'fecha_confirmacion'
    ]
    list_filter = [
        'estado_asistencia', 
        'fecha_invitacion', 
        'reserva__sala'
    ]
    search_fields = [
        'usuario__username',
        'usuario__first_name',
        'usuario__last_name',
        'reserva__titulo'
    ]
    readonly_fields = ['fecha_invitacion', 'fecha_confirmacion']
    
    def get_queryset(self, request):
        """Optimiza las consultas incluyendo las relaciones"""
        return super().get_queryset(request).select_related(
            'usuario', 'reserva', 'reserva__sala'
        )


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Notificacion.
    
    Permite a los administradores revisar el historial de
    notificaciones enviadas y su estado.
    """
    
    list_display = [
        'tipo', 
        'destinatario', 
        'reserva', 
        'email_enviado',
        'estado', 
        'fecha_envio'
    ]
    list_filter = [
        'tipo', 
        'estado', 
        'fecha_envio',
        'reserva__sala'
    ]
    search_fields = [
        'destinatario__username',
        'destinatario__first_name',
        'destinatario__last_name',
        'email_enviado',
        'reserva__titulo'
    ]
    readonly_fields = ['fecha_envio', 'error_mensaje']
    
    def get_queryset(self, request):
        """Optimiza las consultas incluyendo las relaciones"""
        return super().get_queryset(request).select_related(
            'destinatario', 'reserva', 'reserva__sala'
        )
    
    def has_add_permission(self, request):
        """No permite crear notificaciones manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permite editar notificaciones"""
        return False 