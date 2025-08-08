# workflow/signals_backoffice.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import CalificacionDocumentoBackoffice, HistorialBackoffice
from .modelsWorkflow import Solicitud


# --------------------------------------
# SIGNALS PARA CALIFICACIÓN
# --------------------------------------

@receiver(pre_save, sender=CalificacionDocumentoBackoffice)
def capturar_calificacion_anterior(sender, instance, **kwargs):
    """
    Captura la calificación anterior antes de guardar los cambios
    """
    if instance.pk:  # Solo si es una actualización, no una creación
        try:
            # Obtener el registro anterior de la base de datos
            old_instance = CalificacionDocumentoBackoffice.objects.get(pk=instance.pk)
            # Almacenar TANTO el estado como el motivo anterior Y el estado de subsanado
            instance._calificacion_anterior = old_instance.estado
            instance._motivo_anterior = old_instance.opcion_desplegable
            instance._subsanado_anterior = old_instance.subsanado
            instance._subsanado_por_anterior = old_instance.subsanado_por
        except CalificacionDocumentoBackoffice.DoesNotExist:
            instance._calificacion_anterior = None
            instance._motivo_anterior = None
            instance._subsanado_anterior = None
            instance._subsanado_por_anterior = None
    else:
        instance._calificacion_anterior = None
        instance._motivo_anterior = None
        instance._subsanado_anterior = None
        instance._subsanado_por_anterior = None


@receiver(post_save, sender=CalificacionDocumentoBackoffice)
def registrar_cambio_calificacion(sender, instance, created, **kwargs):
    """
    Registra cambios en calificaciones de documentos en el historial
    Y maneja reseteo automático de campos subsanado_por_oficial y pendiente_completado
    """
    
    # NUEVO: Manejar reseteo de campos - TEMPORALMENTE COMENTADO HASTA MIGRATION
    # if created:  # Nueva calificación creada por backoffice
    #     try:
    #         # Si es una nueva calificación "malo", resetear subsanado_por_oficial
    #         if instance.estado == 'malo':
    #             CalificacionDocumentoBackoffice.objects.filter(
    #                 requisito_solicitud=instance.requisito_solicitud
    #             ).update(
    #                 subsanado_por_oficial=False
    #             )
    #             print(f"🔄 Reseteado subsanado_por_oficial para documento: {instance.requisito_solicitud.requisito.nombre}")
    #         
    #         # Si es una nueva calificación "pendiente", resetear pendiente_completado
    #         elif instance.estado == 'pendiente':
    #             CalificacionDocumentoBackoffice.objects.filter(
    #                 requisito_solicitud=instance.requisito_solicitud
    #             ).update(
    #                 pendiente_completado=False
    #             )
    #             print(f"🔄 Reseteado pendiente_completado para documento: {instance.requisito_solicitud.requisito.nombre}")
    #             
    #     except Exception as e:
    #         print(f"Error reseteando campos automáticos: {e}")
    
    if created:
        print(f"🔄 Signal de reseteo de campos temporalmente deshabilitado - ejecutar migration primero")
        
        # NUEVO: Registrar cuando se crea una calificación directamente como subsanado
        print(f"🔍 DEBUG SIGNAL CREATED: instance.subsanado={instance.subsanado}, estado={instance.estado}")
        if instance.subsanado:
            try:
                HistorialBackoffice.objects.create(
                    tipo_evento='calificacion',
                    solicitud=instance.requisito_solicitud.solicitud,
                    usuario=instance.calificado_por,
                    documento_nombre=instance.requisito_solicitud.requisito.nombre,
                    calificacion_anterior='sin_calificar',
                    calificacion_nueva=instance.estado,
                    requisito_solicitud_id=instance.requisito_solicitud.id,
                    observaciones=f"Documento marcado como SUBSANADO directamente por {instance.subsanado_por.get_full_name() if instance.subsanado_por else 'usuario'}"
                )
                print(f"📋 Historial registrado: Subsanado directo para documento {instance.requisito_solicitud.requisito.nombre}")
            except Exception as e:
                print(f"Error registrando subsanado directo: {e}")
    
    # LÓGICA MEJORADA: Registrar si cambia el estado, el motivo O el subsanado
    if not created and hasattr(instance, '_calificacion_anterior'):
        calificacion_anterior = instance._calificacion_anterior
        calificacion_nueva = instance.estado
        motivo_anterior = instance._motivo_anterior
        motivo_nuevo = instance.opcion_desplegable
        subsanado_anterior = getattr(instance, '_subsanado_anterior', False)
        subsanado_nuevo = instance.subsanado
        subsanado_por_anterior = getattr(instance, '_subsanado_por_anterior', None)
        subsanado_por_nuevo = instance.subsanado_por
        
        # Registrar si cambió el estado, el motivo O el subsanado
        cambio_estado = calificacion_anterior != calificacion_nueva
        cambio_motivo = motivo_anterior != motivo_nuevo
        cambio_subsanado = subsanado_anterior != subsanado_nuevo
        
        print(f"🔍 DEBUG SIGNAL: cambio_estado={cambio_estado}, cambio_motivo={cambio_motivo}, cambio_subsanado={cambio_subsanado}")
        print(f"🔍 DEBUG SIGNAL: subsanado_anterior={subsanado_anterior}, subsanado_nuevo={subsanado_nuevo}")
        print(f"🔍 DEBUG SIGNAL: calificacion_anterior={calificacion_anterior}, calificacion_nueva={calificacion_nueva}")
        
        if cambio_estado or cambio_motivo or cambio_subsanado:
            try:
                # Preparar descripción del cambio
                observaciones_partes = []
                
                if cambio_estado:
                    observaciones_partes.append(f"estado ({calificacion_anterior} → {calificacion_nueva})")
                
                if cambio_motivo:
                    observaciones_partes.append("motivo")
                
                if cambio_subsanado:
                    if subsanado_nuevo:
                        observaciones_partes.append(f"marcado como SUBSANADO por {subsanado_por_nuevo.get_full_name() if subsanado_por_nuevo else 'usuario'}")
                    else:
                        observaciones_partes.append("removido marca de subsanado")
                
                if len(observaciones_partes) == 1:
                    observaciones = f"Cambio de {observaciones_partes[0]}"
                else:
                    observaciones = f"Cambios: {', '.join(observaciones_partes)}"
                
                # Siempre usar 'calificacion' como tipo de evento (subsanado se diferencia en observaciones)
                tipo_evento = 'calificacion'
                
                HistorialBackoffice.objects.create(
                    tipo_evento=tipo_evento,
                    solicitud=instance.requisito_solicitud.solicitud,
                    usuario=instance.calificado_por,
                    documento_nombre=instance.requisito_solicitud.requisito.nombre,
                    calificacion_anterior=calificacion_anterior,
                    calificacion_nueva=calificacion_nueva,
                    requisito_solicitud_id=instance.requisito_solicitud.id,
                    observaciones=observaciones
                )
                print(f"📋 Historial registrado: {observaciones} para documento {instance.requisito_solicitud.requisito.nombre}")
            except Exception as e:
                # Log error but don't break the flow
                print(f"Error registrando cambio de calificación: {e}")
                
        # NUEVO: Reseteo en actualizaciones - TEMPORALMENTE COMENTADO HASTA MIGRATION
        # if calificacion_nueva == 'malo' and calificacion_anterior != 'malo':
        #     try:
        #         CalificacionDocumentoBackoffice.objects.filter(
        #             requisito_solicitud=instance.requisito_solicitud
        #         ).update(
        #             subsanado_por_oficial=False
        #         )
        #         print(f"🔄 Reseteado subsanado_por_oficial en actualización")
        #     except Exception as e:
        #         print(f"Error reseteando campos en actualización: {e}")
        
        if calificacion_nueva == 'malo' and calificacion_anterior != 'malo':
            print(f"🔄 Reseteo automático temporalmente deshabilitado - ejecutar migration primero")


# --------------------------------------
# SIGNALS PARA SUBESTADOS
# --------------------------------------

@receiver(pre_save, sender=Solicitud)
def capturar_subestado_anterior(sender, instance, **kwargs):
    """
    Captura el subestado anterior y estado de asignación antes de cambiar
    """
    if instance.pk:  # Solo si es una actualización
        try:
            old_instance = Solicitud.objects.get(pk=instance.pk)
            instance._subestado_anterior = old_instance.subestado_actual  # ✅ CORREGIDO: usar subestado_actual
            instance._fecha_actualizacion_anterior = old_instance.fecha_ultima_actualizacion  # ✅ CORREGIDO: usar fecha_ultima_actualizacion
            # ✅ NUEVO: Capturar estado de asignación anterior para eventos de bandeja grupal
            instance._asignada_a_anterior = old_instance.asignada_a
        except Solicitud.DoesNotExist:
            instance._subestado_anterior = None
            instance._fecha_actualizacion_anterior = None
            instance._asignada_a_anterior = None
    else:
        instance._subestado_anterior = None
        instance._fecha_actualizacion_anterior = None
        instance._asignada_a_anterior = None


@receiver(post_save, sender=Solicitud)
def registrar_cambio_subestado(sender, instance, created, **kwargs):  
    """
    Registra cambios de subestado y eventos de bandeja grupal en el historial (solo para Back Office)
    """
    # Solo para solicitudes en Back Office
    if not instance.etapa_actual or instance.etapa_actual.nombre != "Back Office":
        return
    
    # Solo si es una actualización 
    if not created and hasattr(instance, '_subestado_anterior'):
        subestado_anterior = instance._subestado_anterior
        subestado_nuevo = instance.subestado_actual  # ✅ CORREGIDO: usar subestado_actual
        fecha_actualizacion_anterior = instance._fecha_actualizacion_anterior  # ✅ CORREGIDO: usar nombre correcto
        asignada_a_anterior = instance._asignada_a_anterior  # ✅ NUEVO: estado de asignación anterior
        asignada_a_actual = instance.asignada_a  # Estado de asignación actual
        
        try:
            # Determinar usuario responsable
            usuario_responsable = (instance.asignada_a or 
                                 instance.creada_por or 
                                 getattr(instance, 'propietario', None))
            
            # Si no hay usuario, usar el primero disponible (fallback)
            if not usuario_responsable:
                from django.contrib.auth.models import User
                usuario_responsable = User.objects.filter(is_active=True).first()
            
            # ✅ NUEVO: Detectar ASIGNACIÓN DESDE BANDEJA GRUPAL 
            # (asignada_a cambió de None a un usuario)
            if asignada_a_anterior is None and asignada_a_actual is not None:
                # Buscar el evento de entrada a bandeja grupal más reciente para calcular tiempo
                entrada_bandeja = HistorialBackoffice.objects.filter(
                    solicitud=instance,
                    tipo_evento='entrada_bandeja_grupal',
                    subestado_destino=subestado_nuevo
                ).order_by('-fecha_evento').first()
                
                tiempo_en_bandeja_grupal = None
                fecha_asignacion = timezone.now()
                
                if entrada_bandeja and entrada_bandeja.fecha_entrada_bandeja_grupal:
                    tiempo_en_bandeja_grupal = fecha_asignacion - entrada_bandeja.fecha_entrada_bandeja_grupal
                
                HistorialBackoffice.objects.create(
                    tipo_evento='asignacion_desde_bandeja_grupal',
                    solicitud=instance,
                    usuario=usuario_responsable,  # Quien provocó el cambio
                    usuario_asignado=asignada_a_actual,  # A quién se le asignó
                    subestado_destino=subestado_nuevo,
                    fecha_asignacion_bandeja_grupal=fecha_asignacion,
                    tiempo_en_bandeja_grupal=tiempo_en_bandeja_grupal,
                    observaciones=f"Asignación automática desde bandeja grupal detectada"
                )
            
            # ✅ NUEVO: Detectar ENTRADA A BANDEJA GRUPAL
            # (cambió de subestado y asignada_a = None)
            elif subestado_anterior != subestado_nuevo and asignada_a_actual is None:
                HistorialBackoffice.objects.create(
                    tipo_evento='entrada_bandeja_grupal',
                    solicitud=instance,
                    usuario=usuario_responsable,
                    subestado_destino=subestado_nuevo,
                    fecha_entrada_bandeja_grupal=timezone.now(),
                    observaciones=f"Entrada automática a bandeja grupal detectada"
                )
            
            # ✅ REGISTRAR CAMBIO DE SUBESTADO NORMAL
            # Solo registrar si realmente cambió el subestado (y no es un evento de bandeja grupal puro)
            elif subestado_anterior != subestado_nuevo:
                # Calcular tiempo en subestado anterior (aproximado)
                tiempo_en_subestado = None
                fecha_salida = timezone.now()
                
                if fecha_actualizacion_anterior:
                    tiempo_en_subestado = fecha_salida - fecha_actualizacion_anterior
                
                # Registrar salida del subestado anterior
                if subestado_anterior:
                    HistorialBackoffice.objects.create(
                        tipo_evento='subestado',
                        solicitud=instance,
                        usuario=usuario_responsable,
                        subestado_origen=subestado_anterior,
                        subestado_destino=subestado_nuevo,
                        fecha_entrada_subestado=fecha_actualizacion_anterior,
                        fecha_salida_subestado=fecha_salida,
                        tiempo_en_subestado=tiempo_en_subestado,
                        observaciones=f"Cambio automático de subestado detectado"
                    )
                
        except Exception as e:
            # Log error but don't break the flow
            print(f"Error registrando cambio de subestado/bandeja grupal: {e}")


# --------------------------------------
# FUNCIONES UTILITARIAS PARA REGISTRO MANUAL
# --------------------------------------

def registrar_devolucion_manual(solicitud, usuario, motivo, etapa_destino=None):
    """
    Función para registrar manualmente una devolución desde las vistas
    """
    try:
        HistorialBackoffice.objects.create(
            tipo_evento='devolucion',
            solicitud=solicitud,
            usuario=usuario,
            motivo_devolucion=motivo,
            observaciones=f"Devuelto a etapa: {etapa_destino.nombre if etapa_destino else 'Negocio'}"
        )
        return True
    except Exception as e:
        print(f"Error registrando devolución: {e}")
        return False


def registrar_entrada_subestado_manual(solicitud, usuario, subestado_destino, observaciones=""):
    """
    Función para registrar manualmente entrada a un subestado
    """
    try:
        HistorialBackoffice.objects.create(
            tipo_evento='subestado',
            solicitud=solicitud,
            usuario=usuario,
            subestado_destino=subestado_destino,
            fecha_entrada_subestado=timezone.now(),
            observaciones=observaciones or f"Entrada manual a {subestado_destino.nombre}"
        )
        return True
    except Exception as e:
        print(f"Error registrando entrada a subestado: {e}")
        return False


def registrar_entrada_bandeja_grupal_manual(solicitud, usuario, subestado, observaciones=""):
    """
    Función para registrar manualmente entrada a bandeja grupal
    """
    try:
        HistorialBackoffice.objects.create(
            tipo_evento='entrada_bandeja_grupal',
            solicitud=solicitud,
            usuario=usuario,
            subestado_destino=subestado,
            fecha_entrada_bandeja_grupal=timezone.now(),
            observaciones=observaciones or f"Entrada manual a bandeja grupal en {subestado.nombre}"
        )
        return True
    except Exception as e:
        print(f"Error registrando entrada a bandeja grupal: {e}")
        return False


def registrar_asignacion_bandeja_grupal_manual(solicitud, usuario_que_asigna, usuario_asignado, subestado, observaciones=""):
    """
    Función para registrar manualmente asignación desde bandeja grupal
    """
    try:
        # Buscar el evento de entrada a bandeja grupal más reciente para calcular tiempo
        entrada_bandeja = HistorialBackoffice.objects.filter(
            solicitud=solicitud,
            tipo_evento='entrada_bandeja_grupal',
            subestado_destino=subestado
        ).order_by('-fecha_evento').first()
        
        tiempo_en_bandeja_grupal = None
        fecha_asignacion = timezone.now()
        
        if entrada_bandeja and entrada_bandeja.fecha_entrada_bandeja_grupal:
            tiempo_en_bandeja_grupal = fecha_asignacion - entrada_bandeja.fecha_entrada_bandeja_grupal
        
        HistorialBackoffice.objects.create(
            tipo_evento='asignacion_desde_bandeja_grupal',
            solicitud=solicitud,
            usuario=usuario_que_asigna,
            usuario_asignado=usuario_asignado,
            subestado_destino=subestado,
            fecha_asignacion_bandeja_grupal=fecha_asignacion,
            tiempo_en_bandeja_grupal=tiempo_en_bandeja_grupal,
            observaciones=observaciones or f"Asignación manual desde bandeja grupal a {usuario_asignado.username}"
        )
        return True
    except Exception as e:
        print(f"Error registrando asignación desde bandeja grupal: {e}")
        return False


def obtener_historial_solicitud(solicitud_id, tipo_evento=None):
    """
    Función utilitaria para obtener el historial de una solicitud
    """
    queryset = HistorialBackoffice.objects.filter(solicitud_id=solicitud_id)
    
    if tipo_evento:
        queryset = queryset.filter(tipo_evento=tipo_evento)
    
    return queryset.select_related('usuario', 'subestado_origen', 'subestado_destino', 'usuario_asignado')


def registrar_subsanado_manual(solicitud, usuario, documento_nombre, requisito_solicitud_id, observaciones=""):
    """
    Función para registrar manualmente un evento de subsanado
    """
    try:
        HistorialBackoffice.objects.create(
            tipo_evento='calificacion',
            solicitud=solicitud,
            usuario=usuario,
            documento_nombre=documento_nombre,
            requisito_solicitud_id=requisito_solicitud_id,
            observaciones=observaciones or f"Documento {documento_nombre} marcado como SUBSANADO por {usuario.get_full_name() or usuario.username}"
        )
        print(f"📋 Historial manual registrado: Subsanado para documento {documento_nombre}")
        return True
    except Exception as e:
        print(f"Error registrando subsanado manual: {e}")
        return False


def obtener_estadisticas_bandeja_grupal(subestado=None, fecha_desde=None, fecha_hasta=None):
    """
    Función utilitaria para obtener estadísticas de bandeja grupal
    """
    from django.db.models import Avg, Count, Min, Max
    
    queryset = HistorialBackoffice.objects.filter(
        tipo_evento='asignacion_desde_bandeja_grupal',
        tiempo_en_bandeja_grupal__isnull=False
    )
    
    if subestado:
        queryset = queryset.filter(subestado_destino=subestado)
    
    if fecha_desde:
        queryset = queryset.filter(fecha_evento__gte=fecha_desde)
        
    if fecha_hasta:
        queryset = queryset.filter(fecha_evento__lte=fecha_hasta)
    
    estadisticas = queryset.aggregate(
        tiempo_promedio=Avg('tiempo_en_bandeja_grupal'),
        tiempo_minimo=Min('tiempo_en_bandeja_grupal'),
        tiempo_maximo=Max('tiempo_en_bandeja_grupal'),
        total_asignaciones=Count('id')
    )
    
    return estadisticas