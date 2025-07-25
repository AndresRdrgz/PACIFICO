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