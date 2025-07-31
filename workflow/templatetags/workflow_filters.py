import os
from django import template
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def basename(value):
    """Returns the base name of a file path."""
    return os.path.basename(value)

@register.filter
def get_etapa_count(solicitudes_por_etapa, etapa):
    """Obtener el conteo de solicitudes para una etapa específica"""
    if solicitudes_por_etapa and etapa in solicitudes_por_etapa:
        return solicitudes_por_etapa[etapa].count()
    return 0

@register.filter
def get_etapa_solicitudes(solicitudes_por_etapa, etapa):
    """Obtener las solicitudes para una etapa específica"""
    if solicitudes_por_etapa and etapa in solicitudes_por_etapa:
        return solicitudes_por_etapa[etapa]
    return []

@register.filter
def get_item(dictionary, key):
    """Obtener un elemento de un diccionario por su clave"""
    if dictionary and key in dictionary:
        return dictionary[key]
    return []

@register.filter
def filter_activas(solicitudes):
    """Filtrar solicitudes activas"""
    if not solicitudes:
        return []
    return [s for s in solicitudes if s.etapa_actual is not None]

@register.filter
def filter_completadas(solicitudes):
    """Filtrar solicitudes completadas"""
    if not solicitudes:
        return []
    return [s for s in solicitudes if s.etapa_actual is None]

@register.filter
def filter_vencidas(solicitudes):
    """Filtrar solicitudes vencidas"""
    if not solicitudes:
        return []
    
    vencidas = []
    for solicitud in solicitudes:
        if solicitud.etapa_actual:
            tiempo_en_etapa = timezone.now() - solicitud.fecha_ultima_actualizacion
            if tiempo_en_etapa > solicitud.etapa_actual.sla:
                vencidas.append(solicitud)
    
    return vencidas

@register.filter
def is_vencida(solicitud):
    """Verificar si una solicitud está vencida"""
    if solicitud.etapa_actual:
        tiempo_en_etapa = timezone.now() - solicitud.fecha_ultima_actualizacion
        return tiempo_en_etapa > solicitud.etapa_actual.sla
    return False

@register.filter
def tiempo_restante(solicitud):
    """Calcular tiempo restante para una solicitud"""
    if solicitud.etapa_actual:
        tiempo_en_etapa = timezone.now() - solicitud.fecha_ultima_actualizacion
        tiempo_restante = solicitud.etapa_actual.sla - tiempo_en_etapa
        
        if tiempo_restante.total_seconds() <= 0:
            return "Vencida"
        
        dias = tiempo_restante.days
        horas = tiempo_restante.seconds // 3600
        minutos = (tiempo_restante.seconds % 3600) // 60
        
        if dias > 0:
            return f"{dias}d {horas}h"
        elif horas > 0:
            return f"{horas}h {minutos}m"
        else:
            return f"{minutos}m"
    
    return "N/A"

@register.filter
def porcentaje_completado(solicitud):
    """Calcular porcentaje completado de una solicitud"""
    if not solicitud.etapa_actual:
        return 100
    
    pipeline = solicitud.pipeline
    etapas = pipeline.etapas.all().order_by('orden')
    total_etapas = etapas.count()
    
    if total_etapas == 0:
        return 0
    
    # Encontrar la posición de la etapa actual
    etapa_actual_orden = solicitud.etapa_actual.orden
    etapas_completadas = etapas.filter(orden__lt=etapa_actual_orden).count()
    
    return int((etapas_completadas / total_etapas) * 100)

@register.filter
def get_avatar_url(user):
    """Obtener URL del avatar del usuario"""
    if hasattr(user, 'profile') and user.profile.avatar:
        return user.profile.avatar.url
    return '/static/images/default-avatar.png'

@register.filter
def get_user_display_name(user):
    """Obtener nombre de visualización del usuario"""
    if user.first_name and user.last_name:
        return f"{user.first_name} {user.last_name}"
    return user.username

@register.filter
def get_user_role(user):
    """Obtener rol del usuario"""
    if user.is_superuser:
        return "Administrador"
    elif user.groups.all():
        return user.groups.first().name
    return "Usuario"

@register.filter
def break_words(value):
    """Coloca solo un salto de línea después de la primera palabra (máximo 2 líneas)."""
    if not value:
        return ''
    partes = value.split(' ', 1)
    if len(partes) == 2:
        return f'{partes[0]}<br>{partes[1]}'
    return value

@register.filter
def split(value, arg):
    """Dividir una cadena por un separador y retornar una lista"""
    if not value:
        return []
    return [item.strip() for item in value.split(arg) if item.strip()]

@register.filter
def get_item(dictionary, key):
    """Obtener un elemento de un diccionario por su clave"""
    if dictionary and key in dictionary:
        return dictionary[key]
    return []

@register.filter
def sla_to_hours(sla):
    """Convertir un timedelta SLA a horas"""
    if not sla:
        return "0h"
    
    if isinstance(sla, str):
        # Si es un string, intentar parsearlo
        try:
            # Formato "X days, HH:MM:SS" o "HH:MM:SS"
            if ', ' in sla:
                # Formato "X days, HH:MM:SS"
                parts = sla.split(', ')
                days = int(parts[0].split(' ')[0])
                time_parts = parts[1].split(':')
                hours = int(time_parts[0])
                total_hours = days * 24 + hours
            else:
                # Formato "HH:MM:SS"
                time_parts = sla.split(':')
                total_hours = int(time_parts[0])
            
            return f"{total_hours}h"
        except (ValueError, IndexError):
            return sla
    elif isinstance(sla, timedelta):
        # Si es un timedelta
        total_hours = sla.days * 24 + sla.seconds // 3600
        return f"{total_hours}h"
    else:
        return str(sla) 

@register.filter
def sla_color_class(sla_color):
    """Convierte el color de SLA texto a clase CSS"""
    color_map = {
        'text-danger': 'bg-red-500',
        'text-warning': 'bg-yellow-500', 
        'text-success': 'bg-green-500',
    }
    return color_map.get(sla_color, 'bg-gray-400')

@register.filter
def priority_class(priority):
    """Retorna las clases CSS para la prioridad"""
    if not priority:
        return 'bg-gray-100 text-gray-800'
    
    priority_classes = {
        'Alta': 'bg-red-100 text-red-800',
        'Media': 'bg-yellow-100 text-yellow-800', 
        'Baja': 'bg-green-100 text-green-800'
    }
    return priority_classes.get(priority, 'bg-gray-100 text-gray-800')

@register.filter
def user_avatar_or_initial(user):
    """Retorna el avatar del usuario o sus iniciales"""
    if not user:
        return {
            'type': 'icon',
            'content': 'fas fa-user-slash',
            'class': 'w-4 h-4 bg-gray-200 rounded-full flex items-center justify-center text-xs font-medium text-gray-500'
        }
    
    # Verificar si tiene foto de perfil
    if hasattr(user, 'userprofile') and user.userprofile and hasattr(user.userprofile, 'profile_picture') and user.userprofile.profile_picture:
        return {
            'type': 'image',
            'src': user.userprofile.profile_picture.url,
            'alt': user.get_full_name() or user.username,
            'class': 'w-4 h-4 rounded-full object-cover border'
        }
    
    # Retornar iniciales
    initial = ''
    if user.first_name:
        initial = user.first_name[0].upper()
    elif user.username:
        initial = user.username[0].upper()
    
    return {
        'type': 'initial',
        'content': initial,
        'class': 'w-4 h-4 bg-gray-300 rounded-full flex items-center justify-center text-xs font-medium text-gray-600'
    }

@register.filter
def is_unassigned(asignado_a):
    """Verifica si una solicitud no está asignada"""
    return asignado_a == 'Sin asignar' or not asignado_a

@register.filter
def digital_badge_needed(etiquetas, origen):
    """Determina si se necesita mostrar el badge digital"""
    return origen == 'Canal Digital' and not etiquetas

@register.filter
def priority_background_color(priority):
    """Retorna el color de fondo para la prioridad"""
    colors = {
        'Alta': '#fee2e2',
        'Media': '#fef9c3',
        'Baja': '#dcfce7'
    }
    return colors.get(priority, 'white')

@register.filter
def sla_border_color(sla_color):
    """Retorna el color del borde basado en el SLA"""
    colors = {
        'text-danger': '#dc3545',
        'text-warning': '#ffc107', 
        'text-success': '#198754'
    }
    return colors.get(sla_color, '#6c757d')

@register.filter
def priority_text_color(priority):
    """Retorna el color del texto para la prioridad"""
    colors = {
        'Alta': '#dc3545',
        'Media': '#ffc107',
        'Baja': '#198754'
    }
    return colors.get(priority, '#6c757d')

@register.filter
def sla_status_text(sla_color):
    """Convierte el color SLA a texto descriptivo"""
    status_map = {
        'text-success': 'En tiempo',
        'text-warning': 'Por vencer', 
        'text-danger': 'Vencido'
    }
    return status_map.get(sla_color, 'N/A')

@register.filter
def sla_data_attribute(sla_color):
    """Convierte el color SLA a atributo data"""
    data_map = {
        'text-danger': 'vencido',
        'text-warning': 'por vencer',
        'text-success': 'en tiempo'
    }
    return data_map.get(sla_color, 'sin sla')

@register.filter
def sla_bg_class(sla_color):
    """Retorna clase de fondo para filas según SLA"""
    if sla_color == 'text-danger':
        return 'bg-danger bg-opacity-10'
    return ''

@register.filter
def has_group(user, group_name):
    """Verifica si un usuario pertenece a un grupo específico"""
    return user.groups.filter(name=group_name).exists()