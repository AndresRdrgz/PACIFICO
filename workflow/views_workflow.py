from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django.contrib.auth.models import Group, User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db import models
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import os
import tempfile
import json
import io
from PyPDF2 import PdfMerger
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from PIL import Image
# PDF Generation imports
try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
except ImportError:
    pisa = None
    XHTML2PDF_AVAILABLE = False
from .modelsWorkflow import (
    Pipeline, Etapa, SubEstado, TransicionEtapa, PermisoEtapa, 
    Solicitud, HistorialSolicitud, Requisito, RequisitoPipeline, 
    RequisitoSolicitud, CampoPersonalizado, ValorCampoSolicitud,
    RequisitoTransicion, SolicitudComentario, PermisoPipeline, PermisoBandeja,
    NivelComite, UsuarioNivelComite, CatalogoPendienteAntesFirma, PendienteSolicitud,
    AgendaFirma
)
from .models import ClienteEntrevista, CalificacionCampo
from pacifico.models import UserProfile, Cliente, Cotizacion
import json
import ssl


def usuario_puede_modificar_solicitud(usuario, solicitud):
    """
    Verifica si un usuario puede modificar una solicitud.
    Incluye permisos básicos y supervisión de grupos (sin importar el rol del usuario).
    """
    print(f"🔍 DEBUG PERMISOS: Verificando permisos para usuario {usuario.username} en solicitud {solicitud.id}")
    
    # Permisos básicos
    if (
        solicitud.creada_por == usuario
        or solicitud.asignada_a == usuario
        or usuario.is_superuser
        or getattr(usuario, "is_staff", False)
    ):
        print(f"✅ DEBUG: Usuario {usuario.username} tiene permisos básicos (creador/asignado/superuser/staff)")
        return True

    print(f"🔍 DEBUG: Verificando supervisión de grupos para {usuario.username}")
    
    # Verificación por supervisión de grupos
    try:
        from pacifico.utils_grupos import (
            obtener_usuarios_supervisados_por_usuario,
            obtener_grupos_supervisados_por_usuario,
        )

        # 1. Verificar si supervisa a los usuarios relacionados con la solicitud
        print(f"🔍 DEBUG: Obteniendo usuarios supervisados por {usuario.username}")
        usuarios_supervisados = obtener_usuarios_supervisados_por_usuario(usuario)
        print(f"🔍 DEBUG: Usuarios supervisados encontrados: {usuarios_supervisados.count()}")
        
        if usuarios_supervisados.exists():
            usuarios_relacionados = [u for u in [solicitud.creada_por, solicitud.asignada_a] if u]
            print(f"🔍 DEBUG: Usuarios relacionados con solicitud: {[u.username for u in usuarios_relacionados]}")
            
            for usuario_relacionado in usuarios_relacionados:
                if usuarios_supervisados.filter(pk=usuario_relacionado.pk).exists():
                    print(f"✅ DEBUG: Usuario {usuario.username} supervisa a {usuario_relacionado.username}")
                    return True

        # 2. Verificar si supervisa grupos con permisos de bandeja/pipeline
        print(f"🔍 DEBUG: Obteniendo grupos supervisados por {usuario.username}")
        grupos_supervisados_profiles = obtener_grupos_supervisados_por_usuario(usuario)
        print(f"🔍 DEBUG: Grupos supervisados encontrados: {grupos_supervisados_profiles.count()}")
        
        if grupos_supervisados_profiles.exists():
            try:
                from workflow.modelsWorkflow import PermisoBandeja, PermisoPipeline

                grupos_supervisados = [gp.group for gp in grupos_supervisados_profiles]
                print(f"✅ DEBUG: Usuario {usuario.username} supervisa grupos: {[g.name for g in grupos_supervisados]}")

                # Verificar permisos de bandeja para la etapa actual
                if solicitud.etapa_actual:
                    print(f"🔍 DEBUG: Verificando permisos de bandeja para etapa {solicitud.etapa_actual.nombre}")
                    permisos_bandeja = PermisoBandeja.objects.filter(
                        etapa=solicitud.etapa_actual,
                        grupo__in=grupos_supervisados,
                        puede_transicionar=True,
                    )
                    print(f"🔍 DEBUG: Permisos de bandeja encontrados: {permisos_bandeja.count()}")
                    
                    if permisos_bandeja.exists():
                        print(f"✅ DEBUG: Grupo supervisado tiene permiso de transición en etapa {solicitud.etapa_actual.nombre}")
                        return True

                # Verificar permisos de pipeline
                print(f"🔍 DEBUG: Verificando permisos de pipeline para {solicitud.pipeline.nombre}")
                permisos_pipeline = PermisoPipeline.objects.filter(
                    pipeline=solicitud.pipeline,
                    grupo__in=grupos_supervisados,
                    puede_editar=True,
                )
                print(f"🔍 DEBUG: Permisos de pipeline encontrados: {permisos_pipeline.count()}")
                
                if permisos_pipeline.exists():
                    print(f"✅ DEBUG: Grupo supervisado tiene permiso de edición en pipeline {solicitud.pipeline.nombre}")
                    return True

            except Exception as e:
                print(f"❌ DEBUG: Error verificando permisos de grupo: {e}")
                import traceback
                print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
                pass
        else:
            print(f"❌ DEBUG: Usuario {usuario.username} NO supervisa ningún grupo")

    except ImportError as e:
        print(f"❌ DEBUG: No se pudo importar utils_grupos: {e}")
        import traceback
        print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
        pass

    print(f"❌ DEBUG: Usuario {usuario.username} NO tiene permisos para modificar solicitud {solicitud.id}")
    return False
import uuid
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
import time
import threading
import queue
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from functools import wraps

# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def get_site_url(request=None):
    """
    Dynamically detect the site URL based on the request object.
    Falls back to settings.SITE_URL if request is not available.
    """
    if request:
        # Build URL from request
        scheme = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        return f"{scheme}://{host}"
    else:
        # Fallback to settings with environment-aware default
        default_url = 'https://cotfid.fpacifico.com' if not getattr(settings, 'DEBUG', True) else 'http://localhost:8000'
        return getattr(settings, 'SITE_URL', default_url)

# ==========================================
# DECORADORES PERSONALIZADOS
# ==========================================

def superuser_permission_required(permission):
    """
    Decorator that bypasses permission checks for superusers.
    For superusers, it only requires login. For regular users, it requires the specified permission.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Superusers bypass all permission checks
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                # For regular users, use the standard permission_required decorator
                from django.contrib.auth.decorators import permission_required
                return permission_required(permission)(view_func)(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# ==========================================
# VISTAS PRINCIPALES DEL WORKFLOW
# ==========================================

@login_required
def dashboard_workflow(request):
    """Dashboard principal del sistema de workflow (vista original)"""
    
    # Obtener solicitudes del usuario
    solicitudes_asignadas = Solicitud.objects.filter(
        asignada_a=request.user
    ).select_related('pipeline', 'etapa_actual', 'subestado_actual')
    
    # Obtener bandejas grupales a las que tiene acceso
    if request.user.is_superuser or request.user.is_staff:
        # Superuser y super staff ven TODAS las bandejas grupales
        etapas_grupales = Etapa.objects.filter(es_bandeja_grupal=True)
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related('pipeline', 'etapa_actual', 'subestado_actual')
    else:
        # Usuarios regulares - permisos normales
        grupos_usuario = request.user.groups.all()
        etapas_grupales = Etapa.objects.filter(
            es_bandeja_grupal=True,
            permisos__grupo__in=grupos_usuario,
            permisos__puede_ver=True
        )
        
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related('pipeline', 'etapa_actual', 'subestado_actual')
    
    # Estadísticas
    total_solicitudes = solicitudes_asignadas.count() + solicitudes_grupales.count()
    solicitudes_vencidas = 0
    solicitudes_proximo_vencer = 0
    
    for solicitud in solicitudes_asignadas:
        if solicitud.etapa_actual:
            tiempo_en_etapa = timezone.now() - solicitud.fecha_ultima_actualizacion
            if tiempo_en_etapa > solicitud.etapa_actual.sla:
                solicitudes_vencidas += 1
            elif tiempo_en_etapa > solicitud.etapa_actual.sla * 0.8:  # 80% del SLA
                solicitudes_proximo_vencer += 1
    
    # Pipelines disponibles
    pipelines = Pipeline.objects.all()
    
    context = {
        'solicitudes_asignadas': solicitudes_asignadas[:10],
        'solicitudes_grupales': solicitudes_grupales[:10],
        'total_solicitudes': total_solicitudes,
        'solicitudes_vencidas': solicitudes_vencidas,
        'solicitudes_proximo_vencer': solicitudes_proximo_vencer,
        'pipelines': pipelines,
        'etapas_grupales': etapas_grupales,
    }
    
    return render(request, 'workflow/dashboard.html', context)



@login_required
def bandeja_trabajo(request):
    """Bandeja de trabajo del usuario"""
    
    # === SISTEMA DE PERMISOS SUPERUSER Y SUPER STAFF ===
    # Los usuarios superuser y super staff (is_staff=True) pueden ver TODO
    if request.user.is_superuser or request.user.is_staff:
        # Superuser y super staff ven TODAS las solicitudes asignadas
        solicitudes_asignadas = Solicitud.objects.filter(
            asignada_a__isnull=False
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
        
        # Superuser y super staff ven TODAS las bandejas grupales (excluir Comité de Crédito)
        etapas_grupales = Etapa.objects.filter(es_bandeja_grupal=True).exclude(nombre__iexact="Comité de Crédito")
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
    else:
        # Usuarios regulares - permisos normales
        # Obtener solicitudes asignadas al usuario
        solicitudes_asignadas = Solicitud.objects.filter(
            asignada_a=request.user
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
        
        # Obtener bandejas grupales (excluir Comité de Crédito)
        grupos_usuario = request.user.groups.all()
        etapas_grupales = Etapa.objects.filter(
            es_bandeja_grupal=True,
            permisos__grupo__in=grupos_usuario,
            permisos__puede_autoasignar=True
        ).exclude(nombre__iexact="Comité de Crédito")
        
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
    
    # Filtros
    filtro_estado = request.GET.get('estado', '')
    filtro_pipeline = request.GET.get('pipeline', '')
    
    if filtro_estado == 'vencidas':
        solicitudes_asignadas = solicitudes_asignadas.filter(
            fecha_ultima_actualizacion__lt=timezone.now() - F('etapa_actual__sla')
        )
        solicitudes_grupales = solicitudes_grupales.filter(
            fecha_ultima_actualizacion__lt=timezone.now() - F('etapa_actual__sla')
        )
    
    if filtro_pipeline:
        solicitudes_asignadas = solicitudes_asignadas.filter(pipeline_id=filtro_pipeline)
        solicitudes_grupales = solicitudes_grupales.filter(pipeline_id=filtro_pipeline)
    
    # Paginación
    todas_solicitudes = list(solicitudes_asignadas) + list(solicitudes_grupales)
    paginator = Paginator(todas_solicitudes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'solicitudes_asignadas': solicitudes_asignadas,
        'solicitudes_grupales': solicitudes_grupales,
        'pipelines': Pipeline.objects.all(),
        'filtros': {
            'estado': filtro_estado,
            'pipeline': filtro_pipeline,
        }
    }
    
    return render(request, 'workflow/bandeja_trabajo.html', context)


# FUNCIÓN DUPLICADA ELIMINADA - nueva_solicitud está definida más abajo
# Esta función fue comentada para evitar errores 500
    """Crear una nueva solicitud"""
    
    if request.method == 'POST':
        pipeline_id = request.POST.get('pipeline')
        cliente_id = request.POST.get('cliente')
        cotizacion_id = request.POST.get('cotizacion')
        
        if pipeline_id:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            # Obtener primera etapa del pipeline
            primera_etapa = pipeline.etapas.order_by('orden').first()
            
            # Obtener cliente y cotización si se proporcionaron
            cliente = None
            cotizacion = None
            
            if cliente_id:
                cliente = get_object_or_404(Cliente, id=cliente_id)
            
            if cotizacion_id:
                cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
            
            # Obtener motivo de consulta, como se enteró y APC fields del formulario
            motivo_consulta = request.POST.get('motivo_consulta', '')
            como_se_entero = request.POST.get('como_se_entero', '')
            
            # APC Makito fields
            descargar_apc_makito = request.POST.get('descargar_apc_makito') == '1'
            apc_no_cedula = request.POST.get('apc_no_cedula', '') if descargar_apc_makito else None
            apc_tipo_documento = request.POST.get('apc_tipo_documento', '') if descargar_apc_makito else None
            
            # SURA Makito fields
            cotizar_sura_makito = request.POST.get('cotizar_sura_makito') == '1'
            sura_primer_nombre = request.POST.get('sura_primer_nombre', '') if cotizar_sura_makito else None
            sura_segundo_nombre = request.POST.get('sura_segundo_nombre', '') if cotizar_sura_makito else None
            sura_primer_apellido = request.POST.get('sura_primer_apellido', '') if cotizar_sura_makito else None
            sura_segundo_apellido = request.POST.get('sura_segundo_apellido', '') if cotizar_sura_makito else None
            sura_no_documento = request.POST.get('sura_no_documento', '') if cotizar_sura_makito else None
            sura_tipo_documento = request.POST.get('sura_tipo_documento', '') if cotizar_sura_makito else None
            sura_valor_auto = request.POST.get('sura_valor_auto', '') if cotizar_sura_makito else None
            sura_ano_auto = request.POST.get('sura_ano_auto', '') if cotizar_sura_makito else None
            sura_marca = request.POST.get('sura_marca', '') if cotizar_sura_makito else None
            sura_modelo = request.POST.get('sura_modelo', '') if cotizar_sura_makito else None
            
            # Crear solicitud (el código se generará automáticamente via signal)
            solicitud = Solicitud.objects.create(
                pipeline=pipeline,
                etapa_actual=primera_etapa,
                creada_por=request.user,
                propietario=request.user,  # Set propietario to the user who created the solicitud
                cliente=cliente,
                cotizacion=cotizacion,
                motivo_consulta=motivo_consulta,
                como_se_entero=como_se_entero if como_se_entero else None,
                descargar_apc_makito=descargar_apc_makito,
                apc_no_cedula=apc_no_cedula,
                apc_tipo_documento=apc_tipo_documento if apc_tipo_documento else None,
                cotizar_sura_makito=cotizar_sura_makito,
                sura_primer_nombre=sura_primer_nombre,
                sura_segundo_nombre=sura_segundo_nombre,
                sura_primer_apellido=sura_primer_apellido,
                sura_segundo_apellido=sura_segundo_apellido,
                sura_no_documento=sura_no_documento,
                sura_tipo_documento=sura_tipo_documento,
                sura_valor_auto=sura_valor_auto,
                sura_ano_auto=sura_ano_auto,
                sura_marca=sura_marca,
                sura_modelo=sura_modelo
            )
            
            # Crear historial inicial
            if primera_etapa:
                HistorialSolicitud.objects.create(
                    solicitud=solicitud,
                    etapa=primera_etapa,
                    usuario_responsable=request.user,
                    fecha_inicio=timezone.now()
                )
            
            # Crear requisitos automáticamente
            requisitos_pipeline = RequisitoPipeline.objects.filter(
                pipeline=pipeline
            )
            
            for req_pipeline in requisitos_pipeline:
                requisito_solicitud = RequisitoSolicitud.objects.create(
                    solicitud=solicitud,
                    requisito=req_pipeline.requisito
                )
                
                # Verificar si hay archivo subido para este requisito
                archivo_key = f'archivo_requisito_{req_pipeline.requisito.id}'
                if archivo_key in request.FILES:
                    requisito_solicitud.archivo = request.FILES[archivo_key]
                    requisito_solicitud.cumplido = True  # Marcar como cumplido cuando se sube archivo
                    requisito_solicitud.save()
            
            # Guardar campos personalizados
            campos_personalizados = CampoPersonalizado.objects.filter(pipeline=pipeline)
            for campo in campos_personalizados:
                valor = request.POST.get(f'campo_{campo.id}')
                if valor:
                    valor_campo = ValorCampoSolicitud.objects.create(
                        solicitud=solicitud,
                        campo=campo
                    )
                    
                    # Guardar según el tipo de campo
                    if campo.tipo == 'texto':
                        valor_campo.valor_texto = valor
                    elif campo.tipo == 'numero':
                        valor_campo.valor_numero = float(valor) if valor else None
                    elif campo.tipo == 'entero':
                        valor_campo.valor_entero = int(valor) if valor else None
                    elif campo.tipo == 'fecha':
                        from datetime import datetime
                        valor_campo.valor_fecha = datetime.strptime(valor, '%Y-%m-%d').date() if valor else None
                    elif campo.tipo == 'booleano':
                        valor_campo.valor_booleano = valor == 'true'
                    
                    valor_campo.save()
            
            # Send APC email if requested
            if descargar_apc_makito and apc_no_cedula and apc_tipo_documento:
                try:
                    enviar_correo_apc_makito(solicitud, apc_no_cedula, apc_tipo_documento, request)
                except Exception as e:
                    print(f"Error enviando correo APC: {e}")
                    # No detener el proceso por error en correo
            
            # Send SURA email if requested
            if cotizar_sura_makito and sura_primer_nombre and sura_primer_apellido and sura_no_documento:
                enviar_correo_sura_makito(
                    solicitud, 
                    sura_primer_nombre, 
                    sura_primer_apellido, 
                    sura_no_documento,
                    request,
                    # Vehicle data
                    sura_valor_auto=sura_valor_auto,
                    sura_ano_auto=sura_ano_auto,
                    sura_marca=sura_marca,
                    sura_modelo=sura_modelo,
                    sura_tipo_documento=sura_tipo_documento
                )
            
            # Responder con JSON para requests AJAX
            if request.content_type == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'solicitud_id': solicitud.id,
                    'codigo': solicitud.codigo,
                    'message': f'Solicitud {solicitud.codigo} creada exitosamente.'
                })
            
            messages.success(request, f'Solicitud {solicitud.codigo} creada exitosamente.')
            return redirect('workflow:detalle_solicitud', solicitud_id=solicitud.id)
    
    # Obtener clientes y cotizaciones para el formulario
    
    # Obtener clientes del usuario actual o todos si es superuser
    if request.user.is_superuser:
        clientes = Cliente.objects.all().order_by('-created_at')[:100]  # Últimos 100 clientes
    else:
        clientes = Cliente.objects.filter(
            Q(added_by=request.user) | 
            Q(propietario=request.user)
        ).order_by('-created_at')[:100]
    
    # Obtener cotizaciones del usuario actual o todas si es superuser
    if request.user.is_superuser:
        cotizaciones = Cotizacion.objects.all().order_by('-created_at')[:100]  # Últimas 100 cotizaciones
    else:
        cotizaciones = Cotizacion.objects.filter(added_by=request.user).order_by('-created_at')[:100]
    
    context = {
        'pipelines': Pipeline.objects.all(),
        'clientes': clientes,
        'cotizaciones': cotizaciones,
    }
    
    return render(request, 'workflow/nueva_solicitud.html', context)


@login_required
def detalle_solicitud(request, solicitud_id):
    """Detalle de una solicitud específica"""
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar permisos
    if solicitud.asignada_a and solicitud.asignada_a != request.user:
        # Superusers bypass permission checks
        if not (request.user.is_superuser or request.user.is_staff):
            grupos_usuario = request.user.groups.all()
            tiene_permiso = PermisoEtapa.objects.filter(
                etapa=solicitud.etapa_actual,
                grupo__in=grupos_usuario,
                puede_ver=True
            ).exists()
            
            if not tiene_permiso:
                messages.error(request, 'No tienes permisos para ver esta solicitud.')
                return redirect('bandeja_trabajo')
    
    # Obtener transiciones disponibles
    transiciones_disponibles = []
    if solicitud.etapa_actual:
        transiciones = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual
        )
        
        for transicion in transiciones:
            # Verificar requisitos para esta transición
            requisitos_faltantes = verificar_requisitos_transicion(solicitud, transicion)
            
            if not transicion.requiere_permiso:
                transiciones_disponibles.append({
                    'transicion': transicion,
                    'puede_realizar': len(requisitos_faltantes) == 0,
                    'requisitos_faltantes': requisitos_faltantes,
                    'total_requisitos_faltantes': len(requisitos_faltantes)
                })
            else:
                # Verificar si el usuario tiene permisos específicos
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=transicion.etapa_destino,
                    grupo__in=grupos_usuario
                ).exists()
                if tiene_permiso:
                    transiciones_disponibles.append({
                        'transicion': transicion,
                        'puede_realizar': len(requisitos_faltantes) == 0,
                        'requisitos_faltantes': requisitos_faltantes,
                        'total_requisitos_faltantes': len(requisitos_faltantes)
                    })
    
    # Obtener historial
    historial = solicitud.historial.all().order_by('-fecha_inicio')
    
    # Obtener requisitos
    requisitos = solicitud.requisitos.all()
    
    # Obtener campos personalizados
    campos_personalizados = CampoPersonalizado.objects.filter(pipeline=solicitud.pipeline)
    valores_campos = solicitud.valores_personalizados.all()
    
    # Para vista backoffice: obtener archivos requeridos por subestado
    archivos_por_subestado = {}
    if (solicitud.etapa_actual and 
        solicitud.etapa_actual.nombre == "Back Office" and 
        solicitud.etapa_actual.es_bandeja_grupal):
        
        # ✅ CORREGIDO: Obtener solo los requisitos definidos en RequisitoTransicion para Back Office
        # Los documentos para Back Office están definidos en las transiciones DE ENTRADA hacia Back Office
        # (no en las de salida, que son para la siguiente etapa)
        transiciones_entrada = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_destino=solicitud.etapa_actual
        ).prefetch_related('requisitos_obligatorios__requisito')
        
        # Obtener todos los requisitos necesarios (solo de entrada)
        requisitos_necesarios = {}
        
        # Procesar requisitos de transiciones de entrada
        for transicion in transiciones_entrada:
            for req_transicion in transicion.requisitos_obligatorios.all():
                req_id = req_transicion.requisito.id
                if req_id not in requisitos_necesarios:
                    requisitos_necesarios[req_id] = {
                        'requisito': req_transicion.requisito,
                        'obligatorio': req_transicion.obligatorio,
                        'mensaje_personalizado': req_transicion.mensaje_personalizado,
                        'archivo_actual': None,
                        'esta_cumplido': False,
                        'tipo_transicion': 'entrada'
                    }
        
        # Verificar qué archivos ya están subidos (usar RequisitoSolicitud)
        requisitos_solicitud = RequisitoSolicitud.objects.filter(solicitud=solicitud).select_related('requisito')
        for req_sol in requisitos_solicitud:
            req_id = req_sol.requisito_id  # Usar el foreign key directamente
            if req_id in requisitos_necesarios:
                # Obtener calificaciones y comentarios
                from .models import CalificacionDocumentoBackoffice, ComentarioDocumentoBackoffice, OpcionDesplegable
                
                calificaciones = CalificacionDocumentoBackoffice.objects.filter(
                    requisito_solicitud=req_sol
                ).select_related('calificado_por', 'opcion_desplegable').order_by('-fecha_calificacion')
                
                comentarios = ComentarioDocumentoBackoffice.objects.filter(
                    requisito_solicitud=req_sol,
                    activo=True
                ).select_related('comentario_por').order_by('-fecha_comentario')
                
                # 🚨 DEBUG: LÓGICA AUTOMÁTICA CON VALIDACIÓN ESTRICTA (PRIMERA FUNCIÓN)
                print(f"🔍 DEBUG F1 - Solicitud actual: {solicitud.id} ({solicitud.codigo})")
                print(f"🔍 DEBUG F1 - Procesando req_sol: {req_sol.id} - Requisito: {req_sol.requisito.nombre}")
                print(f"🔍 DEBUG F1 - req_sol.solicitud.id: {req_sol.solicitud.id}")
                print(f"🔍 DEBUG F1 - ¿Coincide solicitud?: {req_sol.solicitud.id == solicitud.id}")
                
                # 🛡️ VALIDACIÓN ESTRICTA: Solo procesar si pertenece a la solicitud actual
                if req_sol.solicitud.id != solicitud.id:
                    print(f"❌ ERROR CRÍTICO F1: req_sol pertenece a solicitud {req_sol.solicitud.id} pero estamos en {solicitud.id}")
                    continue  # Saltar este requisito
                
                if not req_sol.archivo:  # Sin archivo
                    print(f"📄 F1 Sin archivo para: {req_sol.requisito.nombre} en solicitud {solicitud.codigo}")
                    # Buscar si ya existe calificación
                    calificacion_existente = CalificacionDocumentoBackoffice.objects.filter(
                        requisito_solicitud=req_sol
                    ).first()
                    
                    # Si no existe, crearla automáticamente como "pendiente"
                    if not calificacion_existente:
                        try:
                            print(f"💾 F1 CREANDO calificación pendiente para:")
                            print(f"   - RequisitoSolicitud ID: {req_sol.id}")
                            print(f"   - Requisito: {req_sol.requisito.nombre}")
                            print(f"   - Solicitud: {req_sol.solicitud.codigo} (ID: {req_sol.solicitud.id})")
                            print(f"   - Usuario: {request.user.username}")
                            
                            CalificacionDocumentoBackoffice.objects.create(
                                requisito_solicitud=req_sol,
                                calificado_por=request.user,
                                estado='pendiente'
                            )
                            print(f"✅ F1 Calificación creada exitosamente")
                            # Recargar calificaciones para incluir la nueva
                            calificaciones = CalificacionDocumentoBackoffice.objects.filter(
                                requisito_solicitud=req_sol
                            ).select_related('calificado_por', 'opcion_desplegable').order_by('-fecha_calificacion')
                        except Exception as e:
                            print(f"❌ F1 Error creando calificación: {e}")

                requisitos_necesarios[req_id]['archivo_actual'] = req_sol
                requisitos_necesarios[req_id]['esta_cumplido'] = req_sol.cumplido and bool(req_sol.archivo)
                requisitos_necesarios[req_id]['calificaciones_backoffice'] = list(calificaciones)
                requisitos_necesarios[req_id]['comentarios_backoffice'] = list(comentarios)
                requisitos_necesarios[req_id]['ultima_calificacion'] = calificaciones.first() if calificaciones.exists() else None
        
        # Asignar archivos a cada subestado (por ahora todos los subestados muestran los mismos archivos)
        for subestado in solicitud.etapa_actual.subestados.all():
            archivos_por_subestado[subestado.id] = list(requisitos_necesarios.values())
    
    # Calcular estadísticas de archivos para el template
    archivos_stats = {}
    if archivos_por_subestado:
        for subestado_id, archivos in archivos_por_subestado.items():
            total_archivos = len(archivos)
            archivos_completos = len([archivo for archivo in archivos if archivo['esta_cumplido']])
            archivos_stats[subestado_id] = {
                'total': total_archivos,
                'completos': archivos_completos,
                'pendientes': total_archivos - archivos_completos,
                'porcentaje': round((archivos_completos / total_archivos * 100) if total_archivos > 0 else 0, 1)
            }
    
    # Obtener opciones de desplegable para calificación
    opciones_desplegable = []
    if archivos_por_subestado:  # Solo si estamos en Back Office
        from .models import OpcionDesplegable
        opciones_desplegable = OpcionDesplegable.objects.filter(activo=True).order_by('orden')
    
    context = {
        'solicitud': solicitud,
        'transiciones_disponibles': transiciones_disponibles,
        'historial': historial,
        'requisitos': requisitos,
        'campos_personalizados': campos_personalizados,
        'valores_campos': valores_campos,
        'archivos_por_subestado': archivos_por_subestado,
        'archivos_stats': archivos_stats,
        'opciones_desplegable': opciones_desplegable,
    }
    
    # Verificar si estamos en la etapa "Back Office" con bandeja grupal
    if (solicitud.etapa_actual and 
        solicitud.etapa_actual.nombre == "Back Office" and 
        solicitud.etapa_actual.es_bandeja_grupal):
        
        # Asegurar que hay un subestado actual asignado
        if not solicitud.subestado_actual and solicitud.etapa_actual.subestados.exists():
            primer_subestado = solicitud.etapa_actual.subestados.order_by('orden').first()
            solicitud.subestado_actual = primer_subestado
            solicitud.save()
            print(f"DEBUG: Asignado primer subestado por defecto: {primer_subestado.nombre}")
        
        # Verificar si se está cambiando de subestado por parámetro GET
        subestado_param = request.GET.get('subestado')
        if subestado_param:
            try:
                nuevo_subestado = solicitud.etapa_actual.subestados.get(nombre=subestado_param)
                solicitud.subestado_actual = nuevo_subestado
                solicitud.save()
                print(f"DEBUG: Cambiado a subestado: {nuevo_subestado.nombre}")
            except:
                print(f"DEBUG: No se pudo cambiar al subestado: {subestado_param}")
        
        # Seleccionar template según el subestado actual
        template_map = {
            'Checklist': 'workflow/detalle_solicitud_backoffice.html',
            'Captura': 'workflow/detalle_solicitud_captura.html', 
            'Firma': 'workflow/detalle_solicitud_firma.html',
            'Orden del expediente': 'workflow/detalle_solicitud_orden.html',
            'Trámite': 'workflow/detalle_solicitud_tramite.html',
            'Subsanación de pendientes Trámite': 'workflow/detalle_solicitud_subsanacion.html'
        }
        
        # PRIMERA FUNCIÓN DETALLE_SOLICITUD - AHORA CON AUTO-CREACIÓN TAMBIÉN
        template_name = template_map.get(
            solicitud.subestado_actual.nombre if solicitud.subestado_actual else 'Checklist',
            'workflow/detalle_solicitud_backoffice.html'
        )
        
        return render(request, template_name, context)
    
    return render(request, 'workflow/detalle_solicitud.html', context)

# FUNCIÓN DUPLICADA CAMBIADA A NOMBRE DIFERENTE 
# def detalle_solicitud → detalle_solicitud_DUPLICADA_DESHABILITADA

@login_required
def transicion_solicitud(request, solicitud_id):
    """Realizar transición de una solicitud"""
    
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        transicion_id = request.POST.get('transicion_id')
        
        if transicion_id:
            transicion = get_object_or_404(TransicionEtapa, id=transicion_id)
            
            # Verificar que la transición es válida
            if transicion.pipeline != solicitud.pipeline or transicion.etapa_origen != solicitud.etapa_actual:
                messages.error(request, 'Transición no válida.')
                return redirect('detalle_solicitud', solicitud_id=solicitud_id)
            
            # Verificar permisos si es necesario
            if transicion.requiere_permiso:
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=transicion.etapa_destino,
                    grupo__in=grupos_usuario
                ).exists()
                if not tiene_permiso:
                    messages.error(request, 'No tienes permisos para realizar esta transición.')
                    return redirect('detalle_solicitud', solicitud_id=solicitud_id)
            
            # Verificar requisitos obligatorios
            requisitos_pendientes = solicitud.requisitos.filter(
                requisito__requisitopipelinetipo__obligatorio=True,
                cumplido=False
            )
            
            if requisitos_pendientes.exists():
                messages.error(request, 'Debes cumplir todos los requisitos obligatorios antes de continuar.')
                return redirect('detalle_solicitud', solicitud_id=solicitud_id)
            
            # Cerrar historial actual
            historial_actual = solicitud.historial.filter(fecha_fin__isnull=True).first()
            if historial_actual:
                historial_actual.fecha_fin = timezone.now()
                historial_actual.save()
            
            # Actualizar solicitud
            solicitud.etapa_actual = transicion.etapa_destino
            solicitud.subestado_actual = None  # Resetear subestado
            solicitud.save()
            
            # Crear nuevo historial
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=transicion.etapa_destino,
                usuario_responsable=request.user,
                fecha_inicio=timezone.now()
            )
            
            messages.success(request, f'Solicitud movida a {transicion.etapa_destino.nombre}')
            return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    return redirect('detalle_solicitud', solicitud_id=solicitud_id)


@login_required
def auto_asignar_solicitud(request, solicitud_id):
    """Auto-asignar una solicitud de bandeja grupal"""
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que la solicitud está en bandeja grupal
    if not solicitud.etapa_actual.es_bandeja_grupal or solicitud.asignada_a:
        messages.error(request, 'Esta solicitud no está disponible para auto-asignación.')
        return redirect('bandeja_trabajo')
    
    # Verificar permisos
    # Superusers bypass permission checks
    if not (request.user.is_superuser or request.user.is_staff):
        grupos_usuario = request.user.groups.all()
        tiene_permiso = PermisoEtapa.objects.filter(
            etapa=solicitud.etapa_actual,
            grupo__in=grupos_usuario,
            puede_autoasignar=True
        ).exists()
        
        if not tiene_permiso:
            messages.error(request, 'No tienes permisos para auto-asignar solicitudes en esta etapa.')
            return redirect('bandeja_trabajo')
    
    # Asignar solicitud
    solicitud.asignada_a = request.user
    solicitud.save()
    
    messages.success(request, f'Solicitud {solicitud.codigo} asignada exitosamente.')
    return redirect('detalle_solicitud', solicitud_id=solicitud_id)


@login_required
def actualizar_requisito(request, solicitud_id, requisito_id):
    """Actualizar estado de un requisito"""
    
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        requisito_solicitud = get_object_or_404(RequisitoSolicitud, id=requisito_id, solicitud=solicitud)
        
        # Verificar permisos
        if solicitud.asignada_a and solicitud.asignada_a != request.user:
            # Superusers bypass permission checks
            if not (request.user.is_superuser or request.user.is_staff):
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=solicitud.etapa_actual,
                    grupo__in=grupos_usuario,
                    puede_ver=True
                ).exists()
                
                if not tiene_permiso:
                    return JsonResponse({'error': 'No tienes permisos para actualizar esta solicitud.'}, status=403)
        
        # Actualizar requisito
        cumplido = request.POST.get('cumplido') == 'true'
        observaciones = request.POST.get('observaciones', '')
        
        requisito_solicitud.cumplido = cumplido
        requisito_solicitud.observaciones = observaciones
        
        # Manejar archivo si se sube
        if 'archivo' in request.FILES:
            requisito_solicitud.archivo = request.FILES['archivo']
        
        requisito_solicitud.save()
        
        return JsonResponse({
            'success': True,
            'cumplido': cumplido,
            'observaciones': observaciones
        })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def actualizar_campo_personalizado(request, solicitud_id):
    """Actualizar campos personalizados de una solicitud"""
    
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if solicitud.asignada_a and solicitud.asignada_a != request.user:
            # Superusers bypass permission checks
            if not (request.user.is_superuser or request.user.is_staff):
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=solicitud.etapa_actual,
                    grupo__in=grupos_usuario,
                    puede_ver=True
                ).exists()
                
                if not tiene_permiso:
                    return JsonResponse({'error': 'No tienes permisos para actualizar esta solicitud.'}, status=403)
        
        campos_personalizados = CampoPersonalizado.objects.filter(pipeline=solicitud.pipeline)
        
        for campo in campos_personalizados:
            valor_campo, created = ValorCampoSolicitud.objects.get_or_create(
                solicitud=solicitud,
                campo=campo
            )
            
            valor = request.POST.get(f'campo_{campo.id}')
            
            if campo.tipo == 'texto':
                valor_campo.valor_texto = valor
            elif campo.tipo == 'numero':
                valor_campo.valor_numero = float(valor) if valor else None
            elif campo.tipo == 'entero':
                valor_campo.valor_entero = int(valor) if valor else None
            elif campo.tipo == 'fecha':
                valor_campo.valor_fecha = datetime.strptime(valor, '%Y-%m-%d').date() if valor else None
            elif campo.tipo == 'booleano':
                valor_campo.valor_booleano = valor == 'true'
            
            valor_campo.save()
        
        messages.success(request, 'Campos personalizados actualizados exitosamente.')
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ==========================================
# VISTAS DE ADMINISTRACIÓN
# ==========================================

@login_required
@superuser_permission_required('workflow.add_pipeline')
def administrar_pipelines(request):
    """Administración de pipelines"""
    
    pipelines = Pipeline.objects.all().prefetch_related('etapas')
    
    context = {
        'pipelines': pipelines,
    }
    
    return render(request, 'workflow/admin/pipelines.html', context)


@login_required
@superuser_permission_required('workflow.add_requisito')
def administrar_requisitos(request):
    """Administración de requisitos"""
    
    requisitos = Requisito.objects.all()
    requisitos_pipeline = RequisitoPipeline.objects.all().select_related('pipeline', 'requisito')
    
    context = {
        'requisitos': requisitos,
        'requisitos_pipeline': requisitos_pipeline,
    }
    
    return render(request, 'workflow/admin/requisitos.html', context)


@login_required
@superuser_permission_required('workflow.add_campopersonalizado')
def administrar_campos_personalizados(request):
    """Administración de campos personalizados"""
    
    campos = CampoPersonalizado.objects.all().select_related('pipeline')
    
    context = {
        'campos': campos,
    }
    
    return render(request, 'workflow/admin/campos_personalizados.html', context)


@login_required
def administrar_usuarios(request):
    """Vista para administrar usuarios y grupos - Solo para administradores"""
    
    # Verificar permisos de administrador
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('workflow:dashboard')
    
    # Obtener usuarios y grupos
    usuarios = User.objects.select_related('userprofile').all().order_by('username')
    grupos = Group.objects.all().order_by('name')
    
    # Estadísticas
    total_usuarios = usuarios.count()
    usuarios_activos = usuarios.filter(is_active=True).count()
    usuarios_inactivos = total_usuarios - usuarios_activos
    total_grupos = grupos.count()
    
    # Usuarios por grupo
    usuarios_por_grupo = {}
    for grupo in grupos:
        usuarios_por_grupo[grupo.name] = grupo.user_set.count()
    
    # Usuarios sin grupos
    usuarios_sin_grupos = usuarios.filter(groups__isnull=True).count()
    
    context = {
        'usuarios': usuarios,
        'grupos': grupos,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
        'total_grupos': total_grupos,
        'usuarios_por_grupo': usuarios_por_grupo,
        'usuarios_sin_grupos': usuarios_sin_grupos,
    }
    
    return render(request, 'workflow/admin/usuarios.html', context)


# ==========================================
# VISTAS DE REPORTES
# ==========================================

@login_required
def reportes_workflow(request):
    """Reportes del sistema de workflow"""
    
    # Estadísticas generales
    total_solicitudes = Solicitud.objects.count()
    solicitudes_activas = Solicitud.objects.filter(etapa_actual__isnull=False).count()
    solicitudes_completadas = Solicitud.objects.filter(etapa_actual__isnull=True).count()
    
    # Solicitudes por pipeline
    solicitudes_por_pipeline = Pipeline.objects.annotate(
        total=Count('solicitud')
    ).values('nombre', 'total')
    
    # Solicitudes vencidas - Calculamos usando Python para compatibilidad con SQLite
    from datetime import timedelta
    solicitudes_vencidas = 0
    for solicitud in Solicitud.objects.filter(etapa_actual__isnull=False).select_related('etapa_actual'):
        if solicitud.etapa_actual and solicitud.etapa_actual.sla:
            fecha_limite = solicitud.fecha_ultima_actualizacion + solicitud.etapa_actual.sla
            if timezone.now() > fecha_limite:
                solicitudes_vencidas += 1
    
    # Tiempo promedio por etapa - Calculamos usando Python para compatibilidad con SQLite
    tiempos_promedio = []
    historiales = HistorialSolicitud.objects.filter(
        fecha_fin__isnull=False
    ).select_related('etapa')
    
    etapas_tiempos = {}
    for historial in historiales:
        etapa_nombre = historial.etapa.nombre
        if etapa_nombre not in etapas_tiempos:
            etapas_tiempos[etapa_nombre] = []
        
        tiempo_horas = (historial.fecha_fin - historial.fecha_inicio).total_seconds() / 3600
        etapas_tiempos[etapa_nombre].append(tiempo_horas)
    
    for etapa_nombre, tiempos in etapas_tiempos.items():
        tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
        tiempos_promedio.append({
            'etapa__nombre': etapa_nombre,
            'tiempo_promedio': tiempo_promedio
        })
    
    context = {
        'total_solicitudes': total_solicitudes,
        'solicitudes_activas': solicitudes_activas,
        'solicitudes_completadas': solicitudes_completadas,
        'solicitudes_vencidas': solicitudes_vencidas,
        'solicitudes_por_pipeline': solicitudes_por_pipeline,
        'tiempos_promedio': tiempos_promedio,
    }
    
    return render(request, 'workflow/reportes.html', context)


# ==========================================
# VISTAS DE CANALES ALTERNOS
# ==========================================

@login_required
def canal_digital(request):
    """Vista principal del Canal Digital"""
    
    # Importar el modelo aquí para evitar problemas de importación circular
    from .models import FormularioWeb
    from .modelsWorkflow import Pipeline, ConfiguracionCanalDigital
    from django.core.paginator import Paginator
    from django.contrib.auth.models import User
    
    # Estadísticas específicas del canal digital
    solicitudes_canal_digital = FormularioWeb.objects.count()
    solicitudes_procesadas = FormularioWeb.objects.filter(procesado=True).count()
    solicitudes_pendientes = FormularioWeb.objects.filter(procesado=False).count()
    
    # Obtener todas las solicitudes para la tabla (ordenadas por fecha más reciente)
    formularios_queryset = FormularioWeb.objects.order_by('-fecha_creacion')
    
    # Paginación
    paginator = Paginator(formularios_queryset, 25)  # 25 formularios por página
    page_number = request.GET.get('page')
    formularios_page = paginator.get_page(page_number)
    
    # Preparar datos para la tabla
    formularios_tabla = []
    for formulario in formularios_page:
        formularios_tabla.append({
            'id': formulario.id,
            'nombre_completo': formulario.get_nombre_completo(),
            'cedula': formulario.cedulaCliente,
            'celular': formulario.celular,
            'correo': formulario.correo_electronico,
            'producto_interesado': formulario.producto_interesado or 'No especificado',
            'monto_solicitar': f"${formulario.dinero_a_solicitar:,.2f}" if formulario.dinero_a_solicitar else 'N/A',
            'fecha_creacion': formulario.fecha_creacion,
            'procesado': formulario.procesado,
            'ip_address': formulario.ip_address,
            'propietario': getattr(formulario, 'propietario', None),
            'propietario_nombre': formulario.propietario.get_full_name() if getattr(formulario, 'propietario', None) else None,
        })
    
    # Obtener configuración del Canal Digital
    configuracion = ConfiguracionCanalDigital.get_configuracion_activa()
    pipeline_por_defecto = ConfiguracionCanalDigital.get_pipeline_por_defecto()
    etapa_por_defecto = ConfiguracionCanalDigital.get_etapa_por_defecto()
    
    # Obtener todos los pipelines disponibles
    pipelines_disponibles = Pipeline.objects.all()
    
    # Obtener usuarios del grupo "Canal Digital" para el selector de propietarios
    from django.contrib.auth.models import Group
    try:
        grupo_canal_digital = Group.objects.get(name="Canal Digital")
        usuarios_canal_digital = grupo_canal_digital.user_set.filter(is_active=True).order_by('first_name', 'last_name', 'username')
    except Group.DoesNotExist:
        usuarios_canal_digital = User.objects.none()
    
    # Para superusers: obtener información para la gestión de usuarios
    gestion_usuarios = None
    
    if request.user.is_superuser:
        # Obtener o crear el grupo "Canal Digital"
        grupo_canal_digital, created = Group.objects.get_or_create(name="Canal Digital")
        
        # Usuarios que están en el grupo
        usuarios_en_grupo = grupo_canal_digital.user_set.filter(is_active=True).order_by('first_name', 'last_name', 'username')
        
        # Usuarios que NO están en el grupo (candidatos para agregar)
        usuarios_disponibles_para_agregar = User.objects.filter(
            is_active=True
        ).exclude(
            groups=grupo_canal_digital
        ).order_by('first_name', 'last_name', 'username')
        
        # Estadísticas del grupo
        total_usuarios_grupo = usuarios_en_grupo.count()
        total_usuarios_disponibles = usuarios_disponibles_para_agregar.count()
        
        gestion_usuarios = {
            'grupo': grupo_canal_digital,
            'usuarios_en_grupo': usuarios_en_grupo,
            'usuarios_disponibles_para_agregar': usuarios_disponibles_para_agregar,
            'total_usuarios_grupo': total_usuarios_grupo,
            'total_usuarios_disponibles': total_usuarios_disponibles,
        }
        
        # Asegurar que usuarios_canal_digital use los usuarios del grupo para superusers
        usuarios_canal_digital = usuarios_en_grupo
    else:
        # Para usuarios no-superuser, seguir usando el filtro del grupo
        try:
            grupo_canal_digital = Group.objects.get(name="Canal Digital")
            usuarios_canal_digital = grupo_canal_digital.user_set.filter(is_active=True).order_by('first_name', 'last_name', 'username')
        except Group.DoesNotExist:
            usuarios_canal_digital = User.objects.none()
    
    # KPIs del canal digital
    context = {
        'solicitudes_canal_digital': solicitudes_canal_digital,
        'solicitudes_procesadas': solicitudes_procesadas,
        'solicitudes_pendientes': solicitudes_pendientes,
        'formularios_tabla': formularios_tabla,
        'formularios_page': formularios_page,
        'usuarios_disponibles': usuarios_canal_digital,  # Solo usuarios del grupo "Canal Digital"
        'gestion_usuarios': gestion_usuarios,  # Información para gestión de usuarios (solo superusers)
        'titulo': 'Canal Digital',
        'subtitulo': 'Gestión de solicitudes del canal digital',
        'configuracion': configuracion,
        'pipeline_por_defecto': pipeline_por_defecto,
        'etapa_por_defecto': etapa_por_defecto,
        'pipelines_disponibles': pipelines_disponibles,
    }
    
    return render(request, 'workflow/canal_digital.html', context)


@csrf_exempt
@login_required
def convertir_formulario_a_solicitud(request):
    """Convierte un FormularioWeb en una Solicitud del workflow"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        from .models import FormularioWeb
        from .modelsWorkflow import Pipeline, Etapa, Solicitud, HistorialSolicitud, ConfiguracionCanalDigital
        from pacifico.models import Cliente
        import json
        
        data = json.loads(request.body)
        formulario_id = data.get('formulario_id')
        pipeline_id = data.get('pipeline_id')
        etapa_id = data.get('etapa_id')
        
        if not formulario_id:
            return JsonResponse({'success': False, 'error': 'ID de formulario requerido'})
        
        # Obtener el formulario
        formulario = get_object_or_404(FormularioWeb, id=formulario_id)
        
        if formulario.procesado:
            return JsonResponse({'success': False, 'error': 'Este formulario ya ha sido procesado'})
        
        # Determinar pipeline y etapa
        if pipeline_id:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        else:
            # Usar configuración por defecto
            pipeline = ConfiguracionCanalDigital.get_pipeline_por_defecto()
            if not pipeline:
                return JsonResponse({'success': False, 'error': 'No hay pipeline configurado por defecto'})
        
        if etapa_id:
            etapa = get_object_or_404(Etapa, id=etapa_id, pipeline=pipeline)
        else:
            # Usar configuración por defecto
            etapa = ConfiguracionCanalDigital.get_etapa_por_defecto()
            if not etapa or etapa.pipeline != pipeline:
                # Buscar primera etapa del pipeline
                etapa = pipeline.etapas.first()
                if not etapa:
                    return JsonResponse({'success': False, 'error': f'No hay etapas configuradas en el pipeline {pipeline.nombre}'})
        
        # Buscar o crear cliente basado en la cédula
        cliente = None
        if formulario.cedulaCliente:
            try:
                cliente = Cliente.objects.filter(cedula=formulario.cedulaCliente).first()
            except:
                pass
        
        # Crear la solicitud
        import uuid
        codigo = f"{pipeline.nombre[:3].upper()}-{uuid.uuid4().hex[:8].upper()}"
        
        solicitud = Solicitud()
        solicitud.codigo = codigo
        solicitud.pipeline = pipeline
        solicitud.etapa_actual = etapa
        # Asignar datos del formulario directamente a los campos del modelo
        solicitud.cliente_nombre = formulario.get_nombre_completo()
        solicitud.cliente_cedula = formulario.cedulaCliente
        solicitud.cliente_telefono = formulario.celular
        solicitud.cliente_email = formulario.correo_electronico
        solicitud.producto_solicitado = formulario.producto_interesado
        solicitud.monto_solicitado = formulario.dinero_a_solicitar or 0
        # NO asignar propietario - las solicitudes del Canal Digital llegan sin propietario
        solicitud.propietario = None
        solicitud.creada_por = request.user
        solicitud.cliente = cliente
        solicitud.origen = 'Canal Digital'  # Etiqueta distintiva
        solicitud.observaciones = f"Solicitud creada desde Canal Digital - IP: {formulario.ip_address}"
        solicitud.save()
        
        # Crear historial inicial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=etapa,
            usuario_responsable=request.user
        )
        
        # Marcar formulario como procesado
        formulario.procesado = True
        formulario.save()
        
        return JsonResponse({
            'success': True, 
            'mensaje': f'Solicitud {solicitud.codigo} creada exitosamente en {pipeline.nombre} - {etapa.nombre}',
            'solicitud_id': solicitud.id,
            'solicitud_codigo': solicitud.codigo,
            'pipeline_nombre': pipeline.nombre,
            'etapa_nombre': etapa.nombre
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@login_required
def procesar_formularios_masivo(request):
    """Convierte múltiples FormularioWeb en Solicitudes del workflow"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        from .models import FormularioWeb
        from .modelsWorkflow import Pipeline, Etapa, Solicitud, HistorialSolicitud, ConfiguracionCanalDigital
        from pacifico.models import Cliente
        import json
        
        data = json.loads(request.body)
        formulario_ids = data.get('formulario_ids', [])
        pipeline_id = data.get('pipeline_id')
        etapa_id = data.get('etapa_id')
        
        if not formulario_ids:
            return JsonResponse({'success': False, 'error': 'No se seleccionaron formularios'})
        
        # Determinar pipeline y etapa
        if pipeline_id:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        else:
            # Usar configuración por defecto
            pipeline = ConfiguracionCanalDigital.get_pipeline_por_defecto()
            if not pipeline:
                return JsonResponse({'success': False, 'error': 'No hay pipeline configurado por defecto'})
        
        if etapa_id:
            etapa = get_object_or_404(Etapa, id=etapa_id, pipeline=pipeline)
        else:
            # Usar configuración por defecto
            etapa = ConfiguracionCanalDigital.get_etapa_por_defecto()
            if not etapa or etapa.pipeline != pipeline:
                # Buscar primera etapa del pipeline
                etapa = pipeline.etapas.first()
                if not etapa:
                    return JsonResponse({'success': False, 'error': f'No hay etapas configuradas en el pipeline {pipeline.nombre}'})
        
        formularios = FormularioWeb.objects.filter(id__in=formulario_ids, procesado=False)
        solicitudes_creadas = []
        errores = []
        
        for formulario in formularios:
            try:
                # Buscar cliente
                cliente = None
                if formulario.cedulaCliente:
                    try:
                        cliente = Cliente.objects.filter(cedula=formulario.cedulaCliente).first()
                    except:
                        pass
                
                # Crear la solicitud
                solicitud = Solicitud.objects.create(
                    pipeline=pipeline,
                    etapa_actual=etapa,
                    cliente_nombre=formulario.get_nombre_completo(),
                    cliente_cedula=formulario.cedulaCliente,
                    cliente_telefono=formulario.celular,
                    cliente_email=formulario.correo_electronico,
                    producto_solicitado=formulario.producto_interesado,
                    monto_solicitado=formulario.dinero_a_solicitar or 0,
                    # NO asignar propietario - las solicitudes del Canal Digital llegan sin propietario
                    propietario=None,
                    cliente=cliente,
                    origen='Canal Digital',
                    observaciones=f"Solicitud creada desde formulario web del Canal Digital (ID: {formulario.id})"
                )
                
                # Crear historial inicial
                HistorialSolicitud.objects.create(
                    solicitud=solicitud,
                    etapa_anterior=None,
                    etapa_nueva=etapa,
                    usuario=request.user,
                    observaciones=f"Solicitud creada desde formulario web del Canal Digital (ID: {formulario.id})",
                    es_automatico=True
                )
                
                # Marcar formulario como procesado
                formulario.procesado = True
                formulario.save()
                
                solicitudes_creadas.append({
                    'formulario_id': formulario.id,
                    'solicitud_codigo': solicitud.codigo,
                    'solicitud_id': solicitud.id
                })
                
            except Exception as e:
                errores.append({
                    'formulario_id': formulario.id,
                    'nombre': formulario.get_nombre_completo(),
                    'error': str(e)
                })
        
        return JsonResponse({
            'success': True,
            'solicitudes_creadas': len(solicitudes_creadas),
            'errores': len(errores),
            'detalle_solicitudes': solicitudes_creadas,
            'detalle_errores': errores,
            'pipeline_nombre': pipeline.nombre,
            'etapa_nombre': etapa.nombre
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def formulario_web(request):
    """Vista para el formulario web del canal digital - Crea solicitud automáticamente"""
    
    if request.method == 'POST':
        from .forms import FormularioWebForm
        form = FormularioWebForm(request.POST)
        
        if form.is_valid():
            # Guardar el formulario
            formulario = form.save(commit=False)
            
            # Agregar información adicional
            if request.META.get('HTTP_X_FORWARDED_FOR'):
                formulario.ip_address = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
            else:
                formulario.ip_address = request.META.get('REMOTE_ADDR')
            
            formulario.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limitar tamaño
            formulario.save()
            
            # CREAR SOLICITUD AUTOMÁTICAMENTE
            try:
                from .modelsWorkflow import Pipeline, Etapa, Solicitud, HistorialSolicitud, ConfiguracionCanalDigital
                from pacifico.models import Cliente
                from django.contrib.auth.models import User
                
                # Usar configuración del Canal Digital
                pipeline = ConfiguracionCanalDigital.get_pipeline_por_defecto()
                etapa = ConfiguracionCanalDigital.get_etapa_por_defecto()
                
                if not pipeline:
                    # Fallback al primer pipeline disponible
                    pipeline = Pipeline.objects.first()
                
                if pipeline:
                    # Si no hay etapa configurada o no pertenece al pipeline, usar la primera
                    if not etapa or etapa.pipeline != pipeline:
                        etapa = pipeline.etapas.first()
                    
                    if etapa:
                        # Buscar o crear cliente basado en la cédula
                        cliente = None
                        if formulario.cedulaCliente:
                            try:
                                cliente = Cliente.objects.filter(cedula=formulario.cedulaCliente).first()
                            except:
                                pass
                        
                        # Obtener usuario del sistema para crear la solicitud (primer superuser disponible)
                        usuario_sistema = User.objects.filter(is_superuser=True).first()
                        if not usuario_sistema:
                            usuario_sistema = User.objects.first()  # Fallback
                        
                        # Crear la solicitud automáticamente
                        import uuid
                        codigo = f"{pipeline.nombre[:3].upper()}-{uuid.uuid4().hex[:8].upper()}"
                        
                        solicitud = Solicitud()
                        solicitud.codigo = codigo
                        solicitud.pipeline = pipeline
                        solicitud.etapa_actual = etapa
                        # Asignar datos del formulario directamente a los campos del modelo
                        solicitud.cliente_nombre = formulario.get_nombre_completo()
                        solicitud.cliente_cedula = formulario.cedulaCliente
                        solicitud.cliente_telefono = formulario.celular
                        solicitud.cliente_email = formulario.correo_electronico
                        
                        # Convertir el producto antes de guardarlo
                        producto_original = formulario.producto_interesado
                        if producto_original == 'Préstamos personal':
                            solicitud.producto_solicitado = 'Personal'
                        elif producto_original == 'Préstamo de auto':
                            solicitud.producto_solicitado = 'Auto'
                        else:
                            solicitud.producto_solicitado = producto_original
                            
                        solicitud.monto_solicitado = formulario.dinero_a_solicitar or 0
                        # NO asignar propietario - las solicitudes del Canal Digital llegan sin propietario
                        solicitud.propietario = None
                        solicitud.creada_por = usuario_sistema
                        solicitud.cliente = cliente
                        solicitud.origen = 'Canal Digital'  # Etiqueta distintiva
                        solicitud.observaciones = f"Solicitud creada automáticamente desde Canal Digital - IP: {formulario.ip_address}"
                        solicitud.save()
                        
                        # Crear historial inicial
                        HistorialSolicitud.objects.create(
                            solicitud=solicitud,
                            etapa=etapa,
                            usuario_responsable=usuario_sistema
                        )
                        
                        # Marcar formulario como procesado
                        formulario.procesado = True
                        formulario.save()
                        
                        print(f"✅ Solicitud {solicitud.codigo} creada automáticamente desde Canal Digital")
                        
            except Exception as e:
                # Si hay error creando la solicitud, continuar pero logear el error
                print(f"❌ Error creando solicitud automática: {str(e)}")
                # El formulario se guarda de todas formas
            
            # Redirigir a página de éxito
            return redirect('https://fpacifico.com/prestamos/')
        else:
            # Si hay errores, mostrar el formulario con errores
            context = {
                'form': form,
                'error_message': True,
            }
            return render(request, 'workflow/formulario_web.html', context)
    else:
        # GET request - mostrar formulario vacío
        from .forms import FormularioWebForm
        form = FormularioWebForm()
        
        context = {
            'form': form,
            'error_message': False,
        }
        return render(request, 'workflow/formulario_web.html', context)


# ==========================================
# VISTAS DE API PARA PIPELINES
# ==========================================

@login_required
@superuser_permission_required('workflow.add_pipeline')
def api_crear_pipeline(request):
    """API para crear un nuevo pipeline"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            pipeline = Pipeline.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            
            return JsonResponse({
                'success': True,
                'pipeline': {
                    'id': pipeline.id,
                    'nombre': pipeline.nombre,
                    'descripcion': pipeline.descripcion
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.change_pipeline')
def api_editar_pipeline(request, pipeline_id):
    """API para editar un pipeline"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            pipeline.nombre = nombre
            pipeline.descripcion = descripcion
            pipeline.save()
            
            return JsonResponse({
                'success': True,
                'pipeline': {
                    'id': pipeline.id,
                    'nombre': pipeline.nombre,
                    'descripcion': pipeline.descripcion
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.delete_pipeline')
def api_eliminar_pipeline(request, pipeline_id):
    """API para eliminar un pipeline"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            # Verificar que no hay solicitudes activas
            if pipeline.solicitud_set.exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar un pipeline con solicitudes activas'
                })
            
            pipeline.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_etapa')
def api_obtener_etapas(request, pipeline_id):
    """API para obtener etapas de un pipeline"""
    try:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        etapas = pipeline.etapas.all().order_by('orden')
        
        datos_etapas = []
        for etapa in etapas:
            datos_etapas.append({
                'id': etapa.id,
                'nombre': etapa.nombre,
                'orden': etapa.orden,
                'sla': str(etapa.sla),
                'es_bandeja_grupal': etapa.es_bandeja_grupal,
                'subestados': list(etapa.subestados.values('id', 'nombre', 'orden')),
                'permisos': list(etapa.permisos.values('grupo__name', 'puede_ver', 'puede_autoasignar'))
            })
        
        return JsonResponse({
            'success': True,
            'pipeline_nombre': pipeline.nombre,
            'etapas': datos_etapas
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@superuser_permission_required('workflow.add_etapa')
def api_crear_etapa(request, pipeline_id):
    """API para crear una nueva etapa"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            nombre = request.POST.get('nombre')
            orden = request.POST.get('orden')
            sla_horas = request.POST.get('sla_horas', 24)
            es_bandeja_grupal = request.POST.get('es_bandeja_grupal') == 'true'
            
            if not nombre or not orden:
                return JsonResponse({'success': False, 'error': 'Nombre y orden son obligatorios'})
            
            # Convertir SLA a timedelta
            sla = timedelta(hours=int(sla_horas))
            
            etapa = Etapa.objects.create(
                pipeline=pipeline,
                nombre=nombre,
                orden=int(orden),
                sla=sla,
                es_bandeja_grupal=es_bandeja_grupal
            )
            
            return JsonResponse({
                'success': True,
                'etapa': {
                    'id': etapa.id,
                    'nombre': etapa.nombre,
                    'orden': etapa.orden,
                    'sla': str(etapa.sla),
                    'es_bandeja_grupal': etapa.es_bandeja_grupal
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.change_etapa')
def api_editar_etapa(request, etapa_id):
    """API para editar una etapa"""
    if request.method == 'POST':
        try:
            etapa = get_object_or_404(Etapa, id=etapa_id)
            
            nombre = request.POST.get('nombre')
            orden = request.POST.get('orden')
            sla_horas = request.POST.get('sla_horas', 24)
            es_bandeja_grupal = request.POST.get('es_bandeja_grupal') == 'true'
            
            if not nombre or not orden:
                return JsonResponse({'success': False, 'error': 'Nombre y orden son obligatorios'})
            
            # Convertir SLA a timedelta
            sla = timedelta(hours=int(sla_horas))
            
            etapa.nombre = nombre
            etapa.orden = int(orden)
            etapa.sla = sla
            etapa.es_bandeja_grupal = es_bandeja_grupal
            etapa.save()
            
            return JsonResponse({
                'success': True,
                'etapa': {
                    'id': etapa.id,
                    'nombre': etapa.nombre,
                    'orden': etapa.orden,
                    'sla': str(etapa.sla),
                    'es_bandeja_grupal': etapa.es_bandeja_grupal
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.delete_etapa')
def api_eliminar_etapa(request, etapa_id):
    """API para eliminar una etapa"""
    if request.method == 'POST':
        try:
            etapa = get_object_or_404(Etapa, id=etapa_id)
            
            # Verificar que no hay solicitudes en esta etapa
            if etapa.solicitud_set.exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar una etapa con solicitudes activas'
                })
            
            etapa.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_subestado')
def api_crear_subestado(request, etapa_id):
    """API para crear un subestado"""
    if request.method == 'POST':
        try:
            etapa = get_object_or_404(Etapa, id=etapa_id)
            
            nombre = request.POST.get('nombre')
            orden = request.POST.get('orden', 0)
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            subestado = SubEstado.objects.create(
                etapa=etapa,
                pipeline=etapa.pipeline,
                nombre=nombre,
                orden=int(orden)
            )
            
            return JsonResponse({
                'success': True,
                'subestado': {
                    'id': subestado.id,
                    'nombre': subestado.nombre,
                    'orden': subestado.orden
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_transicionetapa')
def api_crear_transicion(request, pipeline_id):
    """API para crear una transición"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            etapa_origen_id = request.POST.get('etapa_origen')
            etapa_destino_id = request.POST.get('etapa_destino')
            nombre = request.POST.get('nombre')
            requiere_permiso = request.POST.get('requiere_permiso') == 'true'
            
            if not all([etapa_origen_id, etapa_destino_id, nombre]):
                return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios'})
            
            etapa_origen = get_object_or_404(Etapa, id=etapa_origen_id, pipeline=pipeline)
            etapa_destino = get_object_or_404(Etapa, id=etapa_destino_id, pipeline=pipeline)
            
            transicion = TransicionEtapa.objects.create(
                pipeline=pipeline,
                etapa_origen=etapa_origen,
                etapa_destino=etapa_destino,
                nombre=nombre,
                requiere_permiso=requiere_permiso
            )
            
            return JsonResponse({
                'success': True,
                'transicion': {
                    'id': transicion.id,
                    'nombre': transicion.nombre,
                    'etapa_origen': transicion.etapa_origen.nombre,
                    'etapa_destino': transicion.etapa_destino.nombre,
                    'requiere_permiso': transicion.requiere_permiso
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_requisito')
def api_crear_requisito(request):
    """API para crear un requisito"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            requisito = Requisito.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            
            return JsonResponse({
                'success': True,
                'requisito': {
                    'id': requisito.id,
                    'nombre': requisito.nombre,
                    'descripcion': requisito.descripcion
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_requisitopipeline')
def api_asignar_requisito_pipeline(request, pipeline_id):
    """API para asignar un requisito a un pipeline"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            requisito_id = request.POST.get('requisito_id')
            obligatorio = request.POST.get('obligatorio') == 'true'
            
            if not requisito_id:
                return JsonResponse({'success': False, 'error': 'El requisito es obligatorio'})
            
            requisito = get_object_or_404(Requisito, id=requisito_id)
            
            requisito_pipeline, created = RequisitoPipeline.objects.get_or_create(
                pipeline=pipeline,
                requisito=requisito,
                defaults={'obligatorio': obligatorio}
            )
            
            if not created:
                requisito_pipeline.obligatorio = obligatorio
                requisito_pipeline.save()
            
            return JsonResponse({
                'success': True,
                'requisito_pipeline': {
                    'id': requisito_pipeline.id,
                    'requisito_nombre': requisito.nombre,
                    'obligatorio': requisito_pipeline.obligatorio
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_campopersonalizado')
def api_crear_campo_personalizado(request, pipeline_id):
    """API para crear un campo personalizado"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            requerido = request.POST.get('requerido') == 'true'
            
            if not all([nombre, tipo]):
                return JsonResponse({'success': False, 'error': 'Nombre y tipo son obligatorios'})
            
            campo = CampoPersonalizado.objects.create(
                pipeline=pipeline,
                nombre=nombre,
                tipo=tipo,
                requerido=requerido
            )
            
            return JsonResponse({
                'success': True,
                'campo': {
                    'id': campo.id,
                    'nombre': campo.nombre,
                    'tipo': campo.tipo,
                    'requerido': campo.requerido
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.delete_transicionetapa')
def api_eliminar_transicion(request, transicion_id):
    """API para eliminar una transición"""
    if request.method == 'POST':
        try:
            transicion = get_object_or_404(TransicionEtapa, id=transicion_id)
            
            # Verificar que no hay solicitudes usando esta transición
            if transicion.solicitud_set.exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar una transición que está siendo utilizada'
                })
            
            transicion.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.change_transicionetapa')
def api_editar_transicion(request, transicion_id):
    """API para editar una transición"""
    if request.method == 'POST':
        try:
            transicion = get_object_or_404(TransicionEtapa, id=transicion_id)
            
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            etapa_origen_id = request.POST.get('etapa_origen')
            etapa_destino_id = request.POST.get('etapa_destino')
            
            # Validaciones
            if not nombre or not etapa_origen_id or not etapa_destino_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'Todos los campos son obligatorios'
                })
            
            if etapa_origen_id == etapa_destino_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'El origen y destino no pueden ser la misma etapa'
                })
            
            # Verificar que las etapas existen y pertenecen al mismo pipeline
            try:
                etapa_origen = Etapa.objects.get(id=etapa_origen_id, pipeline=transicion.pipeline)
                etapa_destino = Etapa.objects.get(id=etapa_destino_id, pipeline=transicion.pipeline)
            except Etapa.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'error': 'Una o ambas etapas no existen o no pertenecen al pipeline'
                })
            
            # Verificar que no hay otra transición con el mismo origen y destino
            transicion_existente = TransicionEtapa.objects.filter(
                pipeline=transicion.pipeline,
                etapa_origen=etapa_origen,
                etapa_destino=etapa_destino
            ).exclude(id=transicion_id).first()
            
            if transicion_existente:
                return JsonResponse({
                    'success': False, 
                    'error': 'Ya existe una transición entre estas etapas'
                })
            
            # Actualizar la transición
            transicion.nombre = nombre
            transicion.etapa_origen = etapa_origen
            transicion.etapa_destino = etapa_destino
            transicion.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.delete_requisitopipeline')
def api_eliminar_requisito_pipeline(request, requisito_pipeline_id):
    """API para eliminar un requisito de un pipeline"""
    if request.method == 'POST':
        try:
            requisito_pipeline = get_object_or_404(RequisitoPipeline, id=requisito_pipeline_id)
            
            # Verificar que no hay solicitudes con este requisito
            if RequisitoSolicitud.objects.filter(requisito_pipeline=requisito_pipeline).exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar un requisito que está siendo utilizado'
                })
            
            requisito_pipeline.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.change_requisitopipeline')
def api_editar_requisito_pipeline(request, requisito_pipeline_id):
    """API para editar un requisito de un pipeline"""
    if request.method == 'POST':
        try:
            requisito_pipeline = get_object_or_404(RequisitoPipeline, id=requisito_pipeline_id)
            
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            obligatorio = request.POST.get('obligatorio') == 'on'
            
            # Validaciones
            if not nombre:
                return JsonResponse({
                    'success': False, 
                    'error': 'El nombre es obligatorio'
                })
            
            # Actualizar el requisito base
            requisito = requisito_pipeline.requisito
            requisito.nombre = nombre
            requisito.descripcion = descripcion
            requisito.save()
            
            # Actualizar el requisito del pipeline
            requisito_pipeline.obligatorio = obligatorio
            requisito_pipeline.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.delete_campopersonalizado')
def api_eliminar_campo_personalizado(request, campo_id):
    """API para eliminar un campo personalizado"""
    if request.method == 'POST':
        try:
            campo = get_object_or_404(CampoPersonalizado, id=campo_id)
            
            # Verificar que no hay solicitudes con este campo
            if campo.valorcampopersonalizado_set.exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar un campo que está siendo utilizado'
                })
            
            campo.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_obtener_datos_pipeline(request, pipeline_id):
    """API para obtener todos los datos de un pipeline"""
    try:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        
        # Etapas
        etapas = pipeline.etapas.all().order_by('orden')
        datos_etapas = []
        for etapa in etapas:
            datos_etapas.append({
                'id': etapa.id,
                'nombre': etapa.nombre,
                'orden': etapa.orden,
                'sla': str(etapa.sla),
                'es_bandeja_grupal': etapa.es_bandeja_grupal,
                'subestados': list(etapa.subestados.values('id', 'nombre', 'orden')),
                'permisos': list(etapa.permisos.values('grupo__name', 'puede_ver', 'puede_autoasignar'))
            })
        
        # Transiciones
        transiciones = pipeline.transiciones.all()
        datos_transiciones = []
        for transicion in transiciones:
            datos_transiciones.append({
                'id': transicion.id,
                'nombre': transicion.nombre,
                'etapa_origen': transicion.etapa_origen.nombre,
                'etapa_destino': transicion.etapa_destino.nombre,
                'etapa_origen_id': transicion.etapa_origen.id,
                'etapa_destino_id': transicion.etapa_destino.id,
                'requiere_permiso': transicion.requiere_permiso
            })
        
        # Requisitos
        requisitos_pipeline = pipeline.requisitos_pipeline.all().select_related('requisito')
        datos_requisitos = []
        for req_pipeline in requisitos_pipeline:
            datos_requisitos.append({
                'id': req_pipeline.id,
                'requisito_nombre': req_pipeline.requisito.nombre,
                'requisito_descripcion': req_pipeline.requisito.descripcion or '',
                'obligatorio': req_pipeline.obligatorio
            })
        
        # Campos personalizados
        campos = pipeline.campos_personalizados.all()
        datos_campos = []
        for campo in campos:
            datos_campos.append({
                'id': campo.id,
                'nombre': campo.nombre,
                'tipo': campo.tipo,
                'requerido': campo.requerido
            })
        
        return JsonResponse({
            'success': True,
            'pipeline': {
                'id': pipeline.id,
                'nombre': pipeline.nombre,
                'descripcion': pipeline.descripcion
            },
            'etapas': datos_etapas,
            'transiciones': datos_transiciones,
            'requisitos': datos_requisitos,
            'campos_personalizados': datos_campos
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==========================================
# VISTAS DE API
# ==========================================

def api_solicitudes(request):
    """API para obtener solicitudes"""
    
    solicitudes = Solicitud.objects.all().select_related(
        'pipeline', 'etapa_actual', 'subestado_actual', 'creada_por', 'asignada_a',
        'cliente', 'cotizacion'
    )
    
    # Filtro por ID específico (para obtener una solicitud)
    solicitud_id = request.GET.get('id')
    if solicitud_id:
        solicitudes = solicitudes.filter(id=solicitud_id)
    
    # Filtros
    pipeline_id = request.GET.get('pipeline')
    if pipeline_id:
        solicitudes = solicitudes.filter(pipeline_id=pipeline_id)
    
    estado = request.GET.get('estado')
    if estado == 'activas':
        solicitudes = solicitudes.filter(etapa_actual__isnull=False)
    elif estado == 'completadas':
        solicitudes = solicitudes.filter(etapa_actual__isnull=True)
    
    # Serializar datos
    datos = []
    for solicitud in solicitudes:
        # Obtener nombre del cliente de diferentes fuentes
        cliente_nombre = 'N/A'
        cedula_cliente = ''
        
        if solicitud.cliente:
            cliente_nombre = f"{solicitud.cliente.nombre} {solicitud.cliente.apellido}".strip()
            cedula_cliente = solicitud.cliente.cedula or ''
        elif solicitud.cotizacion and hasattr(solicitud.cotizacion, 'cliente') and solicitud.cotizacion.cliente:
            cliente_nombre = f"{solicitud.cotizacion.cliente.nombre} {solicitud.cotizacion.cliente.apellido}".strip()
            cedula_cliente = solicitud.cotizacion.cliente.cedula or ''
        elif solicitud.apc_no_cedula:
            # Fallback para solicitudes APC sin cliente asociado
            cliente_nombre = 'Cliente APC'
            cedula_cliente = solicitud.apc_no_cedula
        elif hasattr(solicitud, 'sura_no_documento') and solicitud.sura_no_documento:
            # Fallback para solicitudes SURA sin cliente asociado  
            cliente_nombre = 'Cliente SURA'
            cedula_cliente = solicitud.sura_no_documento
        
        # Datos de cotización si existe
        cotizacion_data = {}
        if solicitud.cotizacion:
            cotizacion_data = {
                'marca': getattr(solicitud.cotizacion, 'marca', ''),
                'modelo': getattr(solicitud.cotizacion, 'modelo', ''),
                'yearCarro': getattr(solicitud.cotizacion, 'year', ''),
                'valorAuto': getattr(solicitud.cotizacion, 'valor_vehiculo', ''),
                'placa': getattr(solicitud.cotizacion, 'placa', ''),
            }
        
        datos.append({
            'id': solicitud.id,
            'codigo': solicitud.codigo,
            'pipeline': solicitud.pipeline.nombre,
            'pipeline_id': solicitud.pipeline.id,
            'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Completada',
            'etapa_actual_id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
            'subestado_actual': solicitud.subestado_actual.nombre if solicitud.subestado_actual else None,
            'creada_por': solicitud.creada_por.username,
            'asignada_a': solicitud.asignada_a.username if solicitud.asignada_a else None,
            'fecha_creacion': solicitud.fecha_creacion.isoformat(),
            'fecha_ultima_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
            
            # Información del cliente
            'cliente_nombre': cliente_nombre,
            'nombreCliente': cliente_nombre,  # Alias para compatibilidad
            'cedulaCliente': cedula_cliente,
            'apc_no_cedula': solicitud.apc_no_cedula or '',
            'apc_tipo_documento': solicitud.apc_tipo_documento or '',
            'apc_status': solicitud.apc_status or '',
            
            # Status fields for all services
            'sura_status': solicitud.sura_status or '',
            'debida_diligencia_status': solicitud.debida_diligencia_status or '',
            
            # Información de cotización
            **cotizacion_data,
        })
    
    return JsonResponse({'solicitudes': datos})


def api_estadisticas(request):
    """API para obtener estadísticas"""
    
    # Estadísticas básicas
    total_solicitudes = Solicitud.objects.count()
    solicitudes_activas = Solicitud.objects.filter(etapa_actual__isnull=False).count()
    solicitudes_completadas = Solicitud.objects.filter(etapa_actual__isnull=True).count()
    
    # Solicitudes por pipeline
    solicitudes_por_pipeline = Pipeline.objects.annotate(
        total=Count('solicitud')
    ).values('nombre', 'total')
    
    # Solicitudes vencidas - Calculamos usando Python para compatibilidad con SQLite
    solicitudes_vencidas = 0
    for solicitud in Solicitud.objects.filter(etapa_actual__isnull=False).select_related('etapa_actual'):
        if solicitud.etapa_actual and solicitud.etapa_actual.sla:
            fecha_limite = solicitud.fecha_ultima_actualizacion + solicitud.etapa_actual.sla
            if timezone.now() > fecha_limite:
                solicitudes_vencidas += 1
    
    return JsonResponse({
        'total_solicitudes': total_solicitudes,
        'solicitudes_activas': solicitudes_activas,
        'solicitudes_completadas': solicitudes_completadas,
        'solicitudes_vencidas': solicitudes_vencidas,
        'solicitudes_por_pipeline': list(solicitudes_por_pipeline),
    })


def sitio_construccion(request):
    """Vista para página de sitio en construcción"""
    return render(request, 'workflow/sitio_construccion.html')


@login_required
def api_actualizar_prioridad(request, solicitud_id):
    """API para actualizar la prioridad de una solicitud"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            prioridad = data.get('prioridad', '').strip()
            solicitud = get_object_or_404(Solicitud, id=solicitud_id)
            # Eliminar validación de permisos, permitir a cualquier usuario
            prioridades_validas = ['Alta', 'Media', 'Baja']
            if prioridad and prioridad not in prioridades_validas:
                return JsonResponse({'success': False, 'error': 'Prioridad no válida'})
            solicitud.prioridad = prioridad
            solicitud.save()
            return JsonResponse({'success': True, 'prioridad': prioridad})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_actualizar_etiquetas(request, solicitud_id):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        etiquetas = data.get('etiquetas_oficial', '')
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        # Limpiar espacios de cada etiqueta
        etiquetas_limpias = ','.join([e.strip() for e in etiquetas.split(',') if e.strip()])
        solicitud.etiquetas_oficial = etiquetas_limpias
        solicitud.save()
        return JsonResponse({'success': True, 'etiquetas_oficial': etiquetas_limpias})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_buscar_clientes(request):
    """API para buscar clientes"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        if not query:
            return JsonResponse({'clientes': []})
        
        # Buscar clientes por nombre o cédula
        clientes = Cliente.objects.filter(
            Q(nombreCliente__icontains=query) | 
            Q(cedulaCliente__icontains=query)
        ).order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cliente in clientes:
            resultados.append({
                'id': cliente.id,
                'nombre': cliente.nombreCliente or 'Sin nombre',
                'cedula': cliente.cedulaCliente or 'Sin cédula',
                'fecha_creacion': cliente.created_at.strftime('%d/%m/%Y') if cliente.created_at else '',
                'texto_completo': f"{cliente.nombreCliente or 'Sin nombre'} - {cliente.cedulaCliente or 'Sin cédula'}"
            })
        
        return JsonResponse({'clientes': resultados})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def api_buscar_cotizaciones(request):
    """API para buscar cotizaciones"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        cliente_id = request.GET.get('cliente_id', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        # Filtrar cotizaciones
        cotizaciones = Cotizacion.objects.all()
        
        # Filtrar por cliente si se especifica
        if cliente_id:
            cotizaciones = cotizaciones.filter(cedulaCliente=cliente_id)
        
        # Buscar por número de cotización, nombre de cliente o monto
        if query:
            cotizaciones = cotizaciones.filter(
                Q(NumeroCotizacion__icontains=query) |
                Q(nombreCliente__icontains=query) |
                Q(montoPrestamo__icontains=query)
            )
        
        cotizaciones = cotizaciones.order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cotizacion in cotizaciones:
            # Use auxMonto2 as "Monto Financiado" instead of montoPrestamo
            monto_financiado = cotizacion.auxMonto2 or cotizacion.montoPrestamo or 0
            resultados.append({
                'id': cotizacion.id,
                'numero': cotizacion.NumeroCotizacion or cotizacion.id,
                'cliente': cotizacion.nombreCliente or 'Sin cliente',
                'monto_financiado': float(monto_financiado),
                'tipo': cotizacion.tipoPrestamo or 'Sin tipo',
                'fecha_creacion': cotizacion.created_at.strftime('%d/%m/%Y') if cotizacion.created_at else '',
                'texto_completo': f"#{cotizacion.NumeroCotizacion or cotizacion.id} - {cotizacion.nombreCliente or 'Sin cliente'} - Monto Financiado: ${monto_financiado}"
            })
        
        return JsonResponse({'cotizaciones': resultados})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def api_buscar_cotizaciones_drawer(request):
    """API para buscar cotizaciones en el drawer - solo Préstamos de Auto"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        if not query:
            return JsonResponse({'success': True, 'cotizaciones': []})
        
        # Base query - SOLO PRÉSTAMOS DE AUTO
        cotizaciones = Cotizacion.objects.filter(
            Q(nombreCliente__icontains=query) | 
            Q(cedulaCliente__icontains=query) |
            Q(id__icontains=query),
            tipoPrestamo='auto'  # Solo cotizaciones de préstamos de auto
        )
        
        # Filtrar por permisos de usuario
        if not (request.user.is_superuser or request.user.is_staff):
            # Usuarios regulares solo ven sus propias cotizaciones
            cotizaciones = cotizaciones.filter(added_by=request.user)
        
        # Ordenar y limitar resultados
        cotizaciones = cotizaciones.order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cotizacion in cotizaciones:
            resultado = {
                'id': cotizacion.id,
                'nombreCliente': cotizacion.nombreCliente or 'Sin nombre',
                'cedulaCliente': cotizacion.cedulaCliente or 'Sin cédula',
                'tipoPrestamo': cotizacion.tipoPrestamo or 'Sin tipo',
                'montoFinanciado': float(cotizacion.auxMonto2) if cotizacion.auxMonto2 else 0,  # Monto Financiado
                'oficial': cotizacion.oficial or 'Sin oficial',
                'observaciones': cotizacion.observaciones or '',  # Campo observaciones
                'created_at': cotizacion.created_at.isoformat() if cotizacion.created_at else None,
                # Vehicle data for SURA auto-population
                'valorAuto': float(cotizacion.valorAuto) if cotizacion.valorAuto else None,
                'yearCarro': cotizacion.yearCarro,
                'marca': cotizacion.marca or '',
                'modelo': cotizacion.modelo or '',
                'tipoDocumento': cotizacion.tipoDocumento or 'CEDULA'
            }
            print(f"🔧 DEBUG: Cotización {cotizacion.id} observaciones: '{cotizacion.observaciones}'")
            print(f"🔧 DEBUG: Cotización {cotizacion.id} observaciones type: {type(cotizacion.observaciones)}")
            print(f"🔧 DEBUG: Cotización {cotizacion.id} observaciones length: {len(cotizacion.observaciones) if cotizacion.observaciones else 0}")
            print(f"🔧 DEBUG: Cotización {cotizacion.id} vehicle data: valorAuto={cotizacion.valorAuto}, yearCarro={cotizacion.yearCarro}, marca={cotizacion.marca}, modelo={cotizacion.modelo}")
            resultados.append(resultado)
        
        return JsonResponse({'success': True, 'cotizaciones': resultados})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_buscar_clientes_drawer(request):
    """API para buscar clientes en el drawer"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        if not query:
            return JsonResponse({'success': True, 'clientes': []})
        
        # Buscar clientes por nombre o cédula
        clientes = Cliente.objects.filter(
            Q(nombreCliente__icontains=query) | 
            Q(cedulaCliente__icontains=query)
        ).order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cliente in clientes:
            resultados.append({
                'id': cliente.id,
                'nombreCliente': cliente.nombreCliente or 'Sin nombre',
                'cedulaCliente': cliente.cedulaCliente or 'Sin cédula',
                'edad': cliente.edad or 'Sin edad',
                'sexo': cliente.sexo or 'Sin sexo'
            })
        
        return JsonResponse({'success': True, 'clientes': resultados})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_formulario_datos(request):
    """API para obtener datos del formulario basado en el pipeline"""
    if request.method == 'GET':
        pipeline_id = request.GET.get('pipeline_id')
        
        if not pipeline_id:
            return JsonResponse({'success': False, 'error': 'ID de pipeline requerido'})
        
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            # Obtener campos personalizados del pipeline
            campos_personalizados = CampoPersonalizado.objects.filter(
                pipeline=pipeline
            ).values('id', 'nombre', 'tipo', 'requerido', 'descripcion')
            
            # Obtener requisitos del pipeline
            requisitos_pipeline = RequisitoPipeline.objects.filter(
                pipeline=pipeline
            ).select_related('requisito')
            
            requisitos = []
            for req_pipeline in requisitos_pipeline:
                requisitos.append({
                    'id': req_pipeline.requisito.id,
                    'nombre': req_pipeline.requisito.nombre,
                    'descripcion': req_pipeline.requisito.descripcion,
                    'obligatorio': req_pipeline.obligatorio
                })
            
            return JsonResponse({
                'success': True,
                'campos_personalizados': list(campos_personalizados),
                'requisitos': requisitos
            })
            
        except Pipeline.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Pipeline no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# Sistema de notificaciones en tiempo real
class NotificationManager:
    def __init__(self):
        self.clients = {}
        self.last_update = {}
    
    def add_client(self, user_id, response_queue):
        """Agregar cliente para notificaciones"""
        self.clients[user_id] = response_queue
        self.last_update[user_id] = timezone.now()
    
    def remove_client(self, user_id):
        """Remover cliente"""
        if user_id in self.clients:
            del self.clients[user_id]
        if user_id in self.last_update:
            del self.last_update[user_id]
    
    def notify_change(self, change_type, data, affected_users=None):
        """Notificar cambio a usuarios específicos o todos"""
        if affected_users is None:
            affected_users = list(self.clients.keys())
        
        notification = {
            'type': change_type,
            'data': data,
            'timestamp': timezone.now().isoformat()
        }
        
        for user_id in affected_users:
            if user_id in self.clients:
                try:
                    self.clients[user_id].put(notification)
                except:
                    # Cliente desconectado, remover
                    self.remove_client(user_id)

# Instancia global del manager
notification_manager = NotificationManager()

@login_required
def api_notifications_stream(request):
    """API de Server-Sent Events para notificaciones en tiempo real"""
    def event_stream():
        user_id = request.user.id
        response_queue = queue.Queue()
        
        # Agregar cliente
        notification_manager.add_client(user_id, response_queue)
        
        try:
            # Enviar evento inicial
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Conectado a notificaciones'})}\n\n"
            
            while True:
                try:
                    # Esperar por notificaciones con timeout
                    notification = response_queue.get(timeout=30)
                    yield f"data: {json.dumps(notification)}\n\n"
                except queue.Empty:
                    # Enviar heartbeat cada 30 segundos
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': timezone.now().isoformat()})}\n\n"
                except:
                    break
        finally:
            # Limpiar cliente al desconectar
            notification_manager.remove_client(user_id)
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    response['Access-Control-Allow-Origin'] = '*'
    return response

@login_required
def api_check_updates(request):
    """API mejorada para verificar actualizaciones con detección inteligente"""
    print(f"🔍 DEBUG: api_check_updates llamado por usuario: {request.user.username}")
    print(f"🔍 DEBUG: Método: {request.method}")
    print(f"🔍 DEBUG: Parámetros: {request.GET}")
    
    try:
        # Obtener timestamp de la última actualización del usuario
        last_check = request.GET.get('last_check')
        if last_check:
            try:
                last_check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            except:
                last_check_time = timezone.now() - timedelta(minutes=5)
        else:
            last_check_time = timezone.now() - timedelta(minutes=5)
        
        # Obtener vista actual para filtros específicos
        current_view = request.GET.get('view', 'bandejas')  # bandejas, tabla, kanban
        
        # Solicitudes del usuario según sus grupos
        solicitudes_base = Solicitud.objects.filter(
            etapa_actual__pipeline__grupos__in=request.user.groups.all()
        ).select_related('etapa_actual', 'asignada_a', 'pipeline')
        
        # Verificar cambios específicos por tipo de vista
        cambios_detectados = []
        
        # 1. Cambios en bandeja grupal (para vista bandejas)
        if current_view in ['bandejas', 'all']:
            solicitudes_grupales_nuevas = solicitudes_base.filter(
                etapa_actual__es_bandeja_grupal=True,
                asignada_a__isnull=True,
                fecha_ultima_actualizacion__gt=last_check_time
            ).count()
            
            if solicitudes_grupales_nuevas > 0:
                cambios_detectados.append({
                    'tipo': 'bandeja_grupal',
                    'count': solicitudes_grupales_nuevas
                })
        
        # 2. Cambios en tareas personales (para vista bandejas)
        if current_view in ['bandejas', 'all']:
            solicitudes_personales_nuevas = solicitudes_base.filter(
                asignada_a=request.user,
                fecha_ultima_actualizacion__gt=last_check_time
            ).count()
            
            if solicitudes_personales_nuevas > 0:
                cambios_detectados.append({
                    'tipo': 'bandeja_personal',
                    'count': solicitudes_personales_nuevas
                })
        
        # 3. Cambios generales en solicitudes (para tabla/kanban)
        if current_view in ['tabla', 'kanban', 'all']:
            solicitudes_actualizadas = solicitudes_base.filter(
                fecha_ultima_actualizacion__gt=last_check_time
            ).count()
            
            if solicitudes_actualizadas > 0:
                cambios_detectados.append({
                    'tipo': 'solicitudes_generales',
                    'count': solicitudes_actualizadas
                })
        
        # 4. Nuevas solicitudes creadas
        nuevas_solicitudes = solicitudes_base.filter(
            fecha_creacion__gt=last_check_time
        ).count()
        
        if nuevas_solicitudes > 0:
            cambios_detectados.append({
                'tipo': 'nuevas_solicitudes',
                'count': nuevas_solicitudes
            })
        
        # Obtener detalles de cambios para debugging
        solicitudes_modificadas = list(solicitudes_base.filter(
            fecha_ultima_actualizacion__gt=last_check_time
        ).values('id', 'codigo', 'etapa_actual__nombre', 'asignada_a__username')[:10])
        
        has_updates = len(cambios_detectados) > 0
        
        return JsonResponse({
            'success': True,
            'has_updates': has_updates,
            'cambios_detectados': cambios_detectados,
            'total_cambios': sum(c['count'] for c in cambios_detectados),
            'nuevas_solicitudes': nuevas_solicitudes,
            'solicitudes_modificadas': solicitudes_modificadas,
            'timestamp': timezone.now().isoformat(),
            'last_check': last_check_time.isoformat(),
            'view': current_view
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        })

# Función para notificar cambios automáticamente
def notify_solicitud_change(solicitud, change_type, user=None):
    """Notificar cambio en solicitud a usuarios relevantes"""
    try:
        # Obtener usuarios que deben ser notificados
        affected_users = []
        
        # Usuarios del grupo de la etapa actual
        if solicitud.etapa_actual:
            group_users = User.objects.filter(
                groups__in=solicitud.etapa_actual.pipeline.grupos.all()
            ).values_list('id', flat=True)
            affected_users.extend(group_users)
        
        # Usuario asignado
        if solicitud.asignada_a:
            affected_users.append(solicitud.asignada_a.id)
        
        # Datos de la notificación
        notification_data = {
            'solicitud_id': solicitud.id,
            'codigo': solicitud.codigo,
            'etapa_actual': {
                'id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
                'nombre': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
                'es_bandeja_grupal': solicitud.etapa_actual.es_bandeja_grupal if solicitud.etapa_actual else False
            },
            'asignada_a': {
                'id': solicitud.asignada_a.id if solicitud.asignada_a else None,
                'username': solicitud.asignada_a.username if solicitud.asignada_a else None,
                'nombre_completo': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else None
            },
            'user_action': {
                'id': user.id if user else None,
                'username': user.username if user else None,
                'nombre_completo': user.get_full_name() if user else None
            },
            'pipeline_id': solicitud.pipeline.id if solicitud.pipeline else None,
            'timestamp': timezone.now().isoformat()
        }
        
        # Enviar notificación
        notification_manager.notify_change(change_type, notification_data, affected_users)
        
    except Exception as e:
        print(f"Error notificando cambio: {e}")

# ==========================================
# VISTAS PRINCIPALES DEL WORKFLOW
# ==========================================

@login_required
def dashboard_workflow(request):
    """Dashboard principal del sistema de workflow (vista original)"""
    
    # Obtener solicitudes del usuario
    solicitudes_asignadas = Solicitud.objects.filter(
        asignada_a=request.user
    ).select_related('pipeline', 'etapa_actual', 'subestado_actual')
    
    # Obtener bandejas grupales a las que tiene acceso
    if request.user.is_superuser or request.user.is_staff:
        # Superuser y super staff ven TODAS las bandejas grupales
        etapas_grupales = Etapa.objects.filter(es_bandeja_grupal=True)
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related('pipeline', 'etapa_actual', 'subestado_actual')
    else:
        # Usuarios regulares - permisos normales
        grupos_usuario = request.user.groups.all()
        etapas_grupales = Etapa.objects.filter(
            es_bandeja_grupal=True,
            permisos__grupo__in=grupos_usuario,
            permisos__puede_ver=True
        )
        
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related('pipeline', 'etapa_actual', 'subestado_actual')
    
    # Estadísticas
    total_solicitudes = solicitudes_asignadas.count() + solicitudes_grupales.count()
    solicitudes_vencidas = 0
    solicitudes_proximo_vencer = 0
    
    for solicitud in solicitudes_asignadas:
        if solicitud.etapa_actual:
            tiempo_en_etapa = timezone.now() - solicitud.fecha_ultima_actualizacion
            if tiempo_en_etapa > solicitud.etapa_actual.sla:
                solicitudes_vencidas += 1
            elif tiempo_en_etapa > solicitud.etapa_actual.sla * 0.8:  # 80% del SLA
                solicitudes_proximo_vencer += 1
    
    # Pipelines disponibles
    pipelines = Pipeline.objects.all()
    
    context = {
        'solicitudes_asignadas': solicitudes_asignadas[:10],
        'solicitudes_grupales': solicitudes_grupales[:10],
        'total_solicitudes': total_solicitudes,
        'solicitudes_vencidas': solicitudes_vencidas,
        'solicitudes_proximo_vencer': solicitudes_proximo_vencer,
        'pipelines': pipelines,
        'etapas_grupales': etapas_grupales,
    }
    
    return render(request, 'workflow/dashboard.html', context)


@login_required
def bandeja_trabajo(request):
    """Bandeja de trabajo del usuario"""
    
    # === SISTEMA DE PERMISOS SUPERUSER Y SUPER STAFF ===
    # Los usuarios superuser y super staff (is_staff=True) pueden ver TODO
    if request.user.is_superuser or request.user.is_staff:
        # Superuser y super staff ven TODAS las solicitudes asignadas
        solicitudes_asignadas = Solicitud.objects.filter(
            asignada_a__isnull=False
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
        
        # Superuser y super staff ven TODAS las bandejas grupales (excluir Comité de Crédito)
        etapas_grupales = Etapa.objects.filter(es_bandeja_grupal=True).exclude(nombre__iexact="Comité de Crédito")
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
    else:
        # Usuarios regulares - permisos normales
        # Obtener solicitudes asignadas al usuario
        solicitudes_asignadas = Solicitud.objects.filter(
            asignada_a=request.user
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
        
        # Obtener bandejas grupales (excluir Comité de Crédito)
        grupos_usuario = request.user.groups.all()
        etapas_grupales = Etapa.objects.filter(
            es_bandeja_grupal=True,
            permisos__grupo__in=grupos_usuario,
            permisos__puede_autoasignar=True
        ).exclude(nombre__iexact="Comité de Crédito")
        
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        )
    
    # Filtros
    filtro_estado = request.GET.get('estado', '')
    filtro_pipeline = request.GET.get('pipeline', '')
    
    if filtro_estado == 'vencidas':
        solicitudes_asignadas = solicitudes_asignadas.filter(
            fecha_ultima_actualizacion__lt=timezone.now() - F('etapa_actual__sla')
        )
        solicitudes_grupales = solicitudes_grupales.filter(
            fecha_ultima_actualizacion__lt=timezone.now() - F('etapa_actual__sla')
        )
    
    if filtro_pipeline:
        solicitudes_asignadas = solicitudes_asignadas.filter(pipeline_id=filtro_pipeline)
        solicitudes_grupales = solicitudes_grupales.filter(pipeline_id=filtro_pipeline)
    
    # Paginación
    todas_solicitudes = list(solicitudes_asignadas) + list(solicitudes_grupales)
    paginator = Paginator(todas_solicitudes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'solicitudes_asignadas': solicitudes_asignadas,
        'solicitudes_grupales': solicitudes_grupales,
        'pipelines': Pipeline.objects.all(),
        'filtros': {
            'estado': filtro_estado,
            'pipeline': filtro_pipeline,
        }
    }
    
    return render(request, 'workflow/bandeja_trabajo.html', context)


@login_required
def nueva_solicitud(request):
    """Crear una nueva solicitud"""
    
    if request.method == 'POST':
        pipeline_id = request.POST.get('pipeline')
        cliente_id = request.POST.get('cliente')
        cotizacion_id = request.POST.get('cotizacion')
        
        if pipeline_id:
            try:
                pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            except Exception as e:
                messages.error(request, f'Pipeline no encontrado: {e}')
                return JsonResponse({'success': False, 'error': f'Pipeline {pipeline_id} no existe'}, status=400)
            
            # Obtener primera etapa del pipeline
            primera_etapa = pipeline.etapas.order_by('orden').first()
            
            # Obtener cliente y cotización si se proporcionaron
            cliente = None
            cotizacion = None
            
            if cliente_id:
                cliente = get_object_or_404(Cliente, id=cliente_id)
            
            if cotizacion_id:
                cotizacion = get_object_or_404(Cotizacion, id=cotizacion_id)
            
            # Obtener motivo de consulta, como se enteró y APC fields del formulario
            motivo_consulta = request.POST.get('motivo_consulta', '')
            como_se_entero = request.POST.get('como_se_entero', '')
            
            # APC Makito fields
            descargar_apc_makito = request.POST.get('descargar_apc_makito') == '1'
            apc_no_cedula = request.POST.get('apc_no_cedula', '') if descargar_apc_makito else None
            apc_tipo_documento = request.POST.get('apc_tipo_documento', '') if descargar_apc_makito else None
            
            # SURA Makito fields
            cotizar_sura_makito = request.POST.get('cotizar_sura_makito') == '1'
            sura_primer_nombre = request.POST.get('sura_primer_nombre', '') if cotizar_sura_makito else None
            sura_segundo_nombre = request.POST.get('sura_segundo_nombre', '') if cotizar_sura_makito else None
            sura_primer_apellido = request.POST.get('sura_primer_apellido', '') if cotizar_sura_makito else None
            sura_segundo_apellido = request.POST.get('sura_segundo_apellido', '') if cotizar_sura_makito else None
            sura_no_documento = request.POST.get('sura_no_documento', '') if cotizar_sura_makito else None
            sura_tipo_documento = request.POST.get('sura_tipo_documento', '') if cotizar_sura_makito else None
            sura_valor_auto = request.POST.get('sura_valor_auto', '') if cotizar_sura_makito else None
            sura_ano_auto = request.POST.get('sura_ano_auto', '') if cotizar_sura_makito else None
            sura_marca = request.POST.get('sura_marca', '') if cotizar_sura_makito else None
            sura_modelo = request.POST.get('sura_modelo', '') if cotizar_sura_makito else None
            
            # Crear solicitud (el código se generará automáticamente via signal)
            solicitud = Solicitud.objects.create(
                pipeline=pipeline,
                etapa_actual=primera_etapa,
                creada_por=request.user,
                propietario=request.user,  # Set propietario to the user who created the solicitud
                cliente=cliente,
                cotizacion=cotizacion,
                motivo_consulta=motivo_consulta,
                como_se_entero=como_se_entero if como_se_entero else None,
                descargar_apc_makito=descargar_apc_makito,
                apc_no_cedula=apc_no_cedula,
                apc_tipo_documento=apc_tipo_documento if apc_tipo_documento else None,
                cotizar_sura_makito=cotizar_sura_makito,
                sura_primer_nombre=sura_primer_nombre,
                sura_segundo_nombre=sura_segundo_nombre,
                sura_primer_apellido=sura_primer_apellido,
                sura_segundo_apellido=sura_segundo_apellido,
                sura_no_documento=sura_no_documento,
                sura_tipo_documento=sura_tipo_documento,
                sura_valor_auto=sura_valor_auto,
                sura_ano_auto=sura_ano_auto,
                sura_marca=sura_marca,
                sura_modelo=sura_modelo
            )
            
            # Crear historial inicial
            if primera_etapa:
                HistorialSolicitud.objects.create(
                    solicitud=solicitud,
                    etapa=primera_etapa,
                    usuario_responsable=request.user,
                    fecha_inicio=timezone.now()
                )
            
            # Crear requisitos automáticamente
            requisitos_pipeline = RequisitoPipeline.objects.filter(
                pipeline=pipeline
            )
            
            for req_pipeline in requisitos_pipeline:
                requisito_solicitud = RequisitoSolicitud.objects.create(
                    solicitud=solicitud,
                    requisito=req_pipeline.requisito
                )
                
                # Verificar si hay archivo subido para este requisito
                archivo_key = f'archivo_requisito_{req_pipeline.requisito.id}'
                if archivo_key in request.FILES:
                    requisito_solicitud.archivo = request.FILES[archivo_key]
                    requisito_solicitud.cumplido = True  # Marcar como cumplido cuando se sube archivo
                    requisito_solicitud.save()
            
            # Guardar campos personalizados
            campos_personalizados = CampoPersonalizado.objects.filter(pipeline=pipeline)
            for campo in campos_personalizados:
                valor = request.POST.get(f'campo_{campo.id}')
                if valor:
                    valor_campo = ValorCampoSolicitud.objects.create(
                        solicitud=solicitud,
                        campo=campo
                    )
                    
                    # Guardar según el tipo de campo
                    if campo.tipo == 'texto':
                        valor_campo.valor_texto = valor
                    elif campo.tipo == 'numero':
                        valor_campo.valor_numero = float(valor) if valor else None
                    elif campo.tipo == 'entero':
                        valor_campo.valor_entero = int(valor) if valor else None
                    elif campo.tipo == 'fecha':
                        from datetime import datetime
                        valor_campo.valor_fecha = datetime.strptime(valor, '%Y-%m-%d').date() if valor else None
                    elif campo.tipo == 'booleano':
                        valor_campo.valor_booleano = valor == 'true'
                    
                    valor_campo.save()
            
            # Send APC email if requested
            if descargar_apc_makito and apc_no_cedula and apc_tipo_documento:
                try:
                    enviar_correo_apc_makito(solicitud, apc_no_cedula, apc_tipo_documento, request)
                except Exception as e:
                    print(f"Error enviando correo APC: {e}")
                    # No detener el proceso por error en correo
            
            # Send SURA email if requested
            if cotizar_sura_makito and sura_primer_nombre and sura_primer_apellido and sura_no_documento:
                enviar_correo_sura_makito(
                    solicitud, 
                    sura_primer_nombre, 
                    sura_primer_apellido, 
                    sura_no_documento,
                    request,
                    # Vehicle data
                    sura_valor_auto=sura_valor_auto,
                    sura_ano_auto=sura_ano_auto,
                    sura_marca=sura_marca,
                    sura_modelo=sura_modelo,
                    sura_tipo_documento=sura_tipo_documento
                )
            
            # Responder con JSON para requests AJAX
            if request.content_type == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'solicitud_id': solicitud.id,
                    'codigo': solicitud.codigo,
                    'message': f'Solicitud {solicitud.codigo} creada exitosamente.'
                })
            
            messages.success(request, f'Solicitud {solicitud.codigo} creada exitosamente.')
            return redirect('workflow:detalle_solicitud', solicitud_id=solicitud.id)
    
    # Obtener clientes y cotizaciones para el formulario
    
    # Obtener clientes del usuario actual o todos si es superuser
    if request.user.is_superuser:
        clientes = Cliente.objects.all().order_by('-created_at')[:100]  # Últimos 100 clientes
    else:
        clientes = Cliente.objects.filter(
            Q(added_by=request.user) | 
            Q(propietario=request.user)
        ).order_by('-created_at')[:100]
    
    # Obtener cotizaciones del usuario actual o todas si es superuser
    if request.user.is_superuser:
        cotizaciones = Cotizacion.objects.all().order_by('-created_at')[:100]  # Últimas 100 cotizaciones
    else:
        cotizaciones = Cotizacion.objects.filter(added_by=request.user).order_by('-created_at')[:100]
    
    context = {
        'pipelines': Pipeline.objects.all(),
        'clientes': clientes,
        'cotizaciones': cotizaciones,
    }
    
    return render(request, 'workflow/nueva_solicitud.html', context)


@login_required
def transicion_solicitud(request, solicitud_id):
    """Realizar transición de una solicitud"""
    
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        transicion_id = request.POST.get('transicion_id')
        
        if transicion_id:
            transicion = get_object_or_404(TransicionEtapa, id=transicion_id)
            
            # Verificar que la transición es válida
            if transicion.pipeline != solicitud.pipeline or transicion.etapa_origen != solicitud.etapa_actual:
                messages.error(request, 'Transición no válida.')
                return redirect('detalle_solicitud', solicitud_id=solicitud_id)
            
            # Verificar permisos si es necesario
            if transicion.requiere_permiso:
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=transicion.etapa_destino,
                    grupo__in=grupos_usuario
                ).exists()
                if not tiene_permiso:
                    messages.error(request, 'No tienes permisos para realizar esta transición.')
                    return redirect('detalle_solicitud', solicitud_id=solicitud_id)
            
            # Verificar requisitos obligatorios
            requisitos_pendientes = solicitud.requisitos.filter(
                requisito__requisitopipelinetipo__obligatorio=True,
                cumplido=False
            )
            
            if requisitos_pendientes.exists():
                messages.error(request, 'Debes cumplir todos los requisitos obligatorios antes de continuar.')
                return redirect('detalle_solicitud', solicitud_id=solicitud_id)
            
            # Cerrar historial actual
            historial_actual = solicitud.historial.filter(fecha_fin__isnull=True).first()
            if historial_actual:
                historial_actual.fecha_fin = timezone.now()
                historial_actual.save()
            
            # Actualizar solicitud
            solicitud.etapa_actual = transicion.etapa_destino
            solicitud.subestado_actual = None  # Resetear subestado
            solicitud.save()
            
            # Crear nuevo historial
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=transicion.etapa_destino,
                usuario_responsable=request.user,
                fecha_inicio=timezone.now()
            )
            
            messages.success(request, f'Solicitud movida a {transicion.etapa_destino.nombre}')
            return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    return redirect('detalle_solicitud', solicitud_id=solicitud_id)


@login_required
def auto_asignar_solicitud(request, solicitud_id):
    """Auto-asignar una solicitud de bandeja grupal"""
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que la solicitud está en bandeja grupal
    if not solicitud.etapa_actual.es_bandeja_grupal or solicitud.asignada_a:
        messages.error(request, 'Esta solicitud no está disponible para auto-asignación.')
        return redirect('bandeja_trabajo')
    
    # Verificar permisos
    # Superusers bypass permission checks
    if not (request.user.is_superuser or request.user.is_staff):
        grupos_usuario = request.user.groups.all()
        tiene_permiso = PermisoEtapa.objects.filter(
            etapa=solicitud.etapa_actual,
            grupo__in=grupos_usuario,
            puede_autoasignar=True
        ).exists()
        
        if not tiene_permiso:
            messages.error(request, 'No tienes permisos para auto-asignar solicitudes en esta etapa.')
            return redirect('bandeja_trabajo')
    
    # Asignar solicitud
    solicitud.asignada_a = request.user
    solicitud.save()
    
    messages.success(request, f'Solicitud {solicitud.codigo} asignada exitosamente.')
    return redirect('detalle_solicitud', solicitud_id=solicitud_id)


@login_required
def actualizar_requisito(request, solicitud_id, requisito_id):
    """Actualizar estado de un requisito"""
    
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        requisito_solicitud = get_object_or_404(RequisitoSolicitud, id=requisito_id, solicitud=solicitud)
        
        # Verificar permisos
        if solicitud.asignada_a and solicitud.asignada_a != request.user:
            # Superusers bypass permission checks
            if not (request.user.is_superuser or request.user.is_staff):
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=solicitud.etapa_actual,
                    grupo__in=grupos_usuario,
                    puede_ver=True
                ).exists()
                
                if not tiene_permiso:
                    return JsonResponse({'error': 'No tienes permisos para actualizar esta solicitud.'}, status=403)
        
        # Actualizar requisito
        cumplido = request.POST.get('cumplido') == 'true'
        observaciones = request.POST.get('observaciones', '')
        
        requisito_solicitud.cumplido = cumplido
        requisito_solicitud.observaciones = observaciones
        
        # Manejar archivo si se sube
        if 'archivo' in request.FILES:
            requisito_solicitud.archivo = request.FILES['archivo']
        
        requisito_solicitud.save()
        
        return JsonResponse({
            'success': True,
            'cumplido': cumplido,
            'observaciones': observaciones
        })
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def actualizar_campo_personalizado(request, solicitud_id):
    """Actualizar campos personalizados de una solicitud"""
    
    if request.method == 'POST':
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if solicitud.asignada_a and solicitud.asignada_a != request.user:
            # Superusers bypass permission checks
            if not (request.user.is_superuser or request.user.is_staff):
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=solicitud.etapa_actual,
                    grupo__in=grupos_usuario,
                    puede_ver=True
                ).exists()
                
                if not tiene_permiso:
                    return JsonResponse({'error': 'No tienes permisos para actualizar esta solicitud.'}, status=403)
        
        campos_personalizados = CampoPersonalizado.objects.filter(pipeline=solicitud.pipeline)
        
        for campo in campos_personalizados:
            valor_campo, created = ValorCampoSolicitud.objects.get_or_create(
                solicitud=solicitud,
                campo=campo
            )
            
            valor = request.POST.get(f'campo_{campo.id}')
            
            if campo.tipo == 'texto':
                valor_campo.valor_texto = valor
            elif campo.tipo == 'numero':
                valor_campo.valor_numero = float(valor) if valor else None
            elif campo.tipo == 'entero':
                valor_campo.valor_entero = int(valor) if valor else None
            elif campo.tipo == 'fecha':
                valor_campo.valor_fecha = datetime.strptime(valor, '%Y-%m-%d').date() if valor else None
            elif campo.tipo == 'booleano':
                valor_campo.valor_booleano = valor == 'true'
            
            valor_campo.save()
        
        messages.success(request, 'Campos personalizados actualizados exitosamente.')
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


# ==========================================
# VISTAS DE ADMINISTRACIÓN
# ==========================================

@login_required
@superuser_permission_required('workflow.add_pipeline')
def administrar_pipelines(request):
    """Administración de pipelines"""
    
    pipelines = Pipeline.objects.all().prefetch_related('etapas')
    
    context = {
        'pipelines': pipelines,
    }
    
    return render(request, 'workflow/admin/pipelines.html', context)


@login_required
@superuser_permission_required('workflow.add_requisito')
def administrar_requisitos(request):
    """Administración de requisitos"""
    
    requisitos = Requisito.objects.all()
    requisitos_pipeline = RequisitoPipeline.objects.all().select_related('pipeline', 'requisito')
    
    context = {
        'requisitos': requisitos,
        'requisitos_pipeline': requisitos_pipeline,
    }
    
    return render(request, 'workflow/admin/requisitos.html', context)


@login_required
@superuser_permission_required('workflow.add_campopersonalizado')
def administrar_campos_personalizados(request):
    """Administración de campos personalizados"""
    
    campos = CampoPersonalizado.objects.all().select_related('pipeline')
    
    context = {
        'campos': campos,
    }
    
    return render(request, 'workflow/admin/campos_personalizados.html', context)


@login_required
def administrar_usuarios(request):
    """Vista para administrar usuarios y grupos - Solo para administradores"""
    
    # Verificar permisos de administrador
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('workflow:dashboard')
    
    # Obtener usuarios y grupos
    usuarios = User.objects.select_related('userprofile').all().order_by('username')
    grupos = Group.objects.all().order_by('name')
    
    # Estadísticas
    total_usuarios = usuarios.count()
    usuarios_activos = usuarios.filter(is_active=True).count()
    usuarios_inactivos = total_usuarios - usuarios_activos
    total_grupos = grupos.count()
    
    # Usuarios por grupo
    usuarios_por_grupo = {}
    for grupo in grupos:
        usuarios_por_grupo[grupo.name] = grupo.user_set.count()
    
    # Usuarios sin grupos
    usuarios_sin_grupos = usuarios.filter(groups__isnull=True).count()
    
    context = {
        'usuarios': usuarios,
        'grupos': grupos,
        'total_usuarios': total_usuarios,
        'usuarios_activos': usuarios_activos,
        'usuarios_inactivos': usuarios_inactivos,
        'total_grupos': total_grupos,
        'usuarios_por_grupo': usuarios_por_grupo,
        'usuarios_sin_grupos': usuarios_sin_grupos,
    }
    
    return render(request, 'workflow/admin/usuarios.html', context)


# ==========================================
# VISTAS DE REPORTES
# ==========================================

@login_required
def reportes_workflow(request):
    """Reportes del sistema de workflow"""
    
    # Estadísticas generales
    total_solicitudes = Solicitud.objects.count()
    solicitudes_activas = Solicitud.objects.filter(etapa_actual__isnull=False).count()
    solicitudes_completadas = Solicitud.objects.filter(etapa_actual__isnull=True).count()
    
    # Solicitudes por pipeline
    solicitudes_por_pipeline = Pipeline.objects.annotate(
        total=Count('solicitud')
    ).values('nombre', 'total')
    
    # Solicitudes vencidas - Calculamos usando Python para compatibilidad con SQLite
    from datetime import timedelta
    solicitudes_vencidas = 0
    for solicitud in Solicitud.objects.filter(etapa_actual__isnull=False).select_related('etapa_actual'):
        if solicitud.etapa_actual and solicitud.etapa_actual.sla:
            fecha_limite = solicitud.fecha_ultima_actualizacion + solicitud.etapa_actual.sla
            if timezone.now() > fecha_limite:
                solicitudes_vencidas += 1
    
    # Tiempo promedio por etapa - Calculamos usando Python para compatibilidad con SQLite
    tiempos_promedio = []
    historiales = HistorialSolicitud.objects.filter(
        fecha_fin__isnull=False
    ).select_related('etapa')
    
    etapas_tiempos = {}
    for historial in historiales:
        etapa_nombre = historial.etapa.nombre
        if etapa_nombre not in etapas_tiempos:
            etapas_tiempos[etapa_nombre] = []
        
        tiempo_horas = (historial.fecha_fin - historial.fecha_inicio).total_seconds() / 3600
        etapas_tiempos[etapa_nombre].append(tiempo_horas)
    
    for etapa_nombre, tiempos in etapas_tiempos.items():
        tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
        tiempos_promedio.append({
            'etapa__nombre': etapa_nombre,
            'tiempo_promedio': tiempo_promedio
        })
    
    context = {
        'total_solicitudes': total_solicitudes,
        'solicitudes_activas': solicitudes_activas,
        'solicitudes_completadas': solicitudes_completadas,
        'solicitudes_vencidas': solicitudes_vencidas,
        'solicitudes_por_pipeline': solicitudes_por_pipeline,
        'tiempos_promedio': tiempos_promedio,
    }
    
    return render(request, 'workflow/reportes.html', context)


# ==========================================
# VISTAS DE CANALES ALTERNOS
# ==========================================

@csrf_exempt
@login_required
def convertir_formulario_a_solicitud(request):
    """Convierte un FormularioWeb en una Solicitud del workflow"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        from .models import FormularioWeb
        from .modelsWorkflow import Pipeline, Etapa, Solicitud, HistorialSolicitud, ConfiguracionCanalDigital
        from pacifico.models import Cliente
        import json
        
        data = json.loads(request.body)
        formulario_id = data.get('formulario_id')
        pipeline_id = data.get('pipeline_id')
        etapa_id = data.get('etapa_id')
        
        if not formulario_id:
            return JsonResponse({'success': False, 'error': 'ID de formulario requerido'})
        
        # Obtener el formulario
        formulario = get_object_or_404(FormularioWeb, id=formulario_id)
        
        if formulario.procesado:
            return JsonResponse({'success': False, 'error': 'Este formulario ya ha sido procesado'})
        
        # Determinar pipeline y etapa
        if pipeline_id:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        else:
            # Usar configuración por defecto
            pipeline = ConfiguracionCanalDigital.get_pipeline_por_defecto()
            if not pipeline:
                return JsonResponse({'success': False, 'error': 'No hay pipeline configurado por defecto'})
        
        if etapa_id:
            etapa = get_object_or_404(Etapa, id=etapa_id, pipeline=pipeline)
        else:
            # Usar configuración por defecto
            etapa = ConfiguracionCanalDigital.get_etapa_por_defecto()
            if not etapa or etapa.pipeline != pipeline:
                # Buscar primera etapa del pipeline
                etapa = pipeline.etapas.first()
                if not etapa:
                    return JsonResponse({'success': False, 'error': f'No hay etapas configuradas en el pipeline {pipeline.nombre}'})
        
        # Buscar o crear cliente basado en la cédula
        cliente = None
        if formulario.cedulaCliente:
            try:
                cliente = Cliente.objects.filter(cedula=formulario.cedulaCliente).first()
            except:
                pass
        
        # Crear la solicitud
        import uuid
        codigo = f"{pipeline.nombre[:3].upper()}-{uuid.uuid4().hex[:8].upper()}"
        
        solicitud = Solicitud()
        solicitud.codigo = codigo
        solicitud.pipeline = pipeline
        solicitud.etapa_actual = etapa
        # Asignar datos del formulario directamente a los campos del modelo
        solicitud.cliente_nombre = formulario.get_nombre_completo()
        solicitud.cliente_cedula = formulario.cedulaCliente
        solicitud.cliente_telefono = formulario.celular
        solicitud.cliente_email = formulario.correo_electronico
        solicitud.producto_solicitado = formulario.producto_interesado
        solicitud.monto_solicitado = formulario.dinero_a_solicitar or 0
        # NO asignar propietario - las solicitudes del Canal Digital llegan sin propietario
        solicitud.propietario = None
        solicitud.creada_por = request.user
        solicitud.cliente = cliente
        solicitud.origen = 'Canal Digital'  # Etiqueta distintiva
        solicitud.observaciones = f"Solicitud creada desde Canal Digital - IP: {formulario.ip_address}"
        solicitud.save()
        
        # Crear historial inicial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=etapa,
            usuario_responsable=request.user
        )
        
        # Marcar formulario como procesado
        formulario.procesado = True
        formulario.save()
        
        return JsonResponse({
            'success': True, 
            'mensaje': f'Solicitud {solicitud.codigo} creada exitosamente en {pipeline.nombre} - {etapa.nombre}',
            'solicitud_id': solicitud.id,
            'solicitud_codigo': solicitud.codigo,
            'pipeline_nombre': pipeline.nombre,
            'etapa_nombre': etapa.nombre
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@login_required
def procesar_formularios_masivo(request):
    """Convierte múltiples FormularioWeb en Solicitudes del workflow"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        from .models import FormularioWeb
        from .modelsWorkflow import Pipeline, Etapa, Solicitud, HistorialSolicitud, ConfiguracionCanalDigital
        from pacifico.models import Cliente
        import json
        
        data = json.loads(request.body)
        formulario_ids = data.get('formulario_ids', [])
        pipeline_id = data.get('pipeline_id')
        etapa_id = data.get('etapa_id')
        
        if not formulario_ids:
            return JsonResponse({'success': False, 'error': 'No se seleccionaron formularios'})
        
        # Determinar pipeline y etapa
        if pipeline_id:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        else:
            # Usar configuración por defecto
            pipeline = ConfiguracionCanalDigital.get_pipeline_por_defecto()
            if not pipeline:
                return JsonResponse({'success': False, 'error': 'No hay pipeline configurado por defecto'})
        
        if etapa_id:
            etapa = get_object_or_404(Etapa, id=etapa_id, pipeline=pipeline)
        else:
            # Usar configuración por defecto
            etapa = ConfiguracionCanalDigital.get_etapa_por_defecto()
            if not etapa or etapa.pipeline != pipeline:
                # Buscar primera etapa del pipeline
                etapa = pipeline.etapas.first()
                if not etapa:
                    return JsonResponse({'success': False, 'error': f'No hay etapas configuradas en el pipeline {pipeline.nombre}'})
        
        formularios = FormularioWeb.objects.filter(id__in=formulario_ids, procesado=False)
        solicitudes_creadas = []
        errores = []
        
        for formulario in formularios:
            try:
                # Buscar cliente
                cliente = None
                if formulario.cedulaCliente:
                    try:
                        cliente = Cliente.objects.filter(cedula=formulario.cedulaCliente).first()
                    except:
                        pass
                
                # Crear la solicitud
                solicitud = Solicitud.objects.create(
                    pipeline=pipeline,
                    etapa_actual=etapa,
                    cliente_nombre=formulario.get_nombre_completo(),
                    cliente_cedula=formulario.cedulaCliente,
                    cliente_telefono=formulario.celular,
                    cliente_email=formulario.correo_electronico,
                    producto_solicitado=formulario.producto_interesado,
                    monto_solicitado=formulario.dinero_a_solicitar or 0,
                    # NO asignar propietario - las solicitudes del Canal Digital llegan sin propietario
                    propietario=None,
                    cliente=cliente,
                    origen='Canal Digital',
                    observaciones=f"Solicitud creada desde formulario web del Canal Digital (ID: {formulario.id})"
                )
                
                # Crear historial inicial
                HistorialSolicitud.objects.create(
                    solicitud=solicitud,
                    etapa_anterior=None,
                    etapa_nueva=etapa,
                    usuario=request.user,
                    observaciones=f"Solicitud creada desde formulario web del Canal Digital (ID: {formulario.id})",
                    es_automatico=True
                )
                
                # Marcar formulario como procesado
                formulario.procesado = True
                formulario.save()
                
                solicitudes_creadas.append({
                    'formulario_id': formulario.id,
                    'solicitud_codigo': solicitud.codigo,
                    'solicitud_id': solicitud.id
                })
                
            except Exception as e:
                errores.append({
                    'formulario_id': formulario.id,
                    'nombre': formulario.get_nombre_completo(),
                    'error': str(e)
                })
        
        return JsonResponse({
            'success': True,
            'solicitudes_creadas': len(solicitudes_creadas),
            'errores': len(errores),
            'detalle_solicitudes': solicitudes_creadas,
            'detalle_errores': errores,
            'pipeline_nombre': pipeline.nombre,
            'etapa_nombre': etapa.nombre
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
def formulario_web(request):
    """Vista para el formulario web del canal digital - Crea solicitud automáticamente"""
    
    if request.method == 'POST':
        from .forms import FormularioWebForm
        form = FormularioWebForm(request.POST)
        
        if form.is_valid():
            # Guardar el formulario
            formulario = form.save(commit=False)
            
            # Agregar información adicional
            if request.META.get('HTTP_X_FORWARDED_FOR'):
                formulario.ip_address = request.META.get('HTTP_X_FORWARDED_FOR').split(',')[0]
            else:
                formulario.ip_address = request.META.get('REMOTE_ADDR')
            
            formulario.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limitar tamaño
            formulario.save()
            
            # CREAR SOLICITUD AUTOMÁTICAMENTE
            try:
                from .modelsWorkflow import Pipeline, Etapa, Solicitud, HistorialSolicitud, ConfiguracionCanalDigital
                from pacifico.models import Cliente
                from django.contrib.auth.models import User
                
                # Usar configuración del Canal Digital
                pipeline = ConfiguracionCanalDigital.get_pipeline_por_defecto()
                etapa = ConfiguracionCanalDigital.get_etapa_por_defecto()
                
                if not pipeline:
                    # Fallback al primer pipeline disponible
                    pipeline = Pipeline.objects.first()
                
                if pipeline:
                    # Si no hay etapa configurada o no pertenece al pipeline, usar la primera
                    if not etapa or etapa.pipeline != pipeline:
                        etapa = pipeline.etapas.first()
                    
                    if etapa:
                        # Buscar o crear cliente basado en la cédula
                        cliente = None
                        if formulario.cedulaCliente:
                            try:
                                cliente = Cliente.objects.filter(cedula=formulario.cedulaCliente).first()
                            except:
                                pass
                        
                        # Obtener usuario del sistema para crear la solicitud (primer superuser disponible)
                        usuario_sistema = User.objects.filter(is_superuser=True).first()
                        if not usuario_sistema:
                            usuario_sistema = User.objects.first()  # Fallback
                        
                        # Crear la solicitud automáticamente
                        import uuid
                        codigo = f"{pipeline.nombre[:3].upper()}-{uuid.uuid4().hex[:8].upper()}"
                        
                        solicitud = Solicitud()
                        solicitud.codigo = codigo
                        solicitud.pipeline = pipeline
                        solicitud.etapa_actual = etapa
                        # Asignar datos del formulario directamente a los campos del modelo
                        solicitud.cliente_nombre = formulario.get_nombre_completo()
                        solicitud.cliente_cedula = formulario.cedulaCliente
                        solicitud.cliente_telefono = formulario.celular
                        solicitud.cliente_email = formulario.correo_electronico
                        
                        # Convertir el producto antes de guardarlo
                        producto_original = formulario.producto_interesado
                        if producto_original == 'Préstamos personal':
                            solicitud.producto_solicitado = 'Personal'
                        elif producto_original == 'Préstamo de auto':
                            solicitud.producto_solicitado = 'Auto'
                        else:
                            solicitud.producto_solicitado = producto_original
                            
                        solicitud.monto_solicitado = formulario.dinero_a_solicitar or 0
                        # NO asignar propietario - las solicitudes del Canal Digital llegan sin propietario
                        solicitud.propietario = None
                        solicitud.creada_por = usuario_sistema
                        solicitud.cliente = cliente
                        solicitud.origen = 'Canal Digital'  # Etiqueta distintiva
                        solicitud.observaciones = f"Solicitud creada automáticamente desde Canal Digital - IP: {formulario.ip_address}"
                        solicitud.save()
                        
                        # Crear historial inicial
                        HistorialSolicitud.objects.create(
                            solicitud=solicitud,
                            etapa=etapa,
                            usuario_responsable=usuario_sistema
                        )
                        
                        # Marcar formulario como procesado
                        formulario.procesado = True
                        formulario.save()
                        
                        print(f"✅ Solicitud {solicitud.codigo} creada automáticamente desde Canal Digital")
                        
            except Exception as e:
                # Si hay error creando la solicitud, continuar pero logear el error
                print(f"❌ Error creando solicitud automática: {str(e)}")
                # El formulario se guarda de todas formas
            
            # Redirigir a página de éxito
            return redirect('https://fpacifico.com/prestamos/')
        else:
            # Si hay errores, mostrar el formulario con errores
            context = {
                'form': form,
                'error_message': True,
            }
            return render(request, 'workflow/formulario_web.html', context)
    else:
        # GET request - mostrar formulario vacío
        from .forms import FormularioWebForm
        form = FormularioWebForm()
        
        context = {
            'form': form,
            'error_message': False,
        }
        return render(request, 'workflow/formulario_web.html', context)


# ==========================================
# VISTAS DE API PARA PIPELINES
# ==========================================

@login_required
@superuser_permission_required('workflow.add_pipeline')
def api_crear_pipeline(request):
    """API para crear un nuevo pipeline"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            pipeline = Pipeline.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            
            return JsonResponse({
                'success': True,
                'pipeline': {
                    'id': pipeline.id,
                    'nombre': pipeline.nombre,
                    'descripcion': pipeline.descripcion
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.change_pipeline')
def api_editar_pipeline(request, pipeline_id):
    """API para editar un pipeline"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            pipeline.nombre = nombre
            pipeline.descripcion = descripcion
            pipeline.save()
            
            return JsonResponse({
                'success': True,
                'pipeline': {
                    'id': pipeline.id,
                    'nombre': pipeline.nombre,
                    'descripcion': pipeline.descripcion
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.delete_pipeline')
def api_eliminar_pipeline(request, pipeline_id):
    """API para eliminar un pipeline"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            # Verificar que no hay solicitudes activas
            if pipeline.solicitud_set.exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar un pipeline con solicitudes activas'
                })
            
            pipeline.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_etapa')
def api_obtener_etapas(request, pipeline_id):
    """API para obtener etapas de un pipeline"""
    try:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        etapas = pipeline.etapas.all().order_by('orden')
        
        datos_etapas = []
        for etapa in etapas:
            datos_etapas.append({
                'id': etapa.id,
                'nombre': etapa.nombre,
                'orden': etapa.orden,
                'sla': str(etapa.sla),
                'es_bandeja_grupal': etapa.es_bandeja_grupal,
                'subestados': list(etapa.subestados.values('id', 'nombre', 'orden')),
                'permisos': list(etapa.permisos.values('grupo__name', 'puede_ver', 'puede_autoasignar'))
            })
        
        return JsonResponse({
            'success': True,
            'pipeline_nombre': pipeline.nombre,
            'etapas': datos_etapas
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@superuser_permission_required('workflow.add_etapa')
def api_crear_etapa(request, pipeline_id):
    """API para crear una nueva etapa"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            nombre = request.POST.get('nombre')
            orden = request.POST.get('orden')
            sla_horas = request.POST.get('sla_horas', 24)
            es_bandeja_grupal = request.POST.get('es_bandeja_grupal') == 'true'
            
            if not nombre or not orden:
                return JsonResponse({'success': False, 'error': 'Nombre y orden son obligatorios'})
            
            # Convertir SLA a timedelta
            sla = timedelta(hours=int(sla_horas))
            
            etapa = Etapa.objects.create(
                pipeline=pipeline,
                nombre=nombre,
                orden=int(orden),
                sla=sla,
                es_bandeja_grupal=es_bandeja_grupal
            )
            
            return JsonResponse({
                'success': True,
                'etapa': {
                    'id': etapa.id,
                    'nombre': etapa.nombre,
                    'orden': etapa.orden,
                    'sla': str(etapa.sla),
                    'es_bandeja_grupal': etapa.es_bandeja_grupal
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.change_etapa')
def api_editar_etapa(request, etapa_id):
    """API para editar una etapa"""
    if request.method == 'POST':
        try:
            etapa = get_object_or_404(Etapa, id=etapa_id)
            
            nombre = request.POST.get('nombre')
            orden = request.POST.get('orden')
            sla_horas = request.POST.get('sla_horas', 24)
            es_bandeja_grupal = request.POST.get('es_bandeja_grupal') == 'true'
            
            if not nombre or not orden:
                return JsonResponse({'success': False, 'error': 'Nombre y orden son obligatorios'})
            
            # Convertir SLA a timedelta
            sla = timedelta(hours=int(sla_horas))
            
            etapa.nombre = nombre
            etapa.orden = int(orden)
            etapa.sla = sla
            etapa.es_bandeja_grupal = es_bandeja_grupal
            etapa.save()
            
            return JsonResponse({
                'success': True,
                'etapa': {
                    'id': etapa.id,
                    'nombre': etapa.nombre,
                    'orden': etapa.orden,
                    'sla': str(etapa.sla),
                    'es_bandeja_grupal': etapa.es_bandeja_grupal
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.delete_etapa')
def api_eliminar_etapa(request, etapa_id):
    """API para eliminar una etapa"""
    if request.method == 'POST':
        try:
            etapa = get_object_or_404(Etapa, id=etapa_id)
            
            # Verificar que no hay solicitudes en esta etapa
            if etapa.solicitud_set.exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar una etapa con solicitudes activas'
                })
            
            etapa.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_subestado')
def api_crear_subestado(request, etapa_id):
    """API para crear un subestado"""
    if request.method == 'POST':
        try:
            etapa = get_object_or_404(Etapa, id=etapa_id)
            
            nombre = request.POST.get('nombre')
            orden = request.POST.get('orden', 0)
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            subestado = SubEstado.objects.create(
                etapa=etapa,
                pipeline=etapa.pipeline,
                nombre=nombre,
                orden=int(orden)
            )
            
            return JsonResponse({
                'success': True,
                'subestado': {
                    'id': subestado.id,
                    'nombre': subestado.nombre,
                    'orden': subestado.orden
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_transicionetapa')
def api_crear_transicion(request, pipeline_id):
    """API para crear una transición"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            etapa_origen_id = request.POST.get('etapa_origen')
            etapa_destino_id = request.POST.get('etapa_destino')
            nombre = request.POST.get('nombre')
            requiere_permiso = request.POST.get('requiere_permiso') == 'true'
            
            if not all([etapa_origen_id, etapa_destino_id, nombre]):
                return JsonResponse({'success': False, 'error': 'Todos los campos son obligatorios'})
            
            etapa_origen = get_object_or_404(Etapa, id=etapa_origen_id, pipeline=pipeline)
            etapa_destino = get_object_or_404(Etapa, id=etapa_destino_id, pipeline=pipeline)
            
            transicion = TransicionEtapa.objects.create(
                pipeline=pipeline,
                etapa_origen=etapa_origen,
                etapa_destino=etapa_destino,
                nombre=nombre,
                requiere_permiso=requiere_permiso
            )
            
            return JsonResponse({
                'success': True,
                'transicion': {
                    'id': transicion.id,
                    'nombre': transicion.nombre,
                    'etapa_origen': transicion.etapa_origen.nombre,
                    'etapa_destino': transicion.etapa_destino.nombre,
                    'requiere_permiso': transicion.requiere_permiso
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_requisito')
def api_crear_requisito(request):
    """API para crear un requisito"""
    if request.method == 'POST':
        try:
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            
            if not nombre:
                return JsonResponse({'success': False, 'error': 'El nombre es obligatorio'})
            
            requisito = Requisito.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            
            return JsonResponse({
                'success': True,
                'requisito': {
                    'id': requisito.id,
                    'nombre': requisito.nombre,
                    'descripcion': requisito.descripcion
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_requisitopipeline')
def api_asignar_requisito_pipeline(request, pipeline_id):
    """API para asignar un requisito a un pipeline"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            requisito_id = request.POST.get('requisito_id')
            obligatorio = request.POST.get('obligatorio') == 'true'
            
            if not requisito_id:
                return JsonResponse({'success': False, 'error': 'El requisito es obligatorio'})
            
            requisito = get_object_or_404(Requisito, id=requisito_id)
            
            requisito_pipeline, created = RequisitoPipeline.objects.get_or_create(
                pipeline=pipeline,
                requisito=requisito,
                defaults={'obligatorio': obligatorio}
            )
            
            if not created:
                requisito_pipeline.obligatorio = obligatorio
                requisito_pipeline.save()
            
            return JsonResponse({
                'success': True,
                'requisito_pipeline': {
                    'id': requisito_pipeline.id,
                    'requisito_nombre': requisito.nombre,
                    'obligatorio': requisito_pipeline.obligatorio
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.add_campopersonalizado')
def api_crear_campo_personalizado(request, pipeline_id):
    """API para crear un campo personalizado"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            nombre = request.POST.get('nombre')
            tipo = request.POST.get('tipo')
            requerido = request.POST.get('requerido') == 'true'
            
            if not all([nombre, tipo]):
                return JsonResponse({'success': False, 'error': 'Nombre y tipo son obligatorios'})
            
            campo = CampoPersonalizado.objects.create(
                pipeline=pipeline,
                nombre=nombre,
                tipo=tipo,
                requerido=requerido
            )
            
            return JsonResponse({
                'success': True,
                'campo': {
                    'id': campo.id,
                    'nombre': campo.nombre,
                    'tipo': campo.tipo,
                    'requerido': campo.requerido
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.delete_transicionetapa')
def api_eliminar_transicion(request, transicion_id):
    """API para eliminar una transición"""
    if request.method == 'POST':
        try:
            transicion = get_object_or_404(TransicionEtapa, id=transicion_id)
            
            # Verificar que no hay solicitudes usando esta transición
            if transicion.solicitud_set.exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar una transición que está siendo utilizada'
                })
            
            transicion.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.change_transicionetapa')
def api_editar_transicion(request, transicion_id):
    """API para editar una transición"""
    if request.method == 'POST':
        try:
            transicion = get_object_or_404(TransicionEtapa, id=transicion_id)
            
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            etapa_origen_id = request.POST.get('etapa_origen')
            etapa_destino_id = request.POST.get('etapa_destino')
            
            # Validaciones
            if not nombre or not etapa_origen_id or not etapa_destino_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'Todos los campos son obligatorios'
                })
            
            if etapa_origen_id == etapa_destino_id:
                return JsonResponse({
                    'success': False, 
                    'error': 'El origen y destino no pueden ser la misma etapa'
                })
            
            # Verificar que las etapas existen y pertenecen al mismo pipeline
            try:
                etapa_origen = Etapa.objects.get(id=etapa_origen_id, pipeline=transicion.pipeline)
                etapa_destino = Etapa.objects.get(id=etapa_destino_id, pipeline=transicion.pipeline)
            except Etapa.DoesNotExist:
                return JsonResponse({
                    'success': False, 
                    'error': 'Una o ambas etapas no existen o no pertenecen al pipeline'
                })
            
            # Verificar que no hay otra transición con el mismo origen y destino
            transicion_existente = TransicionEtapa.objects.filter(
                pipeline=transicion.pipeline,
                etapa_origen=etapa_origen,
                etapa_destino=etapa_destino
            ).exclude(id=transicion_id).first()
            
            if transicion_existente:
                return JsonResponse({
                    'success': False, 
                    'error': 'Ya existe una transición entre estas etapas'
                })
            
            # Actualizar la transición
            transicion.nombre = nombre
            transicion.etapa_origen = etapa_origen
            transicion.etapa_destino = etapa_destino
            transicion.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.delete_requisitopipeline')
def api_eliminar_requisito_pipeline(request, requisito_pipeline_id):
    """API para eliminar un requisito de un pipeline"""
    if request.method == 'POST':
        try:
            requisito_pipeline = get_object_or_404(RequisitoPipeline, id=requisito_pipeline_id)
            
            # Verificar que no hay solicitudes con este requisito
            if RequisitoSolicitud.objects.filter(requisito_pipeline=requisito_pipeline).exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar un requisito que está siendo utilizado'
                })
            
            requisito_pipeline.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.change_requisitopipeline')
def api_editar_requisito_pipeline(request, requisito_pipeline_id):
    """API para editar un requisito de un pipeline"""
    if request.method == 'POST':
        try:
            requisito_pipeline = get_object_or_404(RequisitoPipeline, id=requisito_pipeline_id)
            
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            descripcion = request.POST.get('descripcion', '')
            obligatorio = request.POST.get('obligatorio') == 'on'
            
            # Validaciones
            if not nombre:
                return JsonResponse({
                    'success': False, 
                    'error': 'El nombre es obligatorio'
                })
            
            # Actualizar el requisito base
            requisito = requisito_pipeline.requisito
            requisito.nombre = nombre
            requisito.descripcion = descripcion
            requisito.save()
            
            # Actualizar el requisito del pipeline
            requisito_pipeline.obligatorio = obligatorio
            requisito_pipeline.save()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@superuser_permission_required('workflow.delete_campopersonalizado')
def api_eliminar_campo_personalizado(request, campo_id):
    """API para eliminar un campo personalizado"""
    if request.method == 'POST':
        try:
            campo = get_object_or_404(CampoPersonalizado, id=campo_id)
            
            # Verificar que no hay solicitudes con este campo
            if campo.valorcampopersonalizado_set.exists():
                return JsonResponse({
                    'success': False, 
                    'error': 'No se puede eliminar un campo que está siendo utilizado'
                })
            
            campo.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_obtener_datos_pipeline(request, pipeline_id):
    """API para obtener todos los datos de un pipeline"""
    try:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        
        # Etapas
        etapas = pipeline.etapas.all().order_by('orden')
        datos_etapas = []
        for etapa in etapas:
            datos_etapas.append({
                'id': etapa.id,
                'nombre': etapa.nombre,
                'orden': etapa.orden,
                'sla': str(etapa.sla),
                'es_bandeja_grupal': etapa.es_bandeja_grupal,
                'subestados': list(etapa.subestados.values('id', 'nombre', 'orden')),
                'permisos': list(etapa.permisos.values('grupo__name', 'puede_ver', 'puede_autoasignar'))
            })
        
        # Transiciones
        transiciones = pipeline.transiciones.all()
        datos_transiciones = []
        for transicion in transiciones:
            datos_transiciones.append({
                'id': transicion.id,
                'nombre': transicion.nombre,
                'etapa_origen': transicion.etapa_origen.nombre,
                'etapa_destino': transicion.etapa_destino.nombre,
                'etapa_origen_id': transicion.etapa_origen.id,
                'etapa_destino_id': transicion.etapa_destino.id,
                'requiere_permiso': transicion.requiere_permiso
            })
        
        # Requisitos
        requisitos_pipeline = pipeline.requisitos_pipeline.all().select_related('requisito')
        datos_requisitos = []
        for req_pipeline in requisitos_pipeline:
            datos_requisitos.append({
                'id': req_pipeline.id,
                'requisito_nombre': req_pipeline.requisito.nombre,
                'requisito_descripcion': req_pipeline.requisito.descripcion or '',
                'obligatorio': req_pipeline.obligatorio
            })
        
        # Campos personalizados
        campos = pipeline.campos_personalizados.all()
        datos_campos = []
        for campo in campos:
            datos_campos.append({
                'id': campo.id,
                'nombre': campo.nombre,
                'tipo': campo.tipo,
                'requerido': campo.requerido
            })
        
        return JsonResponse({
            'success': True,
            'pipeline': {
                'id': pipeline.id,
                'nombre': pipeline.nombre,
                'descripcion': pipeline.descripcion
            },
            'etapas': datos_etapas,
            'transiciones': datos_transiciones,
            'requisitos': datos_requisitos,
            'campos_personalizados': datos_campos
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==========================================
# VISTAS DE API
# ==========================================

def api_solicitudes(request):
    """API para obtener solicitudes"""
    
    solicitudes = Solicitud.objects.all().select_related(
        'pipeline', 'etapa_actual', 'subestado_actual', 'creada_por', 'asignada_a'
    )
    
    # Filtros
    pipeline_id = request.GET.get('pipeline')
    if pipeline_id:
        solicitudes = solicitudes.filter(pipeline_id=pipeline_id)
    
    estado = request.GET.get('estado')
    if estado == 'activas':
        solicitudes = solicitudes.filter(etapa_actual__isnull=False)
    elif estado == 'completadas':
        solicitudes = solicitudes.filter(etapa_actual__isnull=True)
    
    # Serializar datos
    datos = []
    for solicitud in solicitudes:
        datos.append({
            'id': solicitud.id,
            'codigo': solicitud.codigo,
            'pipeline': solicitud.pipeline.nombre,
            'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
            'subestado_actual': solicitud.subestado_actual.nombre if solicitud.subestado_actual else None,
            'creada_por': solicitud.creada_por.username,
            'asignada_a': solicitud.asignada_a.username if solicitud.asignada_a else None,
            'fecha_creacion': solicitud.fecha_creacion.isoformat(),
            'fecha_ultima_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
        })
    
    return JsonResponse({'solicitudes': datos})


def api_estadisticas(request):
    """API para obtener estadísticas"""
    
    # Estadísticas básicas
    total_solicitudes = Solicitud.objects.count()
    solicitudes_activas = Solicitud.objects.filter(etapa_actual__isnull=False).count()
    solicitudes_completadas = Solicitud.objects.filter(etapa_actual__isnull=True).count()
    
    # Solicitudes por pipeline
    solicitudes_por_pipeline = Pipeline.objects.annotate(
        total=Count('solicitud')
    ).values('nombre', 'total')
    
    # Solicitudes vencidas - Calculamos usando Python para compatibilidad con SQLite
    solicitudes_vencidas = 0
    for solicitud in Solicitud.objects.filter(etapa_actual__isnull=False).select_related('etapa_actual'):
        if solicitud.etapa_actual and solicitud.etapa_actual.sla:
            fecha_limite = solicitud.fecha_ultima_actualizacion + solicitud.etapa_actual.sla
            if timezone.now() > fecha_limite:
                solicitudes_vencidas += 1
    
    return JsonResponse({
        'total_solicitudes': total_solicitudes,
        'solicitudes_activas': solicitudes_activas,
        'solicitudes_completadas': solicitudes_completadas,
        'solicitudes_vencidas': solicitudes_vencidas,
        'solicitudes_por_pipeline': list(solicitudes_por_pipeline),
    })


def sitio_construccion(request):
    """Vista para página de sitio en construcción"""
    return render(request, 'workflow/sitio_construccion.html')


@login_required
def api_actualizar_prioridad(request, solicitud_id):
    """API para actualizar la prioridad de una solicitud"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            prioridad = data.get('prioridad', '').strip()
            solicitud = get_object_or_404(Solicitud, id=solicitud_id)
            # Eliminar validación de permisos, permitir a cualquier usuario
            prioridades_validas = ['Alta', 'Media', 'Baja']
            if prioridad and prioridad not in prioridades_validas:
                return JsonResponse({'success': False, 'error': 'Prioridad no válida'})
            solicitud.prioridad = prioridad
            solicitud.save()
            return JsonResponse({'success': True, 'prioridad': prioridad})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_actualizar_etiquetas(request, solicitud_id):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        etiquetas = data.get('etiquetas_oficial', '')
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        # Limpiar espacios de cada etiqueta
        etiquetas_limpias = ','.join([e.strip() for e in etiquetas.split(',') if e.strip()])
        solicitud.etiquetas_oficial = etiquetas_limpias
        solicitud.save()
        return JsonResponse({'success': True, 'etiquetas_oficial': etiquetas_limpias})
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_buscar_clientes(request):
    """API para buscar clientes"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        if not query:
            return JsonResponse({'clientes': []})
        
        # Buscar clientes por nombre o cédula
        clientes = Cliente.objects.filter(
            Q(nombreCliente__icontains=query) | 
            Q(cedulaCliente__icontains=query)
        ).order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cliente in clientes:
            resultados.append({
                'id': cliente.id,
                'nombre': cliente.nombreCliente or 'Sin nombre',
                'cedula': cliente.cedulaCliente or 'Sin cédula',
                'fecha_creacion': cliente.created_at.strftime('%d/%m/%Y') if cliente.created_at else '',
                'texto_completo': f"{cliente.nombreCliente or 'Sin nombre'} - {cliente.cedulaCliente or 'Sin cédula'}"
            })
        
        return JsonResponse({'clientes': resultados})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def api_buscar_cotizaciones(request):
    """API para buscar cotizaciones"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        cliente_id = request.GET.get('cliente_id', '').strip()
        limit = int(request.GET.get('limit', 20))
        
        # Filtrar cotizaciones
        cotizaciones = Cotizacion.objects.all()
        
        # Filtrar por cliente si se especifica
        if cliente_id:
            cotizaciones = cotizaciones.filter(cedulaCliente=cliente_id)
        
        # Buscar por número de cotización, nombre de cliente o monto
        if query:
            cotizaciones = cotizaciones.filter(
                Q(NumeroCotizacion__icontains=query) |
                Q(nombreCliente__icontains=query) |
                Q(montoPrestamo__icontains=query)
            )
        
        cotizaciones = cotizaciones.order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cotizacion in cotizaciones:
            # Use auxMonto2 as "Monto Financiado" instead of montoPrestamo
            monto_financiado = cotizacion.auxMonto2 or cotizacion.montoPrestamo or 0
            resultados.append({
                'id': cotizacion.id,
                'numero': cotizacion.NumeroCotizacion or cotizacion.id,
                'cliente': cotizacion.nombreCliente or 'Sin cliente',
                'monto_financiado': float(monto_financiado),
                'tipo': cotizacion.tipoPrestamo or 'Sin tipo',
                'fecha_creacion': cotizacion.created_at.strftime('%d/%m/%Y') if cotizacion.created_at else '',
                'texto_completo': f"#{cotizacion.NumeroCotizacion or cotizacion.id} - {cotizacion.nombreCliente or 'Sin cliente'} - Monto Financiado: ${monto_financiado}"
            })
        
        return JsonResponse({'cotizaciones': resultados})
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)


@login_required
def api_buscar_cotizaciones_drawer(request):
    """API para buscar cotizaciones en el drawer - solo Préstamos de Auto"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        if not query:
            return JsonResponse({'success': True, 'cotizaciones': []})
        
        # Base query - SOLO PRÉSTAMOS DE AUTO
        cotizaciones = Cotizacion.objects.filter(
            Q(nombreCliente__icontains=query) | 
            Q(cedulaCliente__icontains=query) |
            Q(id__icontains=query),
            tipoPrestamo='auto'  # Solo cotizaciones de préstamos de auto
        )
        
        # Filtrar por permisos de usuario
        if not (request.user.is_superuser or request.user.is_staff):
            # Usuarios regulares solo ven sus propias cotizaciones
            cotizaciones = cotizaciones.filter(added_by=request.user)
        
        # Ordenar y limitar resultados
        cotizaciones = cotizaciones.order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cotizacion in cotizaciones:
            resultado = {
                'id': cotizacion.id,
                'nombreCliente': cotizacion.nombreCliente or 'Sin nombre',
                'cedulaCliente': cotizacion.cedulaCliente or 'Sin cédula',
                'tipoPrestamo': cotizacion.tipoPrestamo or 'Sin tipo',
                'montoFinanciado': float(cotizacion.auxMonto2) if cotizacion.auxMonto2 else 0,  # Monto Financiado
                'oficial': cotizacion.oficial or 'Sin oficial',
                'observaciones': cotizacion.observaciones or '',  # Campo observaciones
                'created_at': cotizacion.created_at.isoformat() if cotizacion.created_at else None,
                # Vehicle data for SURA auto-population
                'valorAuto': float(cotizacion.valorAuto) if cotizacion.valorAuto else None,
                'yearCarro': cotizacion.yearCarro,
                'marca': cotizacion.marca or '',
                'modelo': cotizacion.modelo or '',
                'tipoDocumento': cotizacion.tipoDocumento or 'CEDULA'
            }
            print(f"🔧 DEBUG: Cotización {cotizacion.id} observaciones: '{cotizacion.observaciones}'")
            print(f"🔧 DEBUG: Cotización {cotizacion.id} observaciones type: {type(cotizacion.observaciones)}")
            print(f"🔧 DEBUG: Cotización {cotizacion.id} observaciones length: {len(cotizacion.observaciones) if cotizacion.observaciones else 0}")
            print(f"🔧 DEBUG: Cotización {cotizacion.id} vehicle data: valorAuto={cotizacion.valorAuto}, yearCarro={cotizacion.yearCarro}, marca={cotizacion.marca}, modelo={cotizacion.modelo}")
            resultados.append(resultado)
        
        return JsonResponse({'success': True, 'cotizaciones': resultados})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_buscar_clientes_drawer(request):
    """API para buscar clientes en el drawer"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        if not query:
            return JsonResponse({'success': True, 'clientes': []})
        
        # Buscar clientes por nombre o cédula
        clientes = Cliente.objects.filter(
            Q(nombreCliente__icontains=query) | 
            Q(cedulaCliente__icontains=query)
        ).order_by('-created_at')[:limit]
        
        # Serializar resultados
        resultados = []
        for cliente in clientes:
            resultados.append({
                'id': cliente.id,
                'nombreCliente': cliente.nombreCliente or 'Sin nombre',
                'cedulaCliente': cliente.cedulaCliente or 'Sin cédula',
                'edad': cliente.edad or 'Sin edad',
                'sexo': cliente.sexo or 'Sin sexo'
            })
        
        return JsonResponse({'success': True, 'clientes': resultados})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def api_formulario_datos(request):
    """API para obtener datos del formulario basado en el pipeline"""
    if request.method == 'GET':
        pipeline_id = request.GET.get('pipeline_id')
        
        if not pipeline_id:
            return JsonResponse({'success': False, 'error': 'ID de pipeline requerido'})
        
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            
            # Obtener campos personalizados del pipeline
            campos_personalizados = CampoPersonalizado.objects.filter(
                pipeline=pipeline
            ).values('id', 'nombre', 'tipo', 'requerido', 'descripcion')
            
            # Obtener requisitos del pipeline
            requisitos_pipeline = RequisitoPipeline.objects.filter(
                pipeline=pipeline
            ).select_related('requisito')
            
            requisitos = []
            for req_pipeline in requisitos_pipeline:
                requisitos.append({
                    'id': req_pipeline.requisito.id,
                    'nombre': req_pipeline.requisito.nombre,
                    'descripcion': req_pipeline.requisito.descripcion,
                    'obligatorio': req_pipeline.obligatorio
                })
            
            return JsonResponse({
                'success': True,
                'campos_personalizados': list(campos_personalizados),
                'requisitos': requisitos
            })
            
        except Pipeline.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Pipeline no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# Sistema de notificaciones en tiempo real
class NotificationManager:
    def __init__(self):
        self.clients = {}
        self.last_update = {}
    
    def add_client(self, user_id, response_queue):
        """Agregar cliente para notificaciones"""
        self.clients[user_id] = response_queue
        self.last_update[user_id] = timezone.now()
    
    def remove_client(self, user_id):
        """Remover cliente"""
        if user_id in self.clients:
            del self.clients[user_id]
        if user_id in self.last_update:
            del self.last_update[user_id]
    
    def notify_change(self, change_type, data, affected_users=None):
        """Notificar cambio a usuarios específicos o todos"""
        if affected_users is None:
            affected_users = list(self.clients.keys())
        
        notification = {
            'type': change_type,
            'data': data,
            'timestamp': timezone.now().isoformat()
        }
        
        for user_id in affected_users:
            if user_id in self.clients:
                try:
                    self.clients[user_id].put(notification)
                except:
                    # Cliente desconectado, remover
                    self.remove_client(user_id)

# Instancia global del manager
notification_manager = NotificationManager()

@login_required
def api_notifications_stream(request):
    """API de Server-Sent Events para notificaciones en tiempo real"""
    def event_stream():
        user_id = request.user.id
        response_queue = queue.Queue()
        
        # Agregar cliente
        notification_manager.add_client(user_id, response_queue)
        
        try:
            # Enviar evento inicial
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Conectado a notificaciones'})}\n\n"
            
            while True:
                try:
                    # Esperar por notificaciones con timeout
                    notification = response_queue.get(timeout=30)
                    yield f"data: {json.dumps(notification)}\n\n"
                except queue.Empty:
                    # Enviar heartbeat cada 30 segundos
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': timezone.now().isoformat()})}\n\n"
                except:
                    break
        finally:
            # Limpiar cliente al desconectar
            notification_manager.remove_client(user_id)
    
    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['Connection'] = 'keep-alive'
    response['Access-Control-Allow-Origin'] = '*'
    return response

@login_required
def api_check_updates(request):
    """API mejorada para verificar actualizaciones con detección inteligente"""
    print(f"🔍 DEBUG: api_check_updates llamado por usuario: {request.user.username}")
    print(f"🔍 DEBUG: Método: {request.method}")
    print(f"🔍 DEBUG: Parámetros: {request.GET}")
    
    try:
        # Obtener timestamp de la última actualización del usuario
        last_check = request.GET.get('last_check')
        if last_check:
            try:
                last_check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            except:
                last_check_time = timezone.now() - timedelta(minutes=5)
        else:
            last_check_time = timezone.now() - timedelta(minutes=5)
        
        # Obtener vista actual para filtros específicos
        current_view = request.GET.get('view', 'bandejas')  # bandejas, tabla, kanban
        
        # Solicitudes del usuario según sus grupos
        solicitudes_base = Solicitud.objects.filter(
            etapa_actual__pipeline__grupos__in=request.user.groups.all()
        ).select_related('etapa_actual', 'asignada_a', 'pipeline')
        
        # Verificar cambios específicos por tipo de vista
        cambios_detectados = []
        
        # 1. Cambios en bandeja grupal (para vista bandejas)
        if current_view in ['bandejas', 'all']:
            solicitudes_grupales_nuevas = solicitudes_base.filter(
                etapa_actual__es_bandeja_grupal=True,
                asignada_a__isnull=True,
                fecha_ultima_actualizacion__gt=last_check_time
            ).count()
            
            if solicitudes_grupales_nuevas > 0:
                cambios_detectados.append({
                    'tipo': 'bandeja_grupal',
                    'count': solicitudes_grupales_nuevas
                })
        
        # 2. Cambios en tareas personales (para vista bandejas)
        if current_view in ['bandejas', 'all']:
            solicitudes_personales_nuevas = solicitudes_base.filter(
                asignada_a=request.user,
                fecha_ultima_actualizacion__gt=last_check_time
            ).count()
            
            if solicitudes_personales_nuevas > 0:
                cambios_detectados.append({
                    'tipo': 'bandeja_personal',
                    'count': solicitudes_personales_nuevas
                })
        
        # 3. Cambios generales en solicitudes (para tabla/kanban)
        if current_view in ['tabla', 'kanban', 'all']:
            solicitudes_actualizadas = solicitudes_base.filter(
                fecha_ultima_actualizacion__gt=last_check_time
            ).count()
            
            if solicitudes_actualizadas > 0:
                cambios_detectados.append({
                    'tipo': 'solicitudes_generales',
                    'count': solicitudes_actualizadas
                })
        
        # 4. Nuevas solicitudes creadas
        nuevas_solicitudes = solicitudes_base.filter(
            fecha_creacion__gt=last_check_time
        ).count()
        
        if nuevas_solicitudes > 0:
            cambios_detectados.append({
                'tipo': 'nuevas_solicitudes',
                'count': nuevas_solicitudes
            })
        
        # Obtener detalles de cambios para debugging
        solicitudes_modificadas = list(solicitudes_base.filter(
            fecha_ultima_actualizacion__gt=last_check_time
        ).values('id', 'codigo', 'etapa_actual__nombre', 'asignada_a__username')[:10])
        
        has_updates = len(cambios_detectados) > 0
        
        return JsonResponse({
            'success': True,
            'has_updates': has_updates,
            'cambios_detectados': cambios_detectados,
            'total_cambios': sum(c['count'] for c in cambios_detectados),
            'nuevas_solicitudes': nuevas_solicitudes,
            'solicitudes_modificadas': solicitudes_modificadas,
            'timestamp': timezone.now().isoformat(),
            'last_check': last_check_time.isoformat(),
            'view': current_view
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        })

# Función para notificar cambios automáticamente
def notify_solicitud_change(solicitud, change_type, user=None):
    """Notificar cambio en solicitud a usuarios relevantes"""
    try:
        # Obtener usuarios que deben ser notificados
        affected_users = []
        
        # Usuarios del grupo de la etapa actual
        if solicitud.etapa_actual:
            group_users = User.objects.filter(
                groups__in=solicitud.etapa_actual.pipeline.grupos.all()
            ).values_list('id', flat=True)
            affected_users.extend(group_users)
        
        # Usuario asignado
        if solicitud.asignada_a:
            affected_users.append(solicitud.asignada_a.id)
        
        # Datos de la notificación
        notification_data = {
            'solicitud_id': solicitud.id,
            'codigo': solicitud.codigo,
            'etapa_actual': {
                'id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
                'nombre': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
                'es_bandeja_grupal': solicitud.etapa_actual.es_bandeja_grupal if solicitud.etapa_actual else False
            },
            'asignada_a': {
                'id': solicitud.asignada_a.id if solicitud.asignada_a else None,
                'username': solicitud.asignada_a.username if solicitud.asignada_a else None,
                'nombre_completo': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else None
            },
            'user_action': {
                'id': user.id if user else None,
                'username': user.username if user else None,
                'nombre_completo': user.get_full_name() if user else None
            },
            'pipeline_id': solicitud.pipeline.id if solicitud.pipeline else None,
            'timestamp': timezone.now().isoformat()
        }
        
        # Enviar notificación
        notification_manager.notify_change(change_type, notification_data, affected_users)
        
    except Exception as e:
        print(f"Error notificando cambio: {e}")

def enviar_correo_bandeja_grupal(solicitud, etapa, request=None):
    """
    Función para enviar correo automático cuando una solicitud entra a una etapa de bandeja grupal.
    Basada en la implementación de correos de la app tómbola.
    """
    try:
        # Obtener usuarios que tienen acceso a esta etapa dinámicamente
        destinatarios = []
        
        # Obtener permisos de bandeja para esta etapa
        permisos_bandeja = PermisoBandeja.objects.filter(
            etapa=etapa,
            puede_ver=True  # Solo usuarios que pueden ver la bandeja
        ).select_related('grupo', 'usuario')
        
        # Recopilar emails de usuarios con acceso
        emails_set = set()  # Usar set para evitar duplicados
        
        for permiso in permisos_bandeja:
            if permiso.usuario and permiso.usuario.email:
                # Permiso directo a usuario
                emails_set.add(permiso.usuario.email)
                print(f"📧 Usuario directo agregado: {permiso.usuario.email}")
            elif permiso.grupo:
                # Permiso a grupo - obtener todos los usuarios del grupo
                usuarios_grupo = permiso.grupo.user_set.filter(
                    is_active=True,
                    email__isnull=False,
                    email__gt=''  # Email no vacío
                )
                for usuario in usuarios_grupo:
                    emails_set.add(usuario.email)
                    print(f"📧 Usuario del grupo '{permiso.grupo.name}' agregado: {usuario.email}")
        
        destinatarios = list(emails_set)
        
        if not destinatarios:
            print(f"⚠️ No se encontraron destinatarios para la etapa '{etapa.nombre}'. Verificar permisos de bandeja.")
            return
        
        print(f"📧 Total de {len(destinatarios)} destinatario(s) encontrado(s) para la etapa '{etapa.nombre}': {destinatarios}")
        
        # Construir la URL de la bandeja usando la función dinámica
        base_url = get_site_url(request)
        bandeja_url = f"{base_url}/workflow/bandejas/?etapa_id={etapa.id}"
        
        # Obtener nombre del cliente
        cliente_nombre = ""
        try:
            if hasattr(solicitud, 'cliente') and solicitud.cliente:
                cliente_nombre = getattr(solicitud.cliente, 'nombreCliente', 'Sin nombre')
            elif hasattr(solicitud, 'cotizacion') and solicitud.cotizacion and solicitud.cotizacion.cliente:
                cliente_nombre = getattr(solicitud.cotizacion.cliente, 'nombreCliente', 'Sin nombre')
            else:
                cliente_nombre = "Cliente no asignado"
        except Exception as e:
            print(f"⚠️ Error obteniendo nombre del cliente: {e}")
            cliente_nombre = "Error al obtener cliente"
        
        # Contexto para el template
        context = {
            'solicitud': solicitud,
            'etapa': etapa,
            'cliente_nombre': cliente_nombre,
            'bandeja_url': bandeja_url,
        }
        
        # Cargar el template HTML
        html_content = render_to_string('workflow/emails/bandeja_grupal_notification.html', context)
        
        # Crear el asunto
        subject = f"🔔 Nueva Solicitud en Bandeja Grupal - {solicitud.codigo}"
        
        # Mensaje de texto plano como respaldo
        text_content = f"""
        Nueva Solicitud en Bandeja Grupal
        
        Hola equipo,
        
        Una solicitud ha ingresado a una etapa de bandeja grupal y requiere atención:
        
        • Código: {solicitud.codigo}
        • Cliente: {cliente_nombre or 'Sin asignar'}
        • Pipeline: {solicitud.pipeline.nombre}
        • Etapa: {etapa.nombre}
        • Creada por: {solicitud.creada_por.get_full_name() or solicitud.creada_por.username}
        • Fecha: {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        
        Para ver la solicitud, haz clic en el siguiente enlace:
        {bandeja_url}
        
        Saludos,
        Sistema de Workflow - Financiera Pacífico
        
        ---
        Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=destinatarios,
        )
        
        # Agregar el contenido HTML
        email.attach_alternative(html_content, "text/html")
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
        
        print(f"✅ Correo enviado correctamente para solicitud {solicitud.codigo} - Etapa: {etapa.nombre} - Enviado a {len(destinatarios)} destinatario(s)")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo para solicitud {solicitud.codigo}: {str(e)}")


def enviar_correo_solicitud_asignada(solicitud, usuario_asignado, request=None):
    """
    Función para enviar correo automático cuando una solicitud es asignada a un usuario.
    Notifica al creador de la solicitud que su solicitud ha sido tomada.
    """
    try:
        # Verificar que la solicitud tiene un creador
        if not solicitud.creada_por or not solicitud.creada_por.email:
            print(f"⚠️ No se puede enviar correo: solicitud {solicitud.codigo} sin creador o email")
            return
        
        # Obtener información del cliente
        cliente_nombre = ""
        try:
            if hasattr(solicitud, 'cliente') and solicitud.cliente:
                cliente_nombre = getattr(solicitud.cliente, 'nombreCliente', 'Sin nombre')
            elif hasattr(solicitud, 'cotizacion') and solicitud.cotizacion and solicitud.cotizacion.cliente:
                cliente_nombre = getattr(solicitud.cotizacion.cliente, 'nombreCliente', 'Sin nombre')
            else:
                cliente_nombre = "Cliente no asignado"
        except Exception as e:
            print(f"⚠️ Error obteniendo nombre del cliente: {e}")
            cliente_nombre = "Error al obtener cliente"
        
        # Construir la URL de la solicitud usando la función dinámica
        base_url = get_site_url(request)
        solicitud_url = f"{base_url}/workflow/solicitud/{solicitud.id}/"
        
        # Contexto para el template
        context = {
            'solicitud': solicitud,
            'usuario_asignado': usuario_asignado,
            'cliente_nombre': cliente_nombre,
            'solicitud_url': solicitud_url,
        }
        
        # Cargar el template HTML
        html_content = render_to_string('workflow/emails/solicitud_asignada_notification.html', context)
        
        # Crear el asunto
        subject = f"✅ Tu solicitud ha sido asignada - {solicitud.codigo}"
        
        # Mensaje de texto plano como respaldo
        text_content = f"""
        Tu Solicitud Ha Sido Asignada
        
        Hola {solicitud.creada_por.get_full_name() or solicitud.creada_por.username},
        
        Tu solicitud ha sido asignada a un usuario y está siendo procesada:
        
        • Código: {solicitud.codigo}
        • Cliente: {cliente_nombre or 'Sin asignar'}
        • Pipeline: {solicitud.pipeline.nombre}
        • Etapa: {solicitud.etapa_actual.nombre}
        • Asignada a: {usuario_asignado.get_full_name() or usuario_asignado.username}
        • Fecha de asignación: {timezone.now().strftime('%d/%m/%Y %H:%M')}
        
        Para ver el estado de tu solicitud, haz clic en el siguiente enlace:
        {solicitud_url}
        
        Saludos,
        Sistema de Workflow - Financiera Pacífico
        
        ---
        Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=[solicitud.creada_por.email],
        )
        
        # Agregar el contenido HTML
        email.attach_alternative(html_content, "text/html")
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
        
        print(f"✅ Correo de asignación enviado correctamente para solicitud {solicitud.codigo} - Asignada a: {usuario_asignado.username}, correo enviado a: {solicitud.creada_por.email}")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo de asignación para solicitud {solicitud.codigo}: {str(e)}")


def enviar_correo_cambio_etapa_propietario(solicitud, etapa_anterior, nueva_etapa, comentarios_analista, bullet_points, analisis_general, usuario_que_cambio, request=None):
    """
    Función para enviar correo automático al propietario de la solicitud cuando cambia de etapa.
    Incluye análisis general, comentarios del analista y bullet points estructurados.
    """
    try:
        # Verificar que la solicitud tiene un creador
        if not solicitud.creada_por or not solicitud.creada_por.email:
            print(f"⚠️ No se puede enviar correo: solicitud {solicitud.codigo} sin creador o email")
            return
        
        # Obtener información del cliente
        cliente_nombre = ""
        try:
            if hasattr(solicitud, 'cliente') and solicitud.cliente:
                cliente_nombre = getattr(solicitud.cliente, 'nombreCliente', 'Sin nombre')
            elif hasattr(solicitud, 'cotizacion') and solicitud.cotizacion and solicitud.cotizacion.cliente:
                cliente_nombre = getattr(solicitud.cotizacion.cliente, 'nombreCliente', 'Sin nombre')
            else:
                cliente_nombre = "Cliente no asignado"
        except Exception as e:
            print(f"⚠️ Error obteniendo nombre del cliente: {e}")
            cliente_nombre = "Error al obtener cliente"
        
        # Construir la URL de la solicitud usando la función dinámica
        base_url = get_site_url(request)
        solicitud_url = f"{base_url}/workflow/solicitud/{solicitud.id}/"
        
        # Preparar análisis general para el correo
        analisis_html = ""
        analisis_texto = ""
        
        if analisis_general:
            analisis_html = f"""
            <div style="background: #e8f5e8; border: 1px solid #28a745; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h4 style="color: #155724; margin: 0 0 15px 0; display: flex; align-items: center;">
                    <i class="fas fa-user-md" style="margin-right: 10px;"></i>
                    Análisis General del Analista
                </h4>
                <div style="color: #155724; line-height: 1.6; font-size: 0.95rem;">
                    {analisis_general.replace(chr(10), '<br>')}
                </div>
            </div>
            """
            analisis_texto = f"Análisis General:\n{analisis_general}\n"
        
        # Preparar comentarios para el correo
        comentarios_html = ""
        comentarios_texto = ""
        
        if comentarios_analista:
            comentarios_html = "<h4>📋 Historial de Comentarios del Analista:</h4>"
            comentarios_texto = "Historial de Comentarios del Analista:\n"
            
            for comentario in comentarios_analista:
                fecha = comentario.fecha_creacion.strftime('%d/%m/%Y %H:%M')
                comentarios_html += f"""
                <div style="background: #f8f9fa; border-left: 4px solid #007bff; padding: 1rem; margin: 1rem 0; border-radius: 4px;">
                    <div style="font-weight: bold; color: #007bff; margin-bottom: 0.5rem;">
                        {comentario.usuario.get_full_name() or comentario.usuario.username} - {fecha}
                    </div>
                    <div style="color: #495057; line-height: 1.5;">
                        {comentario.comentario.replace(chr(10), '<br>')}
                    </div>
                </div>
                """
                comentarios_texto += f"\n• {comentario.usuario.get_full_name() or comentario.usuario.username} ({fecha}):\n{comentario.comentario}\n"
        
        # Preparar bullet points estructurados para el correo
        bullet_points_html = ""
        bullet_points_texto = ""
        
        if bullet_points:
            bullet_points_html = """
            <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h4 style="color: #856404; margin: 0 0 15px 0; display: flex; align-items: center;">
                    <i class="fas fa-list-ul" style="margin-right: 10px;"></i>
                    Comentarios de Campos Específicos
                </h4>
                <div style="max-height: 300px; overflow-y: auto;">
            """
            bullet_points_texto = "Comentarios de Campos Específicos:\n"
            
            for punto in bullet_points:
                estado_color = "#28a745" if punto.get('estado') == 'bueno' else "#dc3545" if punto.get('estado') == 'malo' else "#6c757d"
                estado_texto = "✅ Bueno" if punto.get('estado') == 'bueno' else "❌ Malo" if punto.get('estado') == 'malo' else "⏸️ Sin calificar"
                
                bullet_points_html += f"""
                <div style="background: white; border-radius: 6px; padding: 12px; margin-bottom: 10px; border-left: 4px solid {estado_color};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <strong style="color: #495057; font-size: 0.9rem;">{punto.get('campo', 'Campo')}</strong>
                        <span style="color: {estado_color}; font-size: 0.8rem; font-weight: bold;">{estado_texto}</span>
                    </div>
                    <div style="color: #6c757d; font-size: 0.85rem; margin-bottom: 6px;">
                        <i class="fas fa-user" style="margin-right: 5px;"></i>{punto.get('usuario', 'Usuario')} - {punto.get('fecha', 'Fecha')}
                    </div>
                    <div style="color: #495057; line-height: 1.4; font-size: 0.9rem;">
                        {punto.get('comentario', '').replace(chr(10), '<br>')}
                    </div>
                </div>
                """
                bullet_points_texto += f"\n• {punto.get('campo', 'Campo')} ({estado_texto}):\n{punto.get('comentario', '')}\n"
            
            bullet_points_html += "</div></div>"
        
        # Contexto para el template
        context = {
            'solicitud': solicitud,
            'etapa_anterior': etapa_anterior,
            'nueva_etapa': nueva_etapa,
            'cliente_nombre': cliente_nombre,
            'solicitud_url': solicitud_url,
            'analisis_html': analisis_html,
            'comentarios_html': comentarios_html,
            'bullet_points_html': bullet_points_html,
            'usuario_que_cambio': usuario_que_cambio,
            'tiene_analisis': bool(analisis_general),
            'tiene_comentarios': bool(comentarios_analista),
            'tiene_bullet_points': bool(bullet_points),
        }
        
        # Cargar el template HTML
        html_content = render_to_string('workflow/emails/cambio_etapa_propietario_notification.html', context)
        
        # Crear el asunto
        subject = f"🔄 Tu solicitud ha cambiado de etapa - {solicitud.codigo}"
        
        # Mensaje de texto plano como respaldo
        text_content = f"""
        Tu Solicitud Ha Cambiado de Etapa
        
        Hola {solicitud.creada_por.get_full_name() or solicitud.creada_por.username},
        
        Tu solicitud ha cambiado de etapa y está siendo procesada:
        
        • Código: {solicitud.codigo}
        • Cliente: {cliente_nombre or 'Sin asignar'}
        • Pipeline: {solicitud.pipeline.nombre}
        • Etapa Anterior: {etapa_anterior.nombre if etapa_anterior else 'Sin etapa'}
        • Nueva Etapa: {nueva_etapa.nombre}
        • Cambiado por: {usuario_que_cambio.get_full_name() or usuario_que_cambio.username}
        • Fecha de cambio: {timezone.now().strftime('%d/%m/%Y %H:%M')}
        
        {analisis_texto}
        
        {comentarios_texto}
        
        {bullet_points_texto}
        
        Para ver el estado de tu solicitud, haz clic en el siguiente enlace:
        {solicitud_url}
        
        Saludos,
        Sistema de Workflow - Financiera Pacífico
        
        ---
        Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=[solicitud.creada_por.email],
        )
        
        # Agregar el contenido HTML
        email.attach_alternative(html_content, "text/html")
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
        
        print(f"✅ Correo de cambio de etapa enviado correctamente para solicitud {solicitud.codigo} - Propietario: {solicitud.creada_por.email}")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo de cambio de etapa para solicitud {solicitud.codigo}: {str(e)}")


def enviar_correo_devolucion_backoffice(solicitud, etapa_anterior, nueva_etapa, documentos_problematicos, motivo, usuario_que_devolvio, request=None):
    """
    🚨 NUEVO: Función para enviar correo automático cuando una solicitud es devuelta desde Back Office.
    Incluye documentos problemáticos (malos + pendientes) y motivo de devolución.
    """
    try:
        # Verificar que la solicitud tiene propietario o creador
        destinatario_principal = None
        if solicitud.propietario and solicitud.propietario.email:
            destinatario_principal = solicitud.propietario.email
            print(f"📧 Enviando correo de devolución al propietario: {destinatario_principal}")
        elif solicitud.creada_por and solicitud.creada_por.email:
            destinatario_principal = solicitud.creada_por.email
            print(f"📧 Enviando correo de devolución al creador: {destinatario_principal}")
        else:
            print(f"⚠️ No se puede enviar correo: solicitud {solicitud.codigo} sin propietario/creador o email")
            return
        
        # Destinatarios con copias
        destinatarios = [destinatario_principal]
        copias = [
            "arodriguez@fpacifico.com",
            "jacastillo@fpacifico.com"
        ]
        
        # Construir la URL de la solicitud
        base_url = get_site_url(request)
        solicitud_url = f"{base_url}/workflow/solicitudes/{solicitud.id}/detalle/"
        
        # Crear contexto para el template
        context = {
            'solicitud': solicitud,
            'etapa_anterior': etapa_anterior,
            'nueva_etapa': nueva_etapa,
            'documentos_problematicos': documentos_problematicos,
            'motivo': motivo,
            'usuario_que_devolvio': usuario_que_devolvio,
            'fecha_devolucion': timezone.now(),
            'solicitud_url': solicitud_url,
            'base_url': base_url,
        }
        
        # Generar el contenido HTML del correo
        html_content = render_to_string('workflow/emails/devolucion_backoffice_notification.html', context)
        
        # Crear el asunto del correo
        subject = f"🚨 Solicitud {solicitud.codigo} Devuelta desde Back Office"
        
        # Crear y enviar el correo
        from django.core.mail import EmailMultiAlternatives
        
        email = EmailMultiAlternatives(
            subject=subject,
            body="Tu solicitud ha sido devuelta desde Back Office. Por favor, revisa el correo en formato HTML.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=destinatarios,
            cc=copias
        )
        
        # Adjuntar contenido HTML
        email.attach_alternative(html_content, "text/html")
        
        # Enviar el correo
        email.send()
        
        print(f"✅ Correo de devolución enviado correctamente para solicitud {solicitud.codigo}")
        print(f"   - Destinatario: {destinatario_principal}")
        print(f"   - Copias: {', '.join(copias)}")
        print(f"   - Documentos problemáticos: {len(documentos_problematicos)}")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo de devolución para solicitud {solicitud.codigo}: {str(e)}")
        import traceback
        print(f"❌ TRACEBACK: {traceback.format_exc()}")


def enviar_correo_comite_credito(solicitud, etapa, request=None):
    """
    Función para enviar correo automático cuando una solicitud entra a la etapa del Comité de Crédito.
    """
    try:
        # Obtener usuarios que tienen acceso a la etapa del comité dinámicamente
        destinatarios = []
        
        # Obtener permisos de bandeja para esta etapa del comité
        permisos_bandeja = PermisoBandeja.objects.filter(
            etapa=etapa,
            puede_ver=True  # Solo usuarios que pueden ver la bandeja
        ).select_related('grupo', 'usuario')
        
        # Recopilar emails de usuarios con acceso
        emails_set = set()  # Usar set para evitar duplicados
        
        for permiso in permisos_bandeja:
            if permiso.usuario and permiso.usuario.email:
                # Permiso directo a usuario
                emails_set.add(permiso.usuario.email)
                print(f"📧 Usuario del comité agregado: {permiso.usuario.email}")
            elif permiso.grupo:
                # Permiso a grupo - obtener todos los usuarios del grupo
                usuarios_grupo = permiso.grupo.user_set.filter(
                    is_active=True,
                    email__isnull=False,
                    email__gt=''  # Email no vacío
                )
                for usuario in usuarios_grupo:
                    emails_set.add(usuario.email)
                    print(f"📧 Usuario del grupo '{permiso.grupo.name}' agregado al comité: {usuario.email}")
        
        destinatarios = list(emails_set)
        
        if not destinatarios:
            print(f"⚠️ No se encontraron destinatarios para la etapa del comité '{etapa.nombre}'. Verificar permisos de bandeja.")
            return
        
        print(f"🏛️ Total de {len(destinatarios)} miembro(s) del comité encontrado(s) para '{etapa.nombre}': {destinatarios}")
        
        # Construir la URL específica de la bandeja del comité usando la función dinámica
        base_url = get_site_url(request)
        bandeja_url = f"{base_url}/workflow/comite/"
        
        # Obtener nombre del cliente usando las propiedades del modelo
        cliente_nombre = solicitud.cliente_nombre or "Cliente no asignado"
        cliente_cedula = solicitud.cliente_cedula or "Sin cédula"
        monto_formateado = solicitud.monto_formateado or "$ 0.00"
        
        # Obtener el analista revisor (último usuario que procesó la solicitud)
        analista_revisor = ""
        try:
            ultimo_historial = solicitud.historial.exclude(
                etapa__nombre__iexact="Comité de Crédito"
            ).order_by('-fecha_fin').first()
            
            if ultimo_historial and ultimo_historial.usuario_responsable:
                analista_revisor = ultimo_historial.usuario_responsable.get_full_name() or ultimo_historial.usuario_responsable.username
            else:
                analista_revisor = "No asignado"
        except Exception as e:
            print(f"⚠️ Error obteniendo analista revisor: {e}")
            analista_revisor = "Error al obtener analista"
        
        # Contexto para el template
        context = {
            'solicitud': solicitud,
            'etapa': etapa,
            'cliente_nombre': cliente_nombre,
            'cliente_cedula': cliente_cedula,
            'monto_formateado': monto_formateado,
            'analista_revisor': analista_revisor,
            'bandeja_url': bandeja_url,
        }
        
        # Cargar el template HTML específico del comité
        html_content = render_to_string('workflow/emails/comite_credito_notification.html', context)
        
        # Crear el asunto específico del comité
        subject = f"🏛️ Nueva Solicitud en Comité de Crédito - {solicitud.codigo}"
        
        # Mensaje de texto plano como respaldo
        text_content = f"""
        Nueva Solicitud en Comité de Crédito
        
        Estimado equipo del Comité de Crédito,
        
        Una solicitud ha ingresado al Comité de Crédito y requiere su revisión y aprobación:
        
        • Código: {solicitud.codigo}
        • Cliente: {cliente_nombre}
        • Cédula: {cliente_cedula}
        • Monto: {monto_formateado}
        • Producto: {solicitud.producto_descripcion}
        • Pipeline: {solicitud.pipeline.nombre}
        • Analista Revisor: {analista_revisor}
        • Creada por: {solicitud.creada_por.get_full_name() or solicitud.creada_por.username}
        • Fecha: {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        
        Para revisar la solicitud, haz clic en el siguiente enlace:
        {bandeja_url}
        
        Saludos,
        Sistema de Workflow - Financiera Pacífico
        
        ---
        Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=destinatarios,
        )
        
        # Agregar el contenido HTML
        email.attach_alternative(html_content, "text/html")
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
        
        print(f"✅ Correo del comité enviado correctamente para solicitud {solicitud.codigo} - Enviado a {len(destinatarios)} miembro(s) del comité")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo del comité para solicitud {solicitud.codigo}: {str(e)}")

def enviar_correo_pdf_resultado_consulta(solicitud):
    """
    Envía un correo con PDF adjunto al propietario cuando la etapa cambia a 'Resultado Consulta'
    """
    try:
        # Validar que la solicitud tenga propietario con email válido
        if not solicitud.propietario or not solicitud.propietario.email:
            print(f"❌ No se puede enviar correo para solicitud {solicitud.codigo}: propietario sin email válido")
            return

        # Generar el PDF usando la función optimizada con xhtml2pdf (en lugar de ReportLab)
        from workflow.models import CalificacionCampo
        from workflow.modelsWorkflow import SolicitudComentario
        from django.utils import timezone
        
        # Obtener datos para el PDF
        calificaciones = CalificacionCampo.objects.filter(solicitud=solicitud)
        comentarios_analista = SolicitudComentario.objects.filter(
            solicitud=solicitud,
            tipo="analista_credito"
        ).order_by("-fecha_creacion")
        
        # Obtener el comentario más reciente del analista
        # Priorizar CalificacionCampo con campo 'comentario_analista_credito'
        analyst_comment = ""
        
        # Primero, buscar en CalificacionCampo
        calificacion_analista = CalificacionCampo.objects.filter(
            solicitud=solicitud,
            campo='comentario_analista_credito'
        ).exclude(comentario__isnull=True).exclude(comentario='').first()
        
        if calificacion_analista and calificacion_analista.comentario:
            analyst_comment = calificacion_analista.comentario
        elif comentarios_analista.exists():
            # Fallback a SolicitudComentario si no hay CalificacionCampo
            first_comment = comentarios_analista.first()
            if first_comment:
                analyst_comment = first_comment.comentario
        
        # Obtener resultado de análisis
        # Priorizar solicitud.resultado_consulta sobre subestado_actual.nombre
        resultado_analisis = ""
        if solicitud.resultado_consulta:
            resultado_analisis = solicitud.resultado_consulta
        elif solicitud.subestado_actual:
            resultado_analisis = solicitud.subestado_actual.nombre
        
        # Preparar datos para el PDF
        pdf_data = {
            "solicitud": solicitud,
            "calificaciones": calificaciones,
            "comentarios_analista": comentarios_analista,
            "analyst_comment": analyst_comment,
            "resultado_analisis": resultado_analisis,
            "usuario_generador": solicitud.propietario,
            "fecha_generacion": timezone.now(),
        }
        
        # Generar PDF usando la función optimizada con xhtml2pdf
        pdf_buffer = generar_pdf_resultado_consulta(pdf_data)
        if not pdf_buffer:
            raise Exception("No se pudo generar el PDF con xhtml2pdf")
            
        pdf_content = pdf_buffer.getvalue()
        print(f"📊 PDF generado para email con xhtml2pdf: {len(pdf_content)} bytes")

        # Determinar colores basados en el subestado
        subestado_nombre = solicitud.subestado_actual.nombre.lower() if solicitud.subestado_actual else ""
        
        # Configuración de colores según subestado
        if 'aprobado' in subestado_nombre or 'aprueba' in subestado_nombre or 'autorizado' in subestado_nombre:
            header_color = "linear-gradient(135deg, #28a745 0%, #20c997 100%)"  # Verde
            status_color = "#28a745"
            status_color_rgb = "40, 167, 69"  # Verde en RGB
            status_icon = "fas fa-check-circle"
            status_text = "Aprobado"
        elif 'alternativa' in subestado_nombre:
            header_color = "linear-gradient(135deg, #ffc107 0%, #fd7e14 100%)"  # Amarillo/Naranja
            status_color = "#ffc107"
            status_color_rgb = "255, 193, 7"  # Amarillo en RGB
            status_icon = "fas fa-exclamation-triangle"
            status_text = "Alternativa"
        elif 'rechazado' in subestado_nombre or 'rechaza' in subestado_nombre or 'negado' in subestado_nombre:
            header_color = "linear-gradient(135deg, #dc3545 0%, #c82333 100%)"  # Rojo
            status_color = "#dc3545"
            status_color_rgb = "220, 53, 69"  # Rojo en RGB
            status_icon = "fas fa-times-circle"
            status_text = "Rechazado"
        else:
            header_color = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"  # Azul por defecto
            status_color = "#667eea"
            status_color_rgb = "102, 126, 234"  # Azul en RGB
            status_icon = "fas fa-info-circle"
            status_text = "En Proceso"

        # Preparar secciones dinámicas ANTES del template
        analisis_section = ""
        if comentarios_analista.exists():
            analisis_section = """
            <div class="analisis-section">
                <h4><i class="fas fa-chart-line"></i> Análisis General</h4>
            """
            for comentario in comentarios_analista:
                analisis_text = comentario.comentario if comentario.comentario else "No disponible"
                analisis_section += f'<p style="line-height: 1.6; margin-bottom: 15px;">{analisis_text}</p>'
            analisis_section += "</div>"
        else:
            analisis_section = """
            <div class="analisis-section">
                <h4><i class="fas fa-chart-line"></i> Análisis General</h4>
                <p style="line-height: 1.6; color: #6c757d;">No hay análisis general disponible.</p>
            </div>
            """

        # Obtener comentarios de compliance para los ítems
        from workflow.models import ComentarioDocumentoBackoffice
        comentarios = ComentarioDocumentoBackoffice.objects.filter(requisito_solicitud__solicitud=solicitud).order_by('requisito_solicitud__requisito__nombre')
        
        comentarios_section = ""
        if comentarios.exists():
            comentarios_section = f"""
            <div class="comentarios-section">
                <h4><i class="fas fa-comments"></i> Comentarios por Ítem</h4>
            """
            for comentario in comentarios:
                item_name = comentario.requisito_solicitud.requisito.nombre if comentario.requisito_solicitud and comentario.requisito_solicitud.requisito else "Ítem sin nombre"
                comentario_text = comentario.comentario if comentario.comentario else "Sin comentario"
                comentarios_section += f"""
                <div class="comentario-item">
                    <div style="font-weight: 600; color: {status_color}; margin-bottom: 8px;">{item_name}</div>
                    <div style="color: #495057; line-height: 1.5;">{comentario_text}</div>
                </div>
                """
            comentarios_section += "</div>"

        # Preparar el correo
        asunto = f"Resultado Consulta - Solicitud {solicitud.codigo}"
        mensaje_html = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Resultado de Consulta - Solicitud {solicitud.codigo}</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f8f9fa;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background: {header_color};
                    padding: 30px 40px;
                    text-align: center;
                    position: relative;
                }}
                .header::before {{
                    content: '';
                    position: absolute;
                    top: -20px;
                    right: -20px;
                    width: 80px;
                    height: 80px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 50%;
                    transform: rotate(45deg);
                }}
                .logo {{
                    width: 60px;
                    height: 60px;
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 0 auto 20px;
                    backdrop-filter: blur(10px);
                }}
                .logo i {{
                    font-size: 2rem;
                    color: white;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 1.8rem;
                    font-weight: 700;
                    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .header p {{
                    color: rgba(255, 255, 255, 0.9);
                    margin: 8px 0 0;
                    font-size: 1rem;
                }}
                .content {{
                    padding: 40px;
                }}
                .alert-box {{
                    background: linear-gradient(135deg, rgba({status_color_rgb}, 0.1) 0%, rgba({status_color_rgb}, 0.05) 100%);
                    border: 1px solid {status_color};
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 30px;
                    text-align: center;
                }}
                .alert-box h3 {{
                    color: {status_color};
                    margin: 0 0 10px 0;
                    font-size: 1.3rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                }}
                .alert-box p {{
                    color: #424242;
                    margin: 5px 0;
                    font-size: 0.95rem;
                }}
                .solicitud-info {{
                    background: #f8f9fa;
                    border-radius: 12px;
                    padding: 25px;
                    margin-bottom: 30px;
                }}
                .solicitud-info h4 {{
                    color: #495057;
                    margin: 0 0 20px 0;
                    font-size: 1.2rem;
                    display: flex;
                    align-items: center;
                }}
                .solicitud-info h4 i {{
                    margin-right: 10px;
                    color: {status_color};
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 15px;
                }}
                .info-item {{
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 12px;
                    background: white;
                    border-radius: 8px;
                    border: 1px solid #e9ecef;
                }}
                .info-item i {{
                    color: {status_color};
                    font-size: 1.1rem;
                    width: 20px;
                    text-align: center;
                }}
                .info-item span {{
                    color: #495057;
                    font-size: 0.9rem;
                }}
                .btn-container {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .btn-primary {{
                    background: {header_color};
                    color: white;
                    padding: 15px 30px;
                    border: none;
                    border-radius: 25px;
                    font-size: 1rem;
                    font-weight: 600;
                    text-decoration: none;
                    display: inline-flex;
                    align-items: center;
                    gap: 10px;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 15px rgba({status_color_rgb}, 0.3);
                }}
                .btn-primary:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba({status_color_rgb}, 0.4);
                    color: white;
                    text-decoration: none;
                }}
                .analisis-section {{
                    background: #f8f9fa;
                    border-radius: 12px;
                    padding: 25px;
                    margin-bottom: 30px;
                }}
                .analisis-section h4 {{
                    color: #495057;
                    margin: 0 0 15px 0;
                    font-size: 1.1rem;
                    display: flex;
                    align-items: center;
                }}
                .analisis-section h4 i {{
                    margin-right: 10px;
                    color: {status_color};
                }}
                .comentarios-section {{
                    background: #f8f9fa;
                    border-radius: 12px;
                    padding: 25px;
                    margin-bottom: 30px;
                }}
                .comentarios-section h4 {{
                    color: #495057;
                    margin: 0 0 20px 0;
                    font-size: 1.2rem;
                    display: flex;
                    align-items: center;
                }}
                .comentarios-section h4 i {{
                    margin-right: 10px;
                    color: {status_color};
                }}
                .comentario-item {{
                    background: white;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-left: 4px solid {status_color};
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 20px 40px;
                    text-align: center;
                    border-top: 1px solid #e9ecef;
                }}
                .footer p {{
                    margin: 5px 0;
                    color: #6c757d;
                    font-size: 0.85rem;
                }}
                .footer strong {{
                    color: #495057;
                }}
                @media (max-width: 600px) {{
                    .container {{
                        margin: 10px;
                        border-radius: 8px;
                    }}
                    .content {{
                        padding: 25px 20px;
                    }}
                    .header {{
                        padding: 25px 20px;
                    }}
                    .info-grid {{
                        grid-template-columns: 1fr;
                    }}
                    .btn-primary {{
                        padding: 12px 25px;
                        font-size: 0.9rem;
                    }}
                }}
            </style>
            <!-- Font Awesome for icons -->
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        </head>
        <body>
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <div class="logo">
                        <i class="{status_icon}"></i>
                    </div>
                    <h1>Resultado de Consulta</h1>
                    <p>Solicitud {solicitud.codigo} - {status_text}</p>
                </div>
                
                <!-- Content -->
                <div class="content">
                    <!-- Alert Box -->
                    <div class="alert-box">
                        <h3><i class="{status_icon}"></i> {status_text}</h3>
                        <p>Su solicitud ha completado el proceso de análisis y consulta.</p>
                        <p>Encontrará adjunto el reporte completo con todos los detalles y conclusiones.</p>
                    </div>
                    
                    <!-- Solicitud Info -->
                    <div class="solicitud-info">
                        <h4><i class="fas fa-file-alt"></i> Información de la Solicitud</h4>
                        
                        <div class="info-grid">
                            <div class="info-item">
                                <i class="fas fa-hashtag"></i>
                                <span><strong>Código:</strong> {solicitud.codigo}</span>
                            </div>
                            <div class="info-item">
                                <i class="fas fa-user"></i>
                                <span><strong>Cliente:</strong> {getattr(solicitud, 'cliente_nombre_completo', 'No disponible')}</span>
                            </div>
                            <div class="info-item">
                                <i class="fas fa-calendar"></i>
                                <span><strong>Fecha:</strong> {solicitud.fecha_creacion.strftime('%d/%m/%Y') if solicitud.fecha_creacion else 'No disponible'}</span>
                            </div>
                            <div class="info-item">
                                <i class="fas fa-flag"></i>
                                <span><strong>Estado:</strong> {status_text}</span>
                            </div>
                            <div class="info-item">
                                <i class="fas fa-layer-group"></i>
                                <span><strong>Pipeline:</strong> {solicitud.pipeline.nombre if solicitud.pipeline else 'No disponible'}</span>
                            </div>
                            <div class="info-item">
                                <i class="fas fa-map-marker-alt"></i>
                                <span><strong>Etapa:</strong> {solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'No disponible'}</span>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Análisis General -->
                    {analisis_section}
                    
                    <!-- Comentarios por Ítem -->
                    {comentarios_section}
                    
                    <!-- Action Button -->
                    <div class="btn-container">
                        <a href="#" class="btn-primary">
                            <i class="fas fa-download"></i>
                            Ver Reporte Completo (PDF Adjunto)
                        </a>
                    </div>
                    
                    <p style="color: #6c757d; font-size: 0.9rem; text-align: center; margin-top: 30px;">
                        <i class="fas fa-info-circle"></i>
                        Este correo incluye el reporte completo de su consulta como archivo adjunto en formato PDF.
                    </p>
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <p><strong>Equipo de Análisis</strong></p>
                    <p>📧 Financiera Pacífico</p>
                    <p>⚠️ Este es un correo automático, por favor no responder a esta dirección.</p>
                </div>
            </div>
        </body>
        </html>
        """

        mensaje_texto = f"""
        Resultado de Consulta - Solicitud {solicitud.codigo} - {status_text}
        
        Estimado/a {solicitud.propietario.get_full_name() or solicitud.propietario.username},
        
        Su solicitud {solicitud.codigo} ha completado el proceso de análisis y consulta con resultado: {status_text}
        
        INFORMACIÓN DE LA SOLICITUD:
        - Código: {solicitud.codigo}
        - Cliente: {getattr(solicitud, 'cliente_nombre_completo', 'No disponible')}
        - Fecha: {solicitud.fecha_creacion.strftime('%d/%m/%Y') if solicitud.fecha_creacion else 'No disponible'}
        - Estado: {status_text}
        - Pipeline: {solicitud.pipeline.nombre if solicitud.pipeline else 'No disponible'}
        - Etapa: {solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'No disponible'}
        
        ADJUNTO:
        Encontrará el reporte completo con todos los detalles del análisis en formato PDF.
        
        El documento incluye:
        - Análisis general de la solicitud
        - Comentarios específicos por cada ítem evaluado
        - Conclusiones del proceso de consulta
        
        Si tiene alguna consulta sobre este resultado, no dude en contactarnos.
        
        Saludos cordiales,
        Equipo de Análisis
        Financiera Pacífico
        
        ---
        Este es un correo automático, por favor no responder a esta dirección.
        """

        # Crear y enviar el email
        email = EmailMultiAlternatives(
            subject=asunto,
            body=mensaje_texto,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[solicitud.propietario.email]
        )
        
        email.attach_alternative(mensaje_html, "text/html")
        
        # Adjuntar el PDF
        filename = f"resultado_consulta_solicitud_{solicitud.codigo}.pdf"
        email.attach(filename, pdf_content, 'application/pdf')

        # Enviar email con manejo de SSL
        try:
            email.send()
        except Exception as ssl_error:
            print(f"⚠️ Error detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
        
        print(f"✅ Correo con PDF de Resultado Consulta enviado correctamente para solicitud {solicitud.codigo} a {solicitud.propietario.email}")
        
    except Exception as e:
        print(f"❌ Error al enviar correo de Resultado Consulta para solicitud {solicitud.codigo}: {str(e)}")


def enviar_correo_apc_makito(solicitud, no_cedula, tipo_documento, request=None):
    """
    Función para enviar correo automático cuando se solicita descargar APC con Makito.
    """
    try:
        # Destinatarios específicos para APC
        destinatarios = [
            "makito@fpacifico.com",
            "arodriguez@fpacifico.com",
            "jacastillo@fpacifico.com"
        ]
        
        # Obtener nombre del cliente usando las propiedades del modelo
        cliente_nombre = solicitud.cliente_nombre_completo or "Cliente no asignado"
        
        # Obtener correo del solicitante
        correo_solicitante = solicitud.creada_por.email or "No especificado"
        
        # Crear el asunto específico para APC
        subject = f"workflowAPC - {cliente_nombre} - {no_cedula}"
        
        # Obtener la URL base dinámicamente
        base_url = get_site_url(request)
        print(f"🔍 DEBUG: Base URL: {base_url}")
        
        # Mensaje de texto plano
        text_content = f"""
        Solicitud de Descarga APC con Makito
        
        Hola,
        
        Se ha solicitado la descarga del APC para la siguiente solicitud:
        
        • Código de Solicitud: {solicitud.codigo}
        • Cliente: {cliente_nombre}
        • Tipo de Documento: {tipo_documento.title()}
        • Número de Documento: {no_cedula}
        • Pipeline: {solicitud.pipeline.nombre}
        • Solicitado por: {solicitud.creada_por.get_full_name() or solicitud.creada_por.username}
        • Correo Solicitante: {correo_solicitante}
        • Fecha de Solicitud: {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        
        ==========================================
        DATOS PARA EXTRACCIÓN AUTOMATIZADA (MAKITO RPA)
        ==========================================
        codigo solicitud: <codVariable{solicitud.codigo}cod>
        tipo de documento: <tipodocVariable{tipo_documento.lower()}tipodoc>
        numero documento: <nodocVariable{no_cedula}nodoc>
        cliente: <nombreVariable{cliente_nombre}nombre>
        
        Información para APC:
        Tipo de documento: {tipo_documento.title()}
        Número de documento: {no_cedula}
        
        ==========================================
        INSTRUCCIONES PARA MAKITO RPA
        ==========================================
        
        Para actualizar el estado de esta solicitud, utiliza las siguientes APIs:
        
        1. MARCAR COMO "EN PROGRESO":
           URL: {base_url}/workflow/api/makito/update-status/{solicitud.codigo}/
           Método: POST
           Content-Type: application/json
           Body:
           {{
               "status": "in_progress",
               "observaciones": "Iniciando procesamiento del APC"
           }}
        
        2. MARCAR COMO "COMPLETADO" Y SUBIR ARCHIVO:
           URL: {base_url}/workflow/api/makito/upload-apc/{solicitud.codigo}/
           Método: POST
           Content-Type: multipart/form-data
           Form Data:
           - apc_file: [archivo PDF del APC]
           - observaciones: "APC generado exitosamente"
        
        3. MARCAR COMO "ERROR" (si es necesario):
           URL: {base_url}/workflow/api/makito/update-status/{solicitud.codigo}/
           Método: POST
           Content-Type: application/json
           Body:
           {{
               "status": "error",
               "observaciones": "Descripción del error encontrado"
           }}
        
        ==========================================
        FLUJO RECOMENDADO:
        ==========================================
        1. Al iniciar el procesamiento → Usar API #1 con status "in_progress"
        2. Al completar exitosamente → Usar API #2 para subir el archivo
        3. En caso de error → Usar API #3 con status "error"
        
        ==========================================
        NOTAS IMPORTANTES:
        ==========================================
        • El archivo debe ser un PDF válido
        • Tamaño máximo del archivo: 10MB
        • El sistema automáticamente marcará la solicitud como completada
        • Se enviará una notificación al solicitante cuando se complete
        
        Saludos,
        Sistema de Workflow - Financiera Pacífico
        
        ---
        Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=destinatarios,
        )
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
        
        # Actualizar el estado APC después de enviar el correo exitosamente
        from django.utils import timezone
        solicitud.apc_status = 'pending'
        solicitud.apc_fecha_solicitud = timezone.now()
        solicitud.save(update_fields=['apc_status', 'apc_fecha_solicitud'])
        
        print(f"✅ Correo APC enviado correctamente para solicitud {solicitud.codigo}")
        print(f"✅ Estado APC actualizado a 'pending'")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo APC para solicitud {solicitud.codigo}: {str(e)}")


def enviar_correo_sura_makito(solicitud, sura_primer_nombre, sura_primer_apellido, sura_no_documento, request=None, **kwargs):
    """
    Función para enviar correo automático cuando se solicita cotización SURA con Makito.
    Incluye información del vehículo para la cotización.
    """
    try:
        # Extraer datos del vehículo de kwargs
        sura_valor_auto = kwargs.get('sura_valor_auto', '')
        sura_ano_auto = kwargs.get('sura_ano_auto', '')
        sura_marca = kwargs.get('sura_marca', '')
        sura_modelo = kwargs.get('sura_modelo', '')
        sura_tipo_documento = kwargs.get('sura_tipo_documento', '')
        
        # Destinatarios específicos para SURA
        destinatarios = [
            "makito@fpacifico.com",
            "arodriguez@fpacifico.com",
            "jacastillo@fpacifico.com"
        ]
        
        # Obtener nombre del cliente usando las propiedades del modelo
        cliente_nombre = solicitud.cliente_nombre_completo or "Cliente no asignado"
        
        # Obtener correo del solicitante
        correo_solicitante = solicitud.creada_por.email or "No especificado"
        
        # Crear el asunto específico para SURA
        subject = f"workflowCotSURA - {cliente_nombre} - {sura_no_documento}"
        
        # Obtener la URL base dinámicamente
        base_url = get_site_url(request)
        print(f"🔍 DEBUG: Base URL: {base_url}")
        
        # Mensaje de texto plano con información del vehículo
        text_content = f"""
        Solicitud de Cotización SURA con Makito
        
        Hola,
        
        Se ha solicitado la cotización SURA para la siguiente solicitud:
        
        • Código de Solicitud: {solicitud.codigo}
        • Cliente: {cliente_nombre}
        • Primer Nombre: {sura_primer_nombre}
        • Segundo Nombre: {solicitud.sura_segundo_nombre or 'N/A'}
        • Primer Apellido: {sura_primer_apellido}
        • Segundo Apellido: {solicitud.sura_segundo_apellido or 'N/A'}
        • Número de Documento: {sura_no_documento}
        • Tipo de Documento: {sura_tipo_documento or 'N/A'}
        • Pipeline: {solicitud.pipeline.nombre}
        • Solicitado por: {solicitud.creada_por.get_full_name() or solicitud.creada_por.username}
        • Correo Solicitante: {correo_solicitante}
        • Fecha de Solicitud: {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        
        ==========================================
        INFORMACIÓN DEL VEHÍCULO
        ==========================================
        • Valor del Auto: ${sura_valor_auto or 'N/A'}
        • Año del Auto: {sura_ano_auto or 'N/A'}
        • Marca: {sura_marca or 'N/A'}
        • Modelo: {sura_modelo or 'N/A'}
        
        ==========================================
        DATOS PARA EXTRACCIÓN AUTOMATIZADA (MAKITO RPA)
        ==========================================
        <codigoSolicitudvar>{solicitud.codigo}</codigoSolicitudvar>
        <numeroDocumentovar>{sura_no_documento}</numeroDocumentovar>
        <tipoDocumentovar>{sura_tipo_documento or 'cedula'}</tipoDocumentovar>
        <primerNombrevar>{sura_primer_nombre}</primerNombrevar>
        <segundoNombrevar>{solicitud.sura_segundo_nombre or ''}</segundoNombrevar>
        <primerApellidovar>{sura_primer_apellido}</primerApellidovar>
        <segundoApellidovar>{solicitud.sura_segundo_apellido or ''}</segundoApellidovar>
        <clientevar>{cliente_nombre}</clientevar>
        <valorAutovar>{sura_valor_auto or ''}</valorAutovar>
        <anoAutovar>{sura_ano_auto or ''}</anoAutovar>
        <marcaAutovar>{sura_marca or ''}</marcaAutovar>
        <modeloAutovar>{sura_modelo or ''}</modeloAutovar>
        
        Información para SURA:
        Primer Nombre: {sura_primer_nombre}
        Segundo Nombre: {solicitud.sura_segundo_nombre or 'N/A'}
        Primer Apellido: {sura_primer_apellido}
        Segundo Apellido: {solicitud.sura_segundo_apellido or 'N/A'}
        Número de Documento: {sura_no_documento}
        Tipo de Documento: {sura_tipo_documento or 'N/A'}
        
        Información del Vehículo:
        Valor del Auto: ${sura_valor_auto or 'N/A'}
        Año del Auto: {sura_ano_auto or 'N/A'}
        Marca: {sura_marca or 'N/A'}
        Modelo: {sura_modelo or 'N/A'}
        
        ==========================================
        INSTRUCCIONES PARA MAKITO RPA
        ==========================================
        
        Para actualizar el estado de esta solicitud, utiliza las siguientes APIs:
        
        1. MARCAR COMO "EN PROGRESO":
           URL: {base_url}/workflow/api/sura/update-status/{solicitud.codigo}/
           Método: POST
           Content-Type: application/json
           Body:
           {{
               "status": "in_progress",
               "observaciones": "Iniciando procesamiento de cotización SURA"
           }}
        
        2. MARCAR COMO "COMPLETADO" Y SUBIR ARCHIVO:
           URL: {base_url}/workflow/api/sura/upload-file/{solicitud.codigo}/
           Método: POST
           Content-Type: multipart/form-data
           Form Data:
           - sura_file: [archivo PDF de la cotización]
           - observaciones: "Cotización SURA generada exitosamente"
        
        3. MARCAR COMO "ERROR" (si es necesario):
           URL: {base_url}/workflow/api/sura/update-status/{solicitud.codigo}/
           Método: POST
           Content-Type: application/json
           Body:
           {{
               "status": "error",
               "observaciones": "Descripción del error encontrado"
           }}
        
        ==========================================
        FLUJO RECOMENDADO:
        ==========================================
        1. Al iniciar el procesamiento → Usar API #1 con status "in_progress"
        2. Al completar exitosamente → Usar API #2 para subir el archivo
        3. En caso de error → Usar API #3 con status "error"
        
        ==========================================
        NOTAS IMPORTANTES:
        ==========================================
        • El archivo debe ser un PDF válido
        • Tamaño máximo del archivo: 10MB
        • El sistema automáticamente marcará la solicitud como completada
        • Se enviará una notificación al solicitante cuando se complete
        
        Saludos,
        Sistema de Workflow - Financiera Pacífico
        
        ---
        Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=destinatarios,
        )
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
        
        # Actualizar el estado SURA después de enviar el correo exitosamente
        from django.utils import timezone
        solicitud.sura_status = 'pending'
        solicitud.sura_fecha_solicitud = timezone.now()
        solicitud.save(update_fields=['sura_status', 'sura_fecha_solicitud'])
        
        print(f"✅ Correo SURA enviado correctamente para solicitud {solicitud.codigo}")
        print(f"✅ Estado SURA actualizado a 'pending'")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo SURA para solicitud {solicitud.codigo}: {str(e)}")

# ==========================================
# DEBIDA DILIGENCIA API VIEWS
# ==========================================

@login_required
def api_debida_diligencia_status(request, solicitud_id):
    """
    API para obtener el estado de debida diligencia de una solicitud
    """
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if not request.user.is_superuser:
            # Verificar si el usuario tiene permisos para ver esta solicitud
            user_groups = request.user.groups.all()
            tiene_permiso = PermisoBandeja.objects.filter(
                grupo__in=user_groups,
                etapa=solicitud.etapa_actual
            ).exists()
            
            if not tiene_permiso and solicitud.creada_por != request.user and solicitud.asignada_a != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'No tiene permisos para ver esta solicitud'
                }, status=403)
        
        # Preparar datos de respuesta
        data = {
            'success': True,
            'estado': solicitud.debida_diligencia_status,
            'fecha_solicitud': solicitud.diligencia_fecha_solicitud.isoformat() if solicitud.diligencia_fecha_solicitud else None,
            'fecha_completado': solicitud.diligencia_fecha_completado.isoformat() if solicitud.diligencia_fecha_completado else None,
            'comentarios': solicitud.diligencia_observaciones or '',
            'busqueda_google': {
                'archivo': solicitud.diligencia_busqueda_google.url if solicitud.diligencia_busqueda_google else None,
                'fecha_subida': solicitud.diligencia_google_fecha_subida.isoformat() if solicitud.diligencia_google_fecha_subida else None
            },
            'busqueda_registro_publico': {
                'archivo': solicitud.diligencia_busqueda_registro_publico.url if solicitud.diligencia_busqueda_registro_publico else None,
                'fecha_subida': solicitud.diligencia_registro_publico_fecha_subida.isoformat() if solicitud.diligencia_registro_publico_fecha_subida else None
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        print(f"❌ Error en api_debida_diligencia_status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)

@login_required
def api_debida_diligencia_solicitar(request, solicitud_id):
    """
    API para solicitar debida diligencia para una solicitud
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        }, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if not request.user.is_superuser:
            user_groups = request.user.groups.all()
            tiene_permiso = PermisoBandeja.objects.filter(
                grupo__in=user_groups,
                etapa=solicitud.etapa_actual
            ).exists()
            
            if not tiene_permiso and solicitud.creada_por != request.user and solicitud.asignada_a != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'No tiene permisos para modificar esta solicitud'
                }, status=403)
        
        # Verificar que no esté ya en proceso
        if solicitud.debida_diligencia_status in ['en_progreso', 'completado']:
            return JsonResponse({
                'success': False,
                'error': 'La debida diligencia ya está en proceso o completada'
            }, status=400)
        
        # Actualizar el estado
        solicitud.debida_diligencia_status = 'solicitado'
        solicitud.diligencia_fecha_solicitud = timezone.now()
        solicitud.save(update_fields=['debida_diligencia_status', 'diligencia_fecha_solicitud'])
        
        # Crear entrada en el historial
        historial_entry = HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=solicitud.etapa_actual,
            subestado=solicitud.subestado_actual,
            usuario_responsable=request.user,
            fecha_inicio=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Debida diligencia solicitada exitosamente'
        })
        
    except Exception as e:
        print(f"❌ Error en api_debida_diligencia_solicitar: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)

@login_required
def api_debida_diligencia_solicitar_makito(request, solicitud_id):
    """
    API para solicitar a Makito RPA generar documentos de debida diligencia
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        }, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        tipo_documento = data.get('tipo_documento')
        
        if not tipo_documento or tipo_documento not in ['busqueda_google', 'busqueda_registro_publico']:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de documento inválido'
            }, status=400)
        
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if not request.user.is_superuser:
            user_groups = request.user.groups.all()
            tiene_permiso = PermisoBandeja.objects.filter(
                grupo__in=user_groups,
                etapa=solicitud.etapa_actual
            ).exists()
            
            if not tiene_permiso and solicitud.creada_por != request.user and solicitud.asignada_a != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'No tiene permisos para modificar esta solicitud'
                }, status=403)
        
        # Actualizar el estado a processing si no está ya completado
        if solicitud.debida_diligencia_status not in ['completado']:
            solicitud.debida_diligencia_status = 'en_progreso'
            if not solicitud.diligencia_fecha_solicitud:
                solicitud.diligencia_fecha_solicitud = timezone.now()
            solicitud.diligencia_fecha_inicio = timezone.now()
            solicitud.save(update_fields=['debida_diligencia_status', 'diligencia_fecha_solicitud', 'diligencia_fecha_inicio'])
        
        # Enviar correo a Makito RPA
        enviar_correo_debida_diligencia_makito(solicitud, tipo_documento, request)
        
        # Crear entrada en el historial
        historial_entry = HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=solicitud.etapa_actual,
            subestado=solicitud.subestado_actual,
            usuario_responsable=request.user,
            fecha_inicio=timezone.now()
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Solicitud enviada a Makito RPA para {tipo_documento.replace("_", " ")}'
        })
        
    except Exception as e:
        print(f"❌ Error en api_debida_diligencia_solicitar_makito: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)

@login_required
def api_debida_diligencia_upload(request, solicitud_id):
    """
    API para subir archivos de debida diligencia manualmente o por Makito
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        }, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if not request.user.is_superuser:
            user_groups = request.user.groups.all()
            tiene_permiso = PermisoBandeja.objects.filter(
                grupo__in=user_groups,
                etapa=solicitud.etapa_actual
            ).exists()
            
            if not tiene_permiso and solicitud.creada_por != request.user and solicitud.asignada_a != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'No tiene permisos para modificar esta solicitud'
                }, status=403)
        
        archivo = request.FILES.get('archivo')
        tipo_documento = request.POST.get('tipo_documento')
        observaciones = request.POST.get('observaciones', '')
        
        if not archivo:
            return JsonResponse({
                'success': False,
                'error': 'No se proporcionó archivo'
            }, status=400)
        
        if not tipo_documento or tipo_documento not in ['busqueda_google', 'busqueda_registro_publico']:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de documento inválido'
            }, status=400)
        
        # Validar que sea PDF
        if not archivo.name.lower().endswith('.pdf'):
            return JsonResponse({
                'success': False,
                'error': 'Solo se permiten archivos PDF'
            }, status=400)
        
        # Validar tamaño (10MB máximo)
        if archivo.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'El archivo no puede ser mayor a 10MB'
            }, status=400)
        
        # Guardar el archivo según el tipo
        if tipo_documento == 'busqueda_google':
            solicitud.diligencia_busqueda_google = archivo
            solicitud.diligencia_google_fecha_subida = timezone.now()
        elif tipo_documento == 'busqueda_registro_publico':
            solicitud.diligencia_busqueda_registro_publico = archivo
            solicitud.diligencia_registro_publico_fecha_subida = timezone.now()
        
        # Actualizar observaciones si se proporcionan
        if observaciones:
            solicitud.diligencia_observaciones = observaciones
        
        # Verificar si ambos archivos están subidos para marcar como completado
        if (solicitud.diligencia_busqueda_google and 
            solicitud.diligencia_busqueda_registro_publico):
            solicitud.debida_diligencia_status = 'completado'
            solicitud.diligencia_fecha_completado = timezone.now()
        
        solicitud.save()
        
        # Crear entrada en el historial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            accion='debida_diligencia_archivo_subido',
            detalles=f'Archivo subido: {tipo_documento.replace("_", " ").title()}',
            usuario=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': f'Archivo de {tipo_documento.replace("_", " ")} subido exitosamente'
        })
        
    except Exception as e:
        print(f"❌ Error en api_debida_diligencia_upload: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)

@login_required
def api_debida_diligencia_reenviar_correo(request, solicitud_id):
    """
    API para reenviar correo de debida diligencia a Makito RPA
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        }, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        tipo_documento = data.get('tipo_documento', 'ambos')
        
        if tipo_documento not in ['busqueda_google', 'busqueda_registro_publico', 'ambos']:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de documento inválido'
            }, status=400)
        
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if not request.user.is_superuser:
            user_groups = request.user.groups.all()
            tiene_permiso = PermisoBandeja.objects.filter(
                grupo__in=user_groups,
                etapa=solicitud.etapa_actual
            ).exists()
            
            if not tiene_permiso and solicitud.creada_por != request.user and solicitud.asignada_a != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'No tiene permisos para modificar esta solicitud'
                }, status=403)
        
        # Asegurar que el estado esté en progreso si no está completado
        if solicitud.debida_diligencia_status not in ['en_progreso', 'completado']:
            solicitud.debida_diligencia_status = 'en_progreso'
            if not solicitud.diligencia_fecha_solicitud:
                solicitud.diligencia_fecha_solicitud = timezone.now()
            solicitud.diligencia_fecha_inicio = timezone.now()
            solicitud.save(update_fields=['debida_diligencia_status', 'diligencia_fecha_solicitud', 'diligencia_fecha_inicio'])
        
        # Reenviar correos según el tipo solicitado
        if tipo_documento == 'ambos':
            # Enviar ambos correos
            enviar_correo_debida_diligencia_makito(solicitud, 'busqueda_google', request)
            enviar_correo_debida_diligencia_makito(solicitud, 'busqueda_registro_publico', request)
            mensaje = 'Correos reenviados a Makito RPA para búsqueda Google y Registro Público'
        else:
            # Enviar correo específico
            enviar_correo_debida_diligencia_makito(solicitud, tipo_documento, request)
            tipo_legible = tipo_documento.replace('_', ' ').title()
            mensaje = f'Correo reenviado a Makito RPA para {tipo_legible}'
        
        # Crear entrada en el historial
        historial_entry = HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=solicitud.etapa_actual,
            subestado=solicitud.subestado_actual,
            usuario_responsable=request.user,
            observaciones=f'Correo de debida diligencia reenviado ({tipo_documento})',
            fecha_inicio=timezone.now()
        )
        
        print(f"✅ Correo de debida diligencia reenviado para solicitud {solicitud.codigo} - Tipo: {tipo_documento}")
        
        return JsonResponse({
            'success': True,
            'message': mensaje
        })
        
    except Exception as e:
        print(f"❌ Error en api_debida_diligencia_reenviar_correo: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)

# Makito RPA API endpoints for debida diligencia
@csrf_exempt
def api_makito_debida_diligencia_update_status(request, solicitud_codigo):
    """
    API para que Makito RPA actualice el estado de debida diligencia
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        }, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        status = data.get('status')
        observaciones = data.get('observaciones', '')
        
        if not status or status not in ['in_progress', 'completed', 'error']:
            return JsonResponse({
                'success': False,
                'error': 'Estado inválido'
            }, status=400)
        
        solicitud = get_object_or_404(Solicitud, codigo=solicitud_codigo)
        
        # Mapear estados
        status_mapping = {
            'in_progress': 'makito_processing',
            'completed': 'completado',
            'error': 'error'
        }
        
        solicitud.debida_diligencia_status = status_mapping[status]
        solicitud.diligencia_observaciones = observaciones
        
        if status == 'in_progress':
            solicitud.diligencia_fecha_inicio = timezone.now()
        elif status == 'completed':
            solicitud.diligencia_fecha_completado = timezone.now()
        
        solicitud.save()
        
        # Crear entrada en el historial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            accion='debida_diligencia_makito_status_update',
            detalles=f'Makito RPA actualizó estado a: {status}. Observaciones: {observaciones}',
            usuario=None  # Sistema automático
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Estado actualizado correctamente',
            'new_status': solicitud.debida_diligencia_status
        })
        
    except Exception as e:
        print(f"❌ Error en api_makito_debida_diligencia_update_status: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)

@csrf_exempt
def api_makito_debida_diligencia_upload(request, solicitud_codigo):
    """
    API para que Makito RPA suba archivos de debida diligencia
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        }, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, codigo=solicitud_codigo)
        
        busqueda_google = request.FILES.get('busqueda_google')
        busqueda_registro_publico = request.FILES.get('busqueda_registro_publico')
        observaciones = request.POST.get('observaciones', '')
        
        if not busqueda_google and not busqueda_registro_publico:
            return JsonResponse({
                'success': False,
                'error': 'No se proporcionaron archivos'
            }, status=400)
        
        # Validar y guardar archivos
        if busqueda_google:
            if not busqueda_google.name.lower().endswith('.pdf'):
                return JsonResponse({
                    'success': False,
                    'error': 'Búsqueda Google debe ser un archivo PDF'
                }, status=400)
            solicitud.diligencia_busqueda_google = busqueda_google
            solicitud.diligencia_google_fecha_subida = timezone.now()
        
        if busqueda_registro_publico:
            if not busqueda_registro_publico.name.lower().endswith('.pdf'):
                return JsonResponse({
                    'success': False,
                    'error': 'Búsqueda Registro Público debe ser un archivo PDF'
                }, status=400)
            solicitud.diligencia_busqueda_registro_publico = busqueda_registro_publico
            solicitud.diligencia_registro_publico_fecha_subida = timezone.now()
        
        # Actualizar observaciones
        if observaciones:
            solicitud.diligencia_observaciones = observaciones
        
        # Marcar como completado si ambos archivos están presentes
        if (solicitud.diligencia_busqueda_google and 
            solicitud.diligencia_busqueda_registro_publico):
            solicitud.debida_diligencia_status = 'completado'
            solicitud.diligencia_fecha_completado = timezone.now()
        
        solicitud.save()
        
        # Crear entrada en el historial
        archivos_subidos = []
        if busqueda_google:
            archivos_subidos.append('Búsqueda Google')
        if busqueda_registro_publico:
            archivos_subidos.append('Búsqueda Registro Público')
        
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            accion='debida_diligencia_makito_upload',
            detalles=f'Makito RPA subió archivos: {", ".join(archivos_subidos)}. Observaciones: {observaciones}',
            usuario=None  # Sistema automático
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Archivos subidos correctamente',
            'status': solicitud.debida_diligencia_status
        })
        
    except Exception as e:
        print(f"❌ Error en api_makito_debida_diligencia_upload: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)

def enviar_correo_debida_diligencia_makito(solicitud, tipo_documento, request=None):
    """
    Función para enviar correo automático a Makito RPA para debida diligencia
    """
    try:
        import ssl
        
        # Destinatarios específicos para Debida Diligencia
        # TO: makito@fpacifico.com (principal)
        # CC: arodriguez@fpacifico.com (seguimiento)
        destinatarios = [
            "makito@fpacifico.com",
            "arodriguez@fpacifico.com",
            "jacastillo@fpacifico.com"
        ]
        
        # Obtener nombre del cliente
        cliente_nombre = solicitud.cliente_nombre_completo or "Cliente no asignado"
        
        # Obtener número de documento del cliente
        no_documento = ""
        if solicitud.cliente:
            no_documento = getattr(solicitud.cliente, 'cedulaCliente', '') or solicitud.cliente_cedula or ""
        elif solicitud.cliente_cedula:
            no_documento = solicitud.cliente_cedula
        
        # Obtener correo del solicitante
        correo_solicitante = solicitud.creada_por.email or "No especificado"
        
        # Crear el asunto específico para Debida Diligencia
        tipo_legible = tipo_documento.replace('_', ' ').title()
        subject = f"workflowDiligencia - {cliente_nombre} - {tipo_legible} - CC: arodriguez@fpacifico.com"
        
        # Obtener la URL base dinámicamente
        base_url = get_site_url(request)
        
        # Mensaje de texto plano
        text_content = f"""
        Solicitud de Debida Diligencia con Makito RPA
        
        Hola,
        
        Se ha solicitado generar documentos de debida diligencia para la siguiente solicitud:
        
        • Código de Solicitud: {solicitud.codigo}
        • Cliente: {cliente_nombre}
        • Número de Documento: {no_documento}
        • Tipo de Documento Solicitado: {tipo_legible}
        • Pipeline: {solicitud.pipeline.nombre}
        • Solicitado por: {solicitud.creada_por.get_full_name() or solicitud.creada_por.username}
        • Correo Solicitante: {correo_solicitante}
        • Fecha de Solicitud: {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        
        NOTA: Este correo incluye CC a arodriguez@fpacifico.com para seguimiento.
        
        ==========================================
        DATOS PARA EXTRACCIÓN AUTOMATIZADA (MAKITO RPA)
        ==========================================
        codigo solicitud: <codVariable{solicitud.codigo}cod>
        tipo documento: <tipodocVariable{tipo_documento}tipodoc>
        numero documento: <nodocVariable{no_documento}nodoc>
        cliente: <nombreVariable{cliente_nombre}nombre>
        
        Información para Debida Diligencia:
        Tipo de documento a generar: {tipo_legible}
        Número de documento del cliente: {no_documento}
        
        ==========================================
        INSTRUCCIONES PARA MAKITO RPA
        ==========================================
        
        Para actualizar el estado de esta solicitud, utiliza las siguientes APIs:
        
        1. MARCAR COMO "EN PROGRESO":
           URL: {base_url}/workflow/api/makito/debida-diligencia/update-status/{solicitud.codigo}/
           Método: POST
           Content-Type: application/json
           Body:
           {{
               "status": "in_progress",
               "observaciones": "Iniciando procesamiento de debida diligencia"
           }}
        
        2. SUBIR ARCHIVOS COMPLETADOS:
           URL: {base_url}/workflow/api/makito/debida-diligencia/upload/{solicitud.codigo}/
           Método: POST
           Content-Type: multipart/form-data
           Form Data:
           - busqueda_google: [archivo PDF de búsqueda en Google] (opcional)
           - busqueda_registro_publico: [archivo PDF de búsqueda en Registro Público] (opcional)
           - observaciones: "Archivos generados exitosamente"
           
           NOTA: Se pueden subir uno o ambos archivos según disponibilidad.
           El sistema marcará automáticamente como completado cuando ambos archivos estén presentes.
        
        3. MARCAR COMO "ERROR" (si es necesario):
           URL: {base_url}/workflow/api/makito/debida-diligencia/update-status/{solicitud.codigo}/
           Método: POST
           Content-Type: application/json
           Body:
           {{
               "status": "error",
               "observaciones": "Descripción del error encontrado"
           }}
        
        ==========================================
        FLUJO RECOMENDADO:
        ==========================================
        1. Al iniciar el procesamiento → Usar API #1 con status "in_progress"
        2. Al completar exitosamente → Usar API #2 para subir archivos
        3. En caso de error → Usar API #3 con status "error"
        
        ==========================================
        NOTAS IMPORTANTES:
        ==========================================
        • Los archivos deben ser PDF válidos
        • Tamaño máximo por archivo: 10MB
        • Se pueden subir uno o ambos archivos según disponibilidad
        • El sistema marcará automáticamente como completado cuando ambos archivos estén presentes
        • Se enviará una notificación al solicitante cuando se complete
        
        Saludos,
        Sistema de Workflow - Financiera Pacífico
        
        ---
        Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=destinatarios,
        )
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
        
        print(f"✅ Correo de debida diligencia enviado correctamente para solicitud {solicitud.codigo}")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo de debida diligencia para solicitud {solicitud.codigo}: {str(e)}")

# ==========================================
# APC MAKITO SOLICITAR API
# ==========================================

@login_required
def api_solicitar_apc_makito(request, solicitud_id):
    """
    API para solicitar descarga de APC con Makito RPA
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        }, status=405)

    try:
        import json
        
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Parse request data
        try:
            request_data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            request_data = {}
        
        # Verificar permisos
        if not request.user.is_superuser:
            user_groups = request.user.groups.all()
            tiene_permiso = PermisoBandeja.objects.filter(
                grupo__in=user_groups,
                etapa=solicitud.etapa_actual
            ).exists()
            
            if not tiene_permiso and solicitud.creada_por != request.user and solicitud.asignada_a != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'No tiene permisos para modificar esta solicitud'
                }, status=403)
        
        # Verificar que la solicitud no tenga ya APC procesado
        if solicitud.apc_status == 'completed':
            return JsonResponse({
                'success': False,
                'error': 'Esta solicitud ya tiene APC completado'
            }, status=400)
        
        # Obtener datos necesarios para APC
        cliente_info = solicitud.cliente_nombre_completo or "Cliente no asignado"
        
        # Get document data from form submission first, fallback to existing data
        tipo_documento = request_data.get('tipo_documento', '')
        numero_documento = request_data.get('numero_documento', '')
        
        # If form data is not provided, try to get from existing records
        if not numero_documento:
            if hasattr(solicitud, 'cliente') and solicitud.cliente:
                numero_documento = solicitud.cliente.cedulaCliente
                tipo_documento = 'cedula' if numero_documento else ''
            elif hasattr(solicitud, 'cotizacion') and solicitud.cotizacion and solicitud.cotizacion.cedulaCliente:
                numero_documento = solicitud.cotizacion.cedulaCliente
                tipo_documento = 'cedula' if numero_documento else ''
        
        if not numero_documento or not tipo_documento:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró información del documento del cliente para procesar APC. Por favor complete los campos del formulario.'
            }, status=400)
        
        # Configurar solicitud para APC Makito
        solicitud.descargar_apc_makito = True
        solicitud.apc_no_cedula = numero_documento
        solicitud.apc_tipo_documento = tipo_documento
        solicitud.apc_status = 'pending'
        solicitud.apc_fecha_solicitud = timezone.now()
        
        solicitud.save(update_fields=[
            'descargar_apc_makito', 'apc_no_cedula', 'apc_tipo_documento', 
            'apc_status', 'apc_fecha_solicitud'
        ])
        
        # Enviar correo a Makito RPA
        enviar_correo_apc_makito(
            solicitud=solicitud,
            no_cedula=numero_documento,
            tipo_documento=tipo_documento,
            request=request
        )
        
        # Crear historial
        try:
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=solicitud.etapa_actual,
                usuario_responsable=request.user,
                fecha_inicio=timezone.now(),
                observaciones=f"APC solicitado a Makito RPA por {request.user.get_full_name() or request.user.username} - Documento: {tipo_documento.upper()} {numero_documento}"
            )
        except Exception as hist_error:
            print(f"⚠️ Error al crear historial APC: {hist_error}")
        
        return JsonResponse({
            'success': True,
            'message': f'Solicitud APC para {cliente_info} enviada exitosamente a Makito RPA',
            'solicitud_codigo': solicitud.codigo,
            'apc_status': solicitud.apc_status
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        }, status=404)
    except Exception as e:
        print(f"❌ Error al solicitar APC para solicitud {solicitud_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)

# ==========================================
# SURA MAKITO SOLICITAR API
# ==========================================

@login_required
def api_solicitar_sura_makito(request, solicitud_id):
    """
    API para solicitar cotización SURA con Makito RPA
    """
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        }, status=405)

    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if not request.user.is_superuser:
            user_groups = request.user.groups.all()
            tiene_permiso = PermisoBandeja.objects.filter(
                grupo__in=user_groups,
                etapa=solicitud.etapa_actual
            ).exists()
            
            if not tiene_permiso and solicitud.creada_por != request.user and solicitud.asignada_a != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'No tiene permisos para modificar esta solicitud'
                }, status=403)
        
        # Verificar que la solicitud no tenga ya SURA procesado
        if solicitud.sura_status == 'completed':
            return JsonResponse({
                'success': False,
                'error': 'Esta solicitud ya tiene cotización SURA completada'
            }, status=400)
        
        # Obtener datos necesarios para SURA
        cliente_info = solicitud.cliente_nombre_completo or "Cliente no asignado"
        
        # Verificar información del cliente
        documento_cliente = None
        primer_nombre = ""
        primer_apellido = ""
        
        if hasattr(solicitud, 'cliente') and solicitud.cliente:
            documento_cliente = solicitud.cliente.cedulaCliente
            # Intentar extraer nombres del campo nombreCliente
            if solicitud.cliente.nombreCliente:
                nombres = solicitud.cliente.nombreCliente.split()
                if len(nombres) >= 2:
                    primer_nombre = nombres[0]
                    primer_apellido = nombres[-1]
                elif len(nombres) == 1:
                    primer_nombre = nombres[0]
        elif hasattr(solicitud, 'cotizacion') and solicitud.cotizacion:
            documento_cliente = solicitud.cotizacion.cedulaCliente
            # Intentar extraer nombres de la cotización si están disponibles
            if solicitud.cotizacion.nombreCliente:
                nombres = solicitud.cotizacion.nombreCliente.split()
                if len(nombres) >= 2:
                    primer_nombre = nombres[0]
                    primer_apellido = nombres[-1]
        
        if not documento_cliente:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró información del documento del cliente para procesar SURA'
            }, status=400)
        
        # Configurar solicitud para SURA Makito
        solicitud.sura_primer_nombre = primer_nombre
        solicitud.sura_primer_apellido = primer_apellido
        solicitud.sura_no_documento = documento_cliente
        solicitud.sura_status = 'pending'
        solicitud.sura_fecha_solicitud = timezone.now()
        solicitud.cotizar_sura_makito = True  # CRITICAL: This field is required for tracking
        
        solicitud.save(update_fields=[
            'sura_primer_nombre', 'sura_primer_apellido', 'sura_no_documento',
            'sura_status', 'sura_fecha_solicitud', 'cotizar_sura_makito'
        ])
        
        # Enviar correo a Makito RPA
        enviar_correo_sura_makito(
            solicitud=solicitud,
            sura_primer_nombre=primer_nombre,
            sura_primer_apellido=primer_apellido,
            sura_no_documento=documento_cliente,
            request=request
        )
        
        # Crear historial
        try:
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=solicitud.etapa_actual,
                usuario_responsable=request.user,
                fecha_inicio=timezone.now(),
                observaciones=f"Cotización SURA solicitada a Makito RPA por {request.user.get_full_name() or request.user.username}"
            )
        except Exception as hist_error:
            print(f"⚠️ Error al crear historial SURA: {hist_error}")
        
        return JsonResponse({
            'success': True,
            'message': f'Solicitud de cotización SURA para {cliente_info} enviada exitosamente a Makito RPA',
            'solicitud_codigo': solicitud.codigo,
            'sura_status': solicitud.sura_status
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        }, status=404)
    except Exception as e:
        print(f"❌ Error al solicitar SURA para solicitud {solicitud_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)

@login_required
def api_debida_diligencia_tracking(request):
    """
    API para obtener datos de tracking de debida diligencia
    """
    try:
        # Obtener parámetros de filtrado
        status_filter = request.GET.get('status', '')
        fecha_desde = request.GET.get('fecha_desde', '')
        fecha_hasta = request.GET.get('fecha_hasta', '')
        
        # Construir queryset base - solo solicitudes con debida diligencia iniciada
        solicitudes = Solicitud.objects.exclude(
            debida_diligencia_status='no_iniciado'
        ).select_related(
            'pipeline', 'etapa_actual', 'creada_por', 'asignada_a', 'cliente'
        )
        
        # Aplicar filtro de usuario si no es superuser
        if not request.user.is_superuser:
            solicitudes = solicitudes.filter(propietario=request.user)
        
        solicitudes = solicitudes.order_by('-diligencia_fecha_solicitud')
        
        # Aplicar filtros
        if status_filter:
            solicitudes = solicitudes.filter(debida_diligencia_status=status_filter)
        
        if fecha_desde:
            try:
                fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                solicitudes = solicitudes.filter(diligencia_fecha_solicitud__date__gte=fecha_desde_obj)
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                solicitudes = solicitudes.filter(diligencia_fecha_solicitud__date__lte=fecha_hasta_obj)
            except ValueError:
                pass
        
        # Serializar datos
        solicitudes_data = []
        for solicitud in solicitudes:
            # Obtener nombre del cliente
            cliente_nombre = ""
            if solicitud.cliente:
                cliente_nombre = f"{solicitud.cliente.nombreCliente or ''}"
            elif solicitud.cliente_nombre:
                cliente_nombre = solicitud.cliente_nombre
            else:
                cliente_nombre = "Cliente no asignado"
            
            # Obtener nombre del usuario que creó la solicitud
            creada_por_nombre = ""
            if solicitud.creada_por:
                creada_por_nombre = solicitud.creada_por.get_full_name() or solicitud.creada_por.username
            
            solicitud_data = {
                'id': solicitud.id,
                'codigo': solicitud.codigo,
                'cliente_nombre': cliente_nombre,
                'pipeline_nombre': solicitud.pipeline.nombre if solicitud.pipeline else 'N/A',
                'etapa_actual_nombre': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'N/A',
                'debida_diligencia_status': solicitud.debida_diligencia_status,
                'diligencia_fecha_solicitud': solicitud.diligencia_fecha_solicitud.isoformat() if solicitud.diligencia_fecha_solicitud else None,
                'diligencia_fecha_inicio': solicitud.diligencia_fecha_inicio.isoformat() if solicitud.diligencia_fecha_inicio else None,
                'diligencia_fecha_completado': solicitud.diligencia_fecha_completado.isoformat() if solicitud.diligencia_fecha_completado else None,
                'diligencia_observaciones': solicitud.diligencia_observaciones or '',
                'diligencia_busqueda_google': solicitud.diligencia_busqueda_google.url if solicitud.diligencia_busqueda_google else None,
                'diligencia_busqueda_registro_publico': solicitud.diligencia_busqueda_registro_publico.url if solicitud.diligencia_busqueda_registro_publico else None,
                'diligencia_google_fecha_subida': solicitud.diligencia_google_fecha_subida.isoformat() if solicitud.diligencia_google_fecha_subida else None,
                'diligencia_registro_publico_fecha_subida': solicitud.diligencia_registro_publico_fecha_subida.isoformat() if solicitud.diligencia_registro_publico_fecha_subida else None,
                'creada_por_nombre': creada_por_nombre,
                'fecha_creacion': solicitud.fecha_creacion.isoformat() if solicitud.fecha_creacion else None
            }
            solicitudes_data.append(solicitud_data)
        
        return JsonResponse({
            'success': True,
            'solicitudes': solicitudes_data,
            'total': len(solicitudes_data)
        })
        
    except Exception as e:
        print(f"❌ Error en api_debida_diligencia_tracking: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)


@login_required
@csrf_exempt
def api_cambiar_etapa(request, solicitud_id):
    """API para cambiar la etapa de una solicitud"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Obtener la solicitud
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos usando la función helper
        if not usuario_puede_modificar_solicitud(request.user, solicitud):
            print(f"❌ DEBUG: Usuario {request.user.username} no tiene permisos para cambiar solicitud {solicitud_id}")
            print(f"❌ DEBUG: Creada por: {solicitud.creada_por.username if solicitud.creada_por else 'None'}")
            print(f"❌ DEBUG: Asignada a: {solicitud.asignada_a.username if solicitud.asignada_a else 'None'}")
            return JsonResponse({'error': 'No tienes permisos para cambiar esta solicitud'}, status=403)
        
        print(f"🔑 DEBUG: Usuario {request.user.username} tiene permisos para cambiar solicitud {solicitud_id}")
        
        # Obtener datos del request
        data = json.loads(request.body)
        print(f"🔍 DEBUG: Request data received: {data}")
        
        nueva_etapa_id = data.get('etapa_destino_id') or data.get('etapa_id')
        nuevo_subestado_id = data.get('subestado_id')
        print(f"🔍 DEBUG: Nueva etapa ID extracted: {nueva_etapa_id}")
        print(f"🔍 DEBUG: Nuevo subestado ID extracted: {nuevo_subestado_id}")
        
        if not nueva_etapa_id:
            print(f"❌ ERROR: No etapa ID found in request data")
            return JsonResponse({'error': 'ID de etapa requerido'}, status=400)
        
        # Obtener la nueva etapa
        nueva_etapa = get_object_or_404(Etapa, id=nueva_etapa_id, pipeline=solicitud.pipeline)
        
        # Obtener el nuevo subestado si se especifica, o automáticamente el primero si hay subestados disponibles
        nuevo_subestado = None
        if nuevo_subestado_id:
            try:
                nuevo_subestado = get_object_or_404(SubEstado, id=nuevo_subestado_id, etapa=nueva_etapa)
                print(f"🔍 DEBUG: Nuevo subestado especificado: {nuevo_subestado.nombre}")
            except Exception as e:
                print(f"❌ ERROR: Invalid subestado ID: {e}")
                return JsonResponse({'error': 'ID de subestado inválido'}, status=400)
        else:
            # Si no se especificó subestado, seleccionar automáticamente el primero disponible
            primer_subestado = SubEstado.objects.filter(etapa=nueva_etapa).order_by('orden', 'id').first()
            if primer_subestado:
                nuevo_subestado = primer_subestado
                print(f"🔍 DEBUG: Subestado asignado automáticamente: {nuevo_subestado.nombre}")
            else:
                print(f"🔍 DEBUG: No hay subestados para la etapa {nueva_etapa.nombre}")
        
        # Verificar que la etapa sea diferente a la actual
        if solicitud.etapa_actual == nueva_etapa:
            return JsonResponse({'error': 'La solicitud ya está en esta etapa'}, status=400)
        
        # NUEVO: Verificar que existe una transición válida definida
        transicion = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual,
            etapa_destino=nueva_etapa
        ).first()
        
        if not transicion:
            return JsonResponse({
                'error': 'Transición no válida',
                'tipo_error': 'transicion_invalida',
                'mensaje': f'No existe una transición válida de "{solicitud.etapa_actual.nombre}" a "{nueva_etapa.nombre}". Solo se permiten transiciones definidas en el pipeline.'
            }, status=400)
        
        # Verificar requisitos obligatorios para esta transición
        requisitos_faltantes = verificar_requisitos_transicion(solicitud, transicion)
        if requisitos_faltantes:
            return JsonResponse({
                'error': 'Requisitos faltantes',
                'tipo_error': 'requisitos_faltantes',
                'requisitos_faltantes': requisitos_faltantes,
                'mensaje': f'Faltan {len(requisitos_faltantes)} requisito(s) obligatorio(s) para continuar a "{nueva_etapa.nombre}"'
            }, status=400)
        
        # NUEVO: Verificar que todos los campos de compliance estén calificados
        # Solo aplicar esta verificación para etapas que requieren compliance
        etapas_que_requieren_compliance = ['Comité', 'Aprobación', 'Análisis de Crédito', 'Revisión Final']
        requiere_compliance = nueva_etapa.nombre in etapas_que_requieren_compliance
        
        print(f"🔍 DEBUG: Etapa destino: {nueva_etapa.nombre}, requiere compliance: {requiere_compliance}")
        
        if requiere_compliance:
            campos_sin_calificar = verificar_campos_compliance(solicitud)
            if campos_sin_calificar:
                return JsonResponse({
                    'error': 'Campos sin calificar',
                    'tipo_error': 'campos_sin_calificar',
                    'campos_sin_calificar': campos_sin_calificar,
                    'mensaje': f'Hay {len(campos_sin_calificar)} campo(s) sin calificar. Todos los campos deben estar marcados como "Bueno" o "Malo" antes de cambiar a la etapa "{nueva_etapa.nombre}".'
                }, status=400)
        
        # NUEVO: Verificar que existe al menos un comentario de analista
        # Solo requerir comentarios de analista para etapas específicas
        etapas_que_requieren_analisis = ['Comité', 'Aprobación', 'Análisis de Crédito']
        requiere_analisis = nueva_etapa.nombre in etapas_que_requieren_analisis
        
        print(f"🔍 DEBUG: Etapa destino: {nueva_etapa.nombre}, requiere análisis: {requiere_analisis}")
        
        if requiere_analisis:
            tiene_comentario_analista = verificar_comentario_analista(solicitud)
            if not tiene_comentario_analista:
                return JsonResponse({
                    'error': 'Análisis general requerido',
                    'tipo_error': 'analisis_general_faltante',
                    'mensaje': f'Debe completar el análisis general antes de cambiar a la etapa "{nueva_etapa.nombre}". Agregue su análisis en la sección "Comentarios de Analista".'
                }, status=400)
        
        # Cerrar el historial actual si existe
        if solicitud.etapa_actual:
            historial_actual = HistorialSolicitud.objects.filter(
                solicitud=solicitud,
                etapa=solicitud.etapa_actual,
                fecha_fin__isnull=True
            ).first()
            
            if historial_actual:
                historial_actual.fecha_fin = timezone.now()
                historial_actual.save()
        
        # Cambiar la etapa y subestado
        etapa_anterior = solicitud.etapa_actual
        subestado_anterior = solicitud.subestado_actual
        solicitud.etapa_actual = nueva_etapa
        solicitud.subestado_actual = nuevo_subestado
        solicitud.fecha_ultima_actualizacion = timezone.now()
        
        # Si la nueva etapa es grupal, quitar asignación individual
        if nueva_etapa.es_bandeja_grupal:
            solicitud.asignada_a = None
        
        solicitud.save()
        
        # Crear nuevo historial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=nueva_etapa,
            usuario_responsable=request.user,
            fecha_inicio=timezone.now()
        )
        
        # 🚨 CRÍTICO: Notificar cambio de etapa en tiempo real a TODAS las vistas
        notify_solicitud_change(solicitud, 'solicitud_cambio_etapa', request.user)
        
        # 📧 NUEVO: Enviar correo automático según el tipo de etapa
        print(f"🔍 DEBUG: Verificando etapa {nueva_etapa.nombre} - es_bandeja_grupal: {nueva_etapa.es_bandeja_grupal}")
        
        # Enviar correo específico del comité si la nueva etapa es "Comité de Crédito"
        if nueva_etapa.nombre.lower() == "comité de crédito":
            print(f"📧 ACTIVANDO envío de correo del comité para solicitud {solicitud.codigo}")
            enviar_correo_comite_credito(solicitud, nueva_etapa, request)
        elif nueva_etapa.es_bandeja_grupal:
            # Solo enviar correo de bandeja grupal para etapas que NO sean el comité
            print(f"📧 ACTIVANDO envío de correo de bandeja grupal para solicitud {solicitud.codigo} en etapa {nueva_etapa.nombre}")
            enviar_correo_bandeja_grupal(solicitud, nueva_etapa, request)
        else:
            print(f"ℹ️ No se envía correo - la etapa {nueva_etapa.nombre} no es bandeja grupal")
        
        # 📧 NUEVO: Enviar correo al propietario de la solicitud con comentarios analista
        try:
            # Obtener comentarios de analista
            comentarios_analista = []
            analisis_general = ""
            bullet_points = []
            
            try:
                from workflow.models import CalificacionCampo
                comentarios_analista = CalificacionCampo.objects.filter(
                    solicitud=solicitud,
                    campo__startswith='comentario_analista_credito_'
                ).select_related('usuario').order_by('-fecha_modificacion')
                
                # Obtener el análisis general (el comentario más reciente)
                if comentarios_analista:
                    analisis_general = comentarios_analista[0].comentario
                
                # Obtener bullet points de compliance (comentarios de campos)
                compliance_comments = CalificacionCampo.objects.filter(
                    solicitud=solicitud,
                    comentario__isnull=False
                ).exclude(
                    comentario=''
                ).exclude(
                    campo__startswith='comentario_analista_credito_'
                ).select_related('usuario')
                
                # Crear bullet points estructurados
                for calificacion in compliance_comments:
                    if calificacion.comentario and calificacion.comentario.strip():
                        # Obtener nombre legible del campo
                        nombre_campo = obtener_nombre_campo_legible(calificacion.campo, solicitud)
                        bullet_points.append({
                            'campo': nombre_campo,
                            'comentario': calificacion.comentario.strip(),
                            'estado': calificacion.estado,
                            'usuario': calificacion.usuario.get_full_name() or calificacion.usuario.username,
                            'fecha': calificacion.fecha_modificacion.strftime('%d/%m/%Y %H:%M')
                        })
                
            except Exception as e:
                print(f"⚠️ Error obteniendo comentarios analista: {e}")
            
            # Enviar correo al propietario
            print(f"📧 Enviando correo de cambio de etapa para solicitud {solicitud.codigo}")
            print(f"📧 Propietario: {solicitud.creada_por.email if solicitud.creada_por else 'Sin propietario'}")
            print(f"📧 Análisis general: {'Sí' if analisis_general else 'No'}")
            print(f"📧 Comentarios de analista: {len(comentarios_analista)}")
            print(f"📧 Bullet points: {len(bullet_points)}")
            
            enviar_correo_cambio_etapa_propietario(
                solicitud, 
                etapa_anterior, 
                nueva_etapa, 
                comentarios_analista, 
                bullet_points,
                analisis_general,
                request.user,
                request
            )
            
            # Enviar correo especial con PDF para etapa "Resultado Consulta"
            if nueva_etapa.nombre == "Resultado Consulta":
                print(f"📧 Enviando correo con PDF de Resultado Consulta para solicitud {solicitud.codigo}")
                try:
                    enviar_correo_pdf_resultado_consulta(solicitud)
                except Exception as e:
                    print(f"⚠️ Error al enviar correo con PDF de Resultado Consulta: {e}")
        except Exception as e:
            print(f"⚠️ Error al enviar correo al propietario: {e}")
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Solicitud {solicitud.codigo} movida de "{etapa_anterior.nombre if etapa_anterior else "Sin etapa"}" a "{nueva_etapa.nombre}"' + (f' - {nuevo_subestado.nombre}' if nuevo_subestado else ''),
            'nueva_etapa': {
                'id': nueva_etapa.id,
                'nombre': nueva_etapa.nombre,
                'orden': nueva_etapa.orden
            },
            'nuevo_subestado': {
                'id': nuevo_subestado.id if nuevo_subestado else None,
                'nombre': nuevo_subestado.nombre if nuevo_subestado else None
            },
            'etapa_anterior': {
                'id': etapa_anterior.id if etapa_anterior else None,
                'nombre': etapa_anterior.nombre if etapa_anterior else None
            },
            'subestado_anterior': {
                'id': subestado_anterior.id if subestado_anterior else None,
                'nombre': subestado_anterior.nombre if subestado_anterior else None
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def verificar_requisitos_transicion(solicitud, transicion):
    """
    Verificar si faltan requisitos obligatorios para una transición específica
    """
    # Obtener requisitos obligatorios para esta transición
    requisitos_transicion = RequisitoTransicion.objects.filter(
        transicion=transicion,
        obligatorio=True
    ).select_related('requisito')
    
    requisitos_faltantes = []
    
    for req_transicion in requisitos_transicion:
        # Verificar si el requisito existe para esta solicitud
        requisito_solicitud = RequisitoSolicitud.objects.filter(
            solicitud=solicitud,
            requisito=req_transicion.requisito
        ).first()
        
        # Lógica especial para requisito de agenda de firma
        if req_transicion.requisito.tipo_especial == 'agenda_firma':
            # Para agenda de firma, verificar si existe una cita agendada
            from workflow.modelsWorkflow import AgendaFirma
            tiene_cita_agendada = AgendaFirma.objects.filter(solicitud=solicitud).exists()
            esta_cumplido = tiene_cita_agendada
        else:
            # Considerar un requisito como cumplido si:
            # 1. Existe el RequisitoSolicitud Y
            # 2. (Tiene archivo O está marcado como cumplido)
            # Esto permite que archivos subidos desde el drawer se consideren válidos
            esta_cumplido = bool(requisito_solicitud and (requisito_solicitud.archivo or requisito_solicitud.cumplido))
        
        # Si no está cumplido, agregarlo a requisitos faltantes
        if not esta_cumplido:
            requisitos_faltantes.append({
                'id': req_transicion.requisito.id,
                'nombre': req_transicion.requisito.nombre,
                'descripcion': req_transicion.requisito.descripcion,
                'mensaje_personalizado': req_transicion.mensaje_personalizado,
                'tiene_archivo': bool(requisito_solicitud and requisito_solicitud.archivo),
                'esta_cumplido': esta_cumplido,
                'requisito_solicitud_id': requisito_solicitud.id if requisito_solicitud else None
            })
    
    return requisitos_faltantes


def verificar_campos_compliance(solicitud):
    """
    Verificar que todos los campos de compliance estén calificados (bueno o malo)
    """
    from workflow.models import CalificacionCampo
    
    # Definir todos los campos que deben estar calificados
    campos_requeridos = [
        # Campos de información del cliente
        'empresa_privada', 'cargo', 'tiempo_servicio', 'salario', 'score',
        # Campos de detalle de la solicitud
        'valor_equipo', 'abono', 'monto_financiado', 'plazo', 'rentabilidad', 'total_letra',
        # Campos del vehículo
        'marca', 'modelo', 'año', 'transmision', 'kilometraje'
    ]
    
    # Obtener calificaciones existentes
    calificaciones = CalificacionCampo.objects.filter(
        solicitud=solicitud
    ).values_list('campo', 'estado')
    
    # Crear diccionario de calificaciones
    calificaciones_dict = dict(calificaciones)
    
    # Verificar campos de documentos
    requisitos_solicitud = RequisitoSolicitud.objects.filter(solicitud=solicitud)
    for requisito in requisitos_solicitud:
        campo_doc = f'doc_{requisito.id}'
        campos_requeridos.append(campo_doc)
    
    # Verificar campos sin calificar
    campos_sin_calificar = []
    
    for campo in campos_requeridos:
        estado = calificaciones_dict.get(campo)
        if not estado or estado == 'sin_calificar':
            # Obtener nombre legible del campo
            nombre_campo = obtener_nombre_campo_legible(campo, solicitud)
            campos_sin_calificar.append({
                'campo': campo,
                'nombre': nombre_campo,
                'tipo': 'documento' if campo.startswith('doc_') else 'campo'
            })
    
    return campos_sin_calificar


def verificar_comentario_analista(solicitud):
    """
    Verificar que existe al menos un comentario de analista de crédito
    """
    from workflow.models import CalificacionCampo
    
    # Buscar comentarios de analista (campos que empiecen con 'comentario_analista_credito_')
    comentarios_analista = CalificacionCampo.objects.filter(
        solicitud=solicitud,
        campo__startswith='comentario_analista_credito_'
    ).exclude(comentario__isnull=True).exclude(comentario='')
    
    return comentarios_analista.exists()


def obtener_nombre_campo_legible(campo, solicitud):
    """
    Obtener el nombre legible de un campo para mostrar en errores
    """
    nombres_campos = {
        'empresa_privada': 'Empresa Privada',
        'cargo': 'Cargo',
        'tiempo_servicio': 'Tiempo de Servicio',
        'salario': 'Salario',
        'score': 'Score',
        'valor_equipo': 'Valor del Equipo',
        'abono': 'Abono',
        'monto_financiado': 'Monto Financiado',
        'plazo': 'Plazo',
        'rentabilidad': 'Rentabilidad',
        'total_letra': 'Total de Letra',
        'marca': 'Marca',
        'modelo': 'Modelo',
        'año': 'Año',
        'transmision': 'Transmisión',
        'kilometraje': 'Kilometraje'
    }
    
    # Si es un campo de documento
    if campo.startswith('doc_'):
        try:
            doc_id = int(campo.replace('doc_', ''))
            requisito_solicitud = RequisitoSolicitud.objects.get(
                id=doc_id, 
                solicitud=solicitud
            )
            return f"Documento: {requisito_solicitud.requisito.nombre}"
        except RequisitoSolicitud.DoesNotExist:
            return f"Documento ID: {doc_id}"
    
    return nombres_campos.get(campo, campo)


@login_required
def vista_mixta_bandejas(request):
    """Vista mixta que combina bandeja grupal y personal"""
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta
    from .modelsWorkflow import Solicitud, Etapa, Pipeline, PermisoEtapa, HistorialSolicitud
    
    # Obtener etapa_id del parámetro GET
    etapa_id = request.GET.get('etapa_id')
    etapa_seleccionada = None
    
    if etapa_id:
        try:
            etapa_seleccionada = Etapa.objects.get(id=etapa_id, es_bandeja_grupal=True)
        except Etapa.DoesNotExist:
            # Si la etapa no existe o no es bandeja grupal, redirigir sin parámetro
            return HttpResponseRedirect(request.path)
    
    # === SISTEMA DE PERMISOS SUPERUSER Y SUPER STAFF ===
    # Los usuarios superuser y super staff (is_staff=True) pueden ver TODO
    if request.user.is_superuser or request.user.is_staff:
        # Superuser y super staff ven TODAS las solicitudes en ambas bandejas
        if etapa_seleccionada:
            # Si hay etapa seleccionada, filtrar solo por esa etapa
            etapas_grupales = Etapa.objects.filter(id=etapa_seleccionada.id)
        else:
            # Si no hay etapa seleccionada, mostrar todas las etapas grupales excepto Comité de Crédito
            etapas_grupales = Etapa.objects.filter(es_bandeja_grupal=True).exclude(nombre__iexact="Comité de Crédito")
        
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        ).order_by('-fecha_creacion')
        
        # Superuser y super staff ven solicitudes personales en las etapas actuales de bandeja grupal
        if etapa_seleccionada:
            # Si hay una etapa específica seleccionada, mostrar solo solicitudes asignadas en esa etapa
            solicitudes_personales = Solicitud.objects.filter(
                asignada_a__isnull=False,
                etapa_actual=etapa_seleccionada
            ).select_related(
                'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
                'creada_por', 'asignada_a'
            ).order_by('-fecha_ultima_actualizacion')
        else:
            # Si no hay etapa específica, mostrar solicitudes asignadas en cualquier etapa de bandeja grupal
            solicitudes_personales = Solicitud.objects.filter(
                asignada_a__isnull=False,
                etapa_actual__in=etapas_grupales
            ).select_related(
                'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
                'creada_por', 'asignada_a'
            ).order_by('-fecha_ultima_actualizacion')
    else:
        # Usuarios regulares - permisos normales
        grupos_usuario = request.user.groups.all()
        
        # === BANDEJA GRUPAL ===
        # Obtener etapas grupales donde el usuario tiene permisos
        if etapa_seleccionada:
            # Si hay etapa seleccionada, verificar que el usuario tenga permisos para esa etapa específica
            etapas_grupales = Etapa.objects.filter(
                id=etapa_seleccionada.id,
                es_bandeja_grupal=True,
                permisos__grupo__in=grupos_usuario,
                permisos__puede_autoasignar=True
            ).distinct()
        else:
            # Si no hay etapa seleccionada, mostrar todas las etapas donde tiene permisos excepto Comité de Crédito
            etapas_grupales = Etapa.objects.filter(
                es_bandeja_grupal=True,
                permisos__grupo__in=grupos_usuario,
                permisos__puede_autoasignar=True
            ).exclude(nombre__iexact="Comité de Crédito").distinct()
        
        # Solicitudes grupales (sin asignar)
        solicitudes_grupales = Solicitud.objects.filter(
            etapa_actual__in=etapas_grupales,
            asignada_a__isnull=True
        ).select_related(
            'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
            'creada_por', 'asignada_a'
        ).order_by('-fecha_creacion')
        
        # === BANDEJA PERSONAL ===
        # Solicitudes asignadas al usuario en las etapas actuales de bandeja grupal
        if etapa_seleccionada:
            # Si hay una etapa específica seleccionada, mostrar solo solicitudes asignadas en esa etapa
            solicitudes_personales = Solicitud.objects.filter(
                asignada_a=request.user,
                etapa_actual=etapa_seleccionada
            ).select_related(
                'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
                'creada_por', 'asignada_a'
            ).order_by('-fecha_ultima_actualizacion')
        else:
            # Si no hay etapa específica, mostrar solicitudes asignadas en cualquier etapa de bandeja grupal
            solicitudes_personales = Solicitud.objects.filter(
                asignada_a=request.user,
                etapa_actual__in=etapas_grupales
            ).select_related(
                'cliente', 'cotizacion', 'pipeline', 'etapa_actual', 'subestado_actual', 
                'creada_por', 'asignada_a'
            ).order_by('-fecha_ultima_actualizacion')
    
    # === MÉTRICAS ===
    # Total en bandeja grupal
    total_grupo = solicitudes_grupales.count()
    
    # Mis tareas
    mis_tareas = solicitudes_personales.count()
    
    # Calcular vencimientos
    ahora = timezone.now()
    
    # Solicitudes por vencer (próximas 24 horas)
    por_vencer = 0
    en_tiempo = 0
    
    todas_solicitudes = list(solicitudes_grupales) + list(solicitudes_personales)
    
    for solicitud in todas_solicitudes:
        if solicitud.etapa_actual and solicitud.etapa_actual.sla:
            fecha_vencimiento = solicitud.fecha_ultima_actualizacion + solicitud.etapa_actual.sla
            
            if fecha_vencimiento < ahora:
                # Ya vencida
                continue
            elif fecha_vencimiento <= ahora + timedelta(hours=24):
                # Por vencer en 24 horas
                por_vencer += 1
            else:
                # En tiempo
                en_tiempo += 1
    
    # Filtros
    filtro_pipeline = request.GET.get('pipeline', '')
    filtro_estado = request.GET.get('estado', '')
    
    if filtro_pipeline:
        solicitudes_grupales = solicitudes_grupales.filter(pipeline_id=filtro_pipeline)
        solicitudes_personales = solicitudes_personales.filter(pipeline_id=filtro_pipeline)
    
    if filtro_estado == 'vencidas':
        # Filtrar solo las vencidas
        solicitudes_vencidas_ids = []
        for solicitud in todas_solicitudes:
            if solicitud.etapa_actual and solicitud.etapa_actual.sla:
                fecha_vencimiento = solicitud.fecha_ultima_actualizacion + solicitud.etapa_actual.sla
                if fecha_vencimiento < ahora:
                    solicitudes_vencidas_ids.append(solicitud.id)
        
        solicitudes_grupales = solicitudes_grupales.filter(id__in=solicitudes_vencidas_ids)
        solicitudes_personales = solicitudes_personales.filter(id__in=solicitudes_vencidas_ids)
    
    # Agregar información de vencimiento y enriquecimiento a cada solicitud
    def agregar_info_vencimiento(solicitudes):
        for solicitud in solicitudes:
            # Obtener fecha de inicio en la etapa actual desde HistorialSolicitud
            if solicitud.etapa_actual:
                historial_actual = HistorialSolicitud.objects.filter(
                    solicitud=solicitud,
                    etapa=solicitud.etapa_actual,
                    fecha_fin__isnull=True
                ).order_by('-fecha_inicio').first()
                
                if historial_actual:
                    solicitud.fecha_inicio_etapa = historial_actual.fecha_inicio
                else:
                    # Si no hay historial actual, usar la fecha de última actualización como fallback
                    solicitud.fecha_inicio_etapa = solicitud.fecha_ultima_actualizacion
            else:
                solicitud.fecha_inicio_etapa = None
            
            # Información de SLA
            if solicitud.etapa_actual and solicitud.etapa_actual.sla:
                fecha_vencimiento = solicitud.fecha_ultima_actualizacion + solicitud.etapa_actual.sla
                solicitud.fecha_vencimiento = fecha_vencimiento
                solicitud.esta_vencida = fecha_vencimiento < ahora
                solicitud.por_vencer = fecha_vencimiento <= ahora + timedelta(hours=24)
                
                # Calcular SLA restante y color
                tiempo_total = solicitud.etapa_actual.sla.total_seconds()
                tiempo_transcurrido = (ahora - solicitud.fecha_ultima_actualizacion).total_seconds()
                segundos_restantes = tiempo_total - tiempo_transcurrido
                porcentaje_restante = (segundos_restantes / tiempo_total) * 100 if tiempo_total > 0 else 0
                
                abs_segundos = abs(int(segundos_restantes))
                horas = abs_segundos // 3600
                minutos = (abs_segundos % 3600) // 60
                
                if segundos_restantes < 0:
                    if horas > 0:
                        solicitud.sla_restante = f"-{horas}h {minutos}m"
                    else:
                        solicitud.sla_restante = f"-{minutos}m"
                    solicitud.sla_color = 'text-danger'
                elif porcentaje_restante > 40:
                    if horas > 0:
                        solicitud.sla_restante = f"{horas}h {minutos}m"
                    else:
                        solicitud.sla_restante = f"{minutos}m"
                    solicitud.sla_color = 'text-success'
                elif porcentaje_restante > 0:
                    if horas > 0:
                        solicitud.sla_restante = f"{horas}h {minutos}m"
                    else:
                        solicitud.sla_restante = f"{minutos}m"
                    solicitud.sla_color = 'text-warning'
                else:
                    if horas > 0:
                        solicitud.sla_restante = f"-{horas}h {minutos}m"
                    else:
                        solicitud.sla_restante = f"-{minutos}m"
                    solicitud.sla_color = 'text-danger'
            else:
                solicitud.fecha_vencimiento = None
                solicitud.esta_vencida = False
                solicitud.por_vencer = False
                solicitud.sla_restante = 'N/A'
                solicitud.sla_color = 'text-secondary'
            
            # Las propiedades del modelo ya están disponibles directamente
            # No es necesario asignar nada - cliente_nombre, cliente_cedula, etc. 
            # están disponibles automáticamente como propiedades del modelo
            
            # Debug temporal para verificar que las propiedades funcionan correctamente
            try:
                # Estas propiedades se pueden leer sin problema
                _ = solicitud.cliente_nombre
                _ = solicitud.cliente_cedula
                _ = solicitud.monto_formateado
                _ = solicitud.producto_descripcion
            except Exception as e:
                print(f"Error accediendo propiedades del modelo: {e}")
            
            # Estado actual
            solicitud.estado_actual = solicitud.subestado_actual.nombre if solicitud.subestado_actual else ("En Proceso" if solicitud.etapa_actual else "Completado")
            
        return solicitudes
    
    solicitudes_grupales = agregar_info_vencimiento(solicitudes_grupales)
    solicitudes_personales = agregar_info_vencimiento(solicitudes_personales)
    
    # Obtener datos únicos para los filtros
    todas_solicitudes_para_filtros = list(solicitudes_grupales) + list(solicitudes_personales)
    
    clientes_unicos = set()
    estados_unicos = set()
    etapas_unicas = set()
    
    for solicitud in todas_solicitudes_para_filtros:
        if hasattr(solicitud, 'cliente_nombre') and solicitud.cliente_nombre:
            clientes_unicos.add(solicitud.cliente_nombre)
        if hasattr(solicitud, 'estado_actual') and solicitud.estado_actual:
            estados_unicos.add(solicitud.estado_actual)
        if solicitud.etapa_actual:
            etapas_unicas.add(solicitud.etapa_actual.nombre)
    
    # Convertir a listas ordenadas
    clientes_unicos = sorted(list(clientes_unicos))
    estados_unicos = sorted(list(estados_unicos))
    etapas_unicas = sorted(list(etapas_unicas))
    
    # Obtener todas las etapas con bandeja habilitada (para el dropdown) excepto Comité de Crédito
    etapas_con_bandeja = Etapa.objects.filter(es_bandeja_grupal=True).exclude(nombre__iexact="Comité de Crédito").select_related('pipeline')
    
    context = {
        'solicitudes_grupales': solicitudes_grupales,
        'solicitudes_personales': solicitudes_personales,
        'total_grupo': total_grupo,
        'mis_tareas': mis_tareas,
        'por_vencer': por_vencer,
        'en_tiempo': en_tiempo,
        'pipelines': Pipeline.objects.all(),
        'clientes_unicos': clientes_unicos,
        'estados_unicos': estados_unicos,
        'etapas_unicas': etapas_unicas,
        'etapas_con_bandeja': etapas_con_bandeja,
        'etapa_seleccionada': etapa_seleccionada,
        'filtros': {
            'pipeline': filtro_pipeline,
            'estado': filtro_estado,
            'etapa_id': etapa_id,
        }
    }
    
    return render(request, 'workflow/vista_mixta_bandejas.html', context)


@login_required
def api_tomar_solicitud(request, solicitud_id):
    """API para tomar una solicitud de bandeja grupal"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar que la solicitud está en bandeja grupal
        if not solicitud.etapa_actual.es_bandeja_grupal or solicitud.asignada_a:
            return JsonResponse({
                'success': False, 
                'error': 'Esta solicitud no está disponible para tomar.'
            })
        
        # === SISTEMA DE PERMISOS SUPER STAFF ===
        # Los usuarios super staff (is_staff=True) pueden tomar cualquier solicitud
        if request.user.is_staff:
            # Super staff tiene permisos completos
            tiene_permiso = True
        else:
            # Verificar permisos regulares para usuarios normales
            grupos_usuario = request.user.groups.all()
            tiene_permiso = PermisoEtapa.objects.filter(
                etapa=solicitud.etapa_actual,
                grupo__in=grupos_usuario,
                puede_autoasignar=True
            ).exists()
        
        if not tiene_permiso:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para tomar solicitudes en esta etapa.'
            })
        
        # Asignar solicitud
        solicitud.asignada_a = request.user
        solicitud.fecha_ultima_actualizacion = timezone.now()
        solicitud.save()
        
        # Actualizar historial
        historial_actual = HistorialSolicitud.objects.filter(
            solicitud=solicitud,
            etapa=solicitud.etapa_actual,
            fecha_fin__isnull=True
        ).first()
        
        if historial_actual:
            historial_actual.usuario_responsable = request.user
            historial_actual.save()
        
        # CRÍTICO: Notificar cambio en tiempo real
        notify_solicitud_change(solicitud, 'solicitud_tomada', request.user)
        
        # 📧 NUEVO: Enviar correo de notificación al creador de la solicitud
        print(f"📧 ACTIVANDO envío de correo de asignación para solicitud {solicitud.codigo}")
        enviar_correo_solicitud_asignada(solicitud, request.user, request)
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Solicitud {solicitud.codigo} asignada exitosamente.',
            'solicitud': {
                'id': solicitud.id,
                'codigo': solicitud.codigo,
                'asignada_a': request.user.get_full_name() or request.user.username
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_devolver_solicitud(request, solicitud_id):
    """API para devolver una solicitud a bandeja grupal"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # === SISTEMA DE PERMISOS SUPER STAFF ===
        # Los usuarios super staff (is_staff=True) pueden devolver cualquier solicitud
        if request.user.is_staff:
            # Super staff tiene permisos completos
            puede_devolver = True
        elif request.user.is_superuser:
            # Superuser también puede devolver cualquier solicitud
            puede_devolver = True
        elif solicitud.asignada_a == request.user:
            # Usuario regular solo puede devolver sus propias solicitudes
            puede_devolver = True
        else:
            puede_devolver = False
        
        if not puede_devolver:
            return JsonResponse({
                'success': False,
                'error': 'No puedes devolver esta solicitud.'
            })
        
        # Verificar que la etapa actual permite bandeja grupal
        if not solicitud.etapa_actual.es_bandeja_grupal:
            return JsonResponse({
                'success': False,
                'error': 'Esta etapa no permite bandeja grupal.'
            })
        
        # Devolver a bandeja grupal
        solicitud.asignada_a = None
        solicitud.fecha_ultima_actualizacion = timezone.now()
        solicitud.save()
        
        # CRÍTICO: Notificar cambio en tiempo real
        notify_solicitud_change(solicitud, 'solicitud_devuelta', request.user)
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Solicitud {solicitud.codigo} devuelta a bandeja grupal.',
            'solicitud': {
                'id': solicitud.id,
                'codigo': solicitud.codigo
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_kpis(request):
    """API para obtener KPIs actualizados"""
    try:
        # Obtener solicitudes del usuario
        solicitudes_usuario = Solicitud.objects.filter(
            etapa_actual__pipeline__grupos__in=request.user.groups.all()
        ).select_related('etapa_actual', 'asignada_a', 'cliente')
        
        # Calcular métricas
        total_grupo = solicitudes_usuario.filter(
            etapa_actual__es_bandeja_grupal=True,
            asignada_a__isnull=True
        ).count()
        
        mis_tareas = solicitudes_usuario.filter(
            asignada_a=request.user
        ).count()
        
        # Calcular por vencer y en tiempo
        por_vencer = 0
        en_tiempo = 0
        
        def calcular_sla_solicitud(solicitud):
            """Calcular SLA para una solicitud específica"""
            if solicitud.etapa_actual and solicitud.etapa_actual.sla_horas:
                fecha_inicio = solicitud.fecha_creacion
                sla_horas = solicitud.etapa_actual.sla_horas
                fecha_vencimiento = fecha_inicio + timedelta(hours=sla_horas)
                ahora = timezone.now()
                
                segundos_restantes = (fecha_vencimiento - ahora).total_seconds()
                porcentaje_restante = (segundos_restantes / (sla_horas * 3600)) * 100
                
                if segundos_restantes < 0:
                    return 'text-danger'
                elif porcentaje_restante > 40:
                    return 'text-success'
                elif porcentaje_restante > 0:
                    return 'text-warning'
                else:
                    return 'text-danger'
            return 'text-secondary'
        
        for solicitud in solicitudes_usuario:
            sla_color = calcular_sla_solicitud(solicitud)
            if sla_color == 'text-warning':
                por_vencer += 1
            elif sla_color == 'text-success':
                en_tiempo += 1
        
        return JsonResponse({
            'success': True,
            'total_grupo': total_grupo,
            'mis_tareas': mis_tareas,
            'por_vencer': por_vencer,
            'en_tiempo': en_tiempo
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def api_bandejas(request):
    """API para obtener contenido actualizado de las bandejas"""
    try:
        # Obtener solicitudes del usuario
        solicitudes_usuario = Solicitud.objects.filter(
            etapa_actual__pipeline__grupos__in=request.user.groups.all()
        ).select_related('etapa_actual', 'asignada_a', 'cliente')
        
        # Bandeja grupal
        bandeja_grupal = solicitudes_usuario.filter(
            etapa_actual__es_bandeja_grupal=True,
            asignada_a__isnull=True
        ).order_by('-fecha_creacion')
        
        # Bandeja personal
        bandeja_personal = solicitudes_usuario.filter(
            asignada_a=request.user
        ).order_by('-fecha_creacion')
        
        def generar_info_solicitud(solicitud):
            """Generar información completa de una solicitud"""
            info = {
                'cliente_nombre': 'Sin cliente',
                'cliente_cedula': 'Sin cédula',
                'sla_color': 'text-secondary',
                'tiempo_restante': 'N/A'
            }
            
            # Información de cliente
            try:
                from pacifico.models import Cotizacion
                cotizacion = Cotizacion.objects.filter(
                    solicitud_workflow=solicitud
                ).first()
                
                if cotizacion:
                    info['cliente_nombre'] = cotizacion.cliente or 'Sin cliente'
                    info['cliente_cedula'] = cotizacion.cedulaCliente or 'Sin cédula'
            except:
                pass
            
            # Información de SLA
            if solicitud.etapa_actual and solicitud.etapa_actual.sla_horas:
                fecha_inicio = solicitud.fecha_creacion
                sla_horas = solicitud.etapa_actual.sla_horas
                fecha_vencimiento = fecha_inicio + timedelta(hours=sla_horas)
                ahora = timezone.now()
                
                segundos_restantes = (fecha_vencimiento - ahora).total_seconds()
                porcentaje_restante = (segundos_restantes / (sla_horas * 3600)) * 100
                abs_segundos = abs(segundos_restantes)
                horas = abs_segundos // 3600
                minutos = (abs_segundos % 3600) // 60
                
                if segundos_restantes < 0:
                    info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    info['sla_color'] = 'text-danger'
                elif porcentaje_restante > 40:
                    info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    info['sla_color'] = 'text-success'
                elif porcentaje_restante > 0:
                    info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    info['sla_color'] = 'text-warning'
                else:
                    info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    info['sla_color'] = 'text-danger'
            
            return info
        
        # Generar HTML para bandeja grupal
        html_grupal = ""
        for solicitud in bandeja_grupal:
            info = generar_info_solicitud(solicitud)
            estado_actual = solicitud.subestado_actual.nombre if solicitud.subestado_actual else ("En Proceso" if solicitud.etapa_actual else "Completado")
            
            html_grupal += f"""
            <tr class="solicitud-row" data-cliente="{info['cliente_nombre']}" 
                data-estado="{estado_actual}" 
                data-etapa="{solicitud.etapa_actual.nombre}" 
                data-sla="{info['sla_color']}" 
                data-search="{solicitud.codigo} {info['cliente_nombre']} {info['cliente_cedula']}"
                id="solicitud-grupal-{solicitud.id}">
                <td>
                    <span class="badge bg-primary">{solicitud.codigo}</span>
                </td>
                <td>{info['cliente_nombre']}</td>
                <td>{info['cliente_cedula']}</td>
                <td>
                    <span class="badge bg-info">{solicitud.etapa_actual.nombre}</span>
                </td>
                <td>
                    <i class="fas fa-circle {info['sla_color']} me-1"></i>
                    {info['tiempo_restante']}
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-success btn-sm tomar-solicitud" 
                                data-solicitud-id="{solicitud.id}" 
                                data-codigo="{solicitud.codigo}">
                            <i class="fas fa-hand-paper me-1"></i>Tomar
                        </button>
                        <button class="btn btn-info btn-sm ver-detalle" 
                                data-solicitud-id="{solicitud.id}">
                            <i class="fas fa-eye me-1"></i>Ver
                        </button>
                    </div>
                </td>
            </tr>
            """
        
        # Generar HTML para bandeja personal
        html_personal = ""
        for solicitud in bandeja_personal:
            info = generar_info_solicitud(solicitud)
            estado_actual = solicitud.subestado_actual.nombre if solicitud.subestado_actual else ("En Proceso" if solicitud.etapa_actual else "Completado")
            
            html_personal += f"""
            <tr class="solicitud-row" data-cliente="{info['cliente_nombre']}" 
                data-estado="{estado_actual}" 
                data-etapa="{solicitud.etapa_actual.nombre}" 
                data-sla="{info['sla_color']}" 
                data-search="{solicitud.codigo} {info['cliente_nombre']} {info['cliente_cedula']}"
                id="solicitud-personal-{solicitud.id}">
                <td>
                    <span class="badge bg-primary">{solicitud.codigo}</span>
                </td>
                <td>{info['cliente_nombre']}</td>
                <td>{info['cliente_cedula']}</td>
                <td>
                    <span class="badge bg-info">{solicitud.etapa_actual.nombre}</span>
                </td>
                <td>
                    <i class="fas fa-circle {info['sla_color']} me-1"></i>
                    {info['tiempo_restante']}
                </td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-warning btn-sm devolver-solicitud" 
                                data-solicitud-id="{solicitud.id}" 
                                data-codigo="{solicitud.codigo}">
                            <i class="fas fa-undo me-1"></i>Devolver
                        </button>
                        <button class="btn btn-primary btn-sm procesar-solicitud" 
                                data-solicitud-id="{solicitud.id}">
                            <i class="fas fa-cogs me-1"></i>Procesar
                        </button>
                        <button class="btn btn-info btn-sm ver-detalle" 
                                data-solicitud-id="{solicitud.id}">
                            <i class="fas fa-eye me-1"></i>Ver
                        </button>
                    </div>
                </td>
            </tr>
            """
        
        return JsonResponse({
            'success': True,
            'bandeja_grupal': html_grupal,
            'bandeja_personal': html_personal
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def test_envio_correo_bandeja(request):
    """
    Vista temporal para probar el envío de correos de bandeja grupal.
    Usar solo para testing - eliminar después.
    """
    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud_id')
        if solicitud_id:
            try:
                solicitud = Solicitud.objects.get(id=solicitud_id)
                etapa = solicitud.etapa_actual
                
                if etapa and etapa.es_bandeja_grupal:
                    enviar_correo_bandeja_grupal(solicitud, etapa, request)
                    return JsonResponse({
                        'success': True,
                        'message': f'Correo enviado para solicitud {solicitud.codigo}'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'La etapa actual no es bandeja grupal'
                    })
            except Solicitud.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Solicitud no encontrada'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error: {str(e)}'
                })
    
    # Listar solicitudes para testing
    solicitudes = Solicitud.objects.filter(etapa_actual__es_bandeja_grupal=True)[:10]
    
    return render(request, 'workflow/test_correo.html', {
        'solicitudes': solicitudes
    })


@login_required
def test_envio_correo_asignacion(request):
    """
    Vista temporal para probar el envío de correos de asignación.
    Usar solo para testing - eliminar después.
    """
    if request.method == 'POST':
        solicitud_id = request.POST.get('solicitud_id')
        if solicitud_id:
            try:
                solicitud = Solicitud.objects.get(id=solicitud_id)
                
                if solicitud.asignada_a:
                    enviar_correo_solicitud_asignada(solicitud, solicitud.asignada_a, request)
                    return JsonResponse({
                        'success': True,
                        'message': f'Correo de asignación enviado para solicitud {solicitud.codigo}'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'La solicitud no está asignada'
                    })
            except Solicitud.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Solicitud no encontrada'
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'message': f'Error: {str(e)}'
                })
    
    # Listar solicitudes asignadas para testing
    solicitudes = Solicitud.objects.filter(asignada_a__isnull=False)[:10]
    
    return render(request, 'workflow/test_correo_asignacion.html', {
        'solicitudes': solicitudes
    })


@login_required
def test_envio_correo_cambio_etapa(request):
    """Función de prueba para enviar correo de cambio de etapa con análisis"""
    try:
        # Obtener una solicitud de prueba
        solicitud = Solicitud.objects.first()
        if not solicitud:
            return JsonResponse({'error': 'No hay solicitudes disponibles para la prueba'})
        
        # Simular datos de prueba
        etapa_anterior = solicitud.etapa_actual
        nueva_etapa = solicitud.etapa_actual  # Usar la misma para la prueba
        
        # Crear comentarios de prueba
        comentarios_analista = []
        analisis_general = "Este es un análisis general de prueba que incluye una evaluación completa de la solicitud del cliente."
        
        # Crear bullet points de prueba
        bullet_points = [
            {
                'campo': 'Empresa Privada',
                'comentario': 'La empresa tiene buena reputación y estabilidad financiera.',
                'estado': 'bueno',
                'usuario': request.user.get_full_name() or request.user.username,
                'fecha': timezone.now().strftime('%d/%m/%Y %H:%M')
            },
            {
                'campo': 'Salario',
                'comentario': 'El salario es adecuado para el monto solicitado.',
                'estado': 'bueno',
                'usuario': request.user.get_full_name() or request.user.username,
                'fecha': timezone.now().strftime('%d/%m/%Y %H:%M')
            },
            {
                'campo': 'Documento de Identidad',
                'comentario': 'Documento válido y legible.',
                'estado': 'bueno',
                'usuario': request.user.get_full_name() or request.user.username,
                'fecha': timezone.now().strftime('%d/%m/%Y %H:%M')
            }
        ]
        
        # Enviar correo
        enviar_correo_cambio_etapa_propietario(
            solicitud, 
            etapa_anterior, 
            nueva_etapa, 
            comentarios_analista, 
            bullet_points,
            analisis_general,
            request.user,
            request
        )
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Correo de cambio de etapa con análisis enviado para solicitud {solicitud.codigo}'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)})


@login_required
def api_get_updated_solicitudes(request):
    """API para obtener solo las solicitudes que han sido actualizadas"""
    try:
        # Obtener timestamp de la última consulta
        last_check = request.GET.get('last_check')
        if last_check:
            try:
                last_check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            except:
                last_check_time = timezone.now() - timedelta(minutes=5)
        else:
            last_check_time = timezone.now() - timedelta(minutes=5)
        
        view_type = request.GET.get('view', 'bandejas')
        
        # Obtener solicitudes actualizadas
        solicitudes_base = Solicitud.objects.filter(
            etapa_actual__pipeline__grupos__in=request.user.groups.all(),
            fecha_ultima_actualizacion__gt=last_check_time
        ).select_related('etapa_actual', 'asignada_a', 'pipeline')
        
        # Formatear datos según la vista
        solicitudes_data = []
        
        for solicitud in solicitudes_base:
            # Información de cliente
            cliente_nombre = 'Sin cliente'
            cliente_cedula = 'Sin cédula'
            
            try:
                from pacifico.models import Cotizacion
                cotizacion = Cotizacion.objects.filter(
                    solicitud_workflow=solicitud
                ).first()
                
                if cotizacion:
                    cliente_nombre = cotizacion.cliente or 'Sin cliente'
                    cliente_cedula = cotizacion.cedulaCliente or 'Sin cédula'
            except:
                pass
            
            # Calcular SLA
            sla_info = {
                'color': 'text-secondary',
                'tiempo_restante': 'N/A'
            }
            
            if solicitud.etapa_actual and solicitud.etapa_actual.sla_horas:
                fecha_inicio = solicitud.fecha_creacion
                sla_horas = solicitud.etapa_actual.sla_horas
                fecha_vencimiento = fecha_inicio + timedelta(hours=sla_horas)
                ahora = timezone.now()
                
                segundos_restantes = (fecha_vencimiento - ahora).total_seconds()
                porcentaje_restante = (segundos_restantes / (sla_horas * 3600)) * 100
                abs_segundos = abs(segundos_restantes)
                horas = abs_segundos // 3600
                minutos = (abs_segundos % 3600) // 60
                
                if segundos_restantes < 0:
                    sla_info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    sla_info['color'] = 'text-danger'
                elif porcentaje_restante > 40:
                    sla_info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    sla_info['color'] = 'text-success'
                elif porcentaje_restante > 0:
                    sla_info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    sla_info['color'] = 'text-warning'
                else:
                    sla_info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    sla_info['color'] = 'text-danger'
            
            solicitudes_data.append({
                'id': solicitud.id,
                'codigo': solicitud.codigo,
                'cliente_nombre': cliente_nombre,
                'cliente_cedula': cliente_cedula,
                'etapa': {
                    'id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
                    'nombre': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
                    'es_bandeja_grupal': solicitud.etapa_actual.es_bandeja_grupal if solicitud.etapa_actual else False
                },
                'asignada_a': {
                    'id': solicitud.asignada_a.id if solicitud.asignada_a else None,
                    'username': solicitud.asignada_a.username if solicitud.asignada_a else None,
                    'nombre_completo': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else None
                },
                'estado_actual': solicitud.subestado_actual.nombre if solicitud.subestado_actual else "En Proceso",
                'sla': sla_info,
                'fecha_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
                'fecha_creacion': solicitud.fecha_creacion.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'solicitudes': solicitudes_data,
            'total': len(solicitudes_data),
            'timestamp': timezone.now().isoformat(),
            'last_check': last_check_time.isoformat(),
            'view': view_type
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        })


@login_required
def api_solicitud_brief(request, solicitud_id):
    """API: Briefing de una solicitud para el modal"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)

        # General info
        general = {
            'codigo': solicitud.codigo,
            'estado': solicitud.subestado_actual.nombre if solicitud.subestado_actual else (solicitud.etapa_actual.nombre if solicitud.etapa_actual else '-'),
            'tipo': solicitud.pipeline.nombre if solicitud.pipeline else '-',
            'fecha_inicio': solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M') if solicitud.fecha_creacion else '-',
            'vencimiento': solicitud.historial.last().fecha_fin.strftime('%d/%m/%Y') if solicitud.historial.last() and solicitud.historial.last().fecha_fin else '-',
            'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else '-',
            'area': '-',  # Campo no existe en el modelo, usar valor por defecto
            'propietario': (
                solicitud.propietario.get_full_name() or solicitud.propietario.username
            ) if solicitud.propietario else (
                solicitud.creada_por.get_full_name() or solicitud.creada_por.username
            ) if solicitud.creada_por else 'N/A',
            'es_etapa_grupal': solicitud.etapa_actual.es_bandeja_grupal if solicitud.etapa_actual else False,
            'resultado_consulta': solicitud.resultado_consulta if hasattr(solicitud, 'resultado_consulta') else 'Pendiente',
            'es_reconsideracion': solicitud.es_reconsideracion if hasattr(solicitud, 'es_reconsideracion') else False,
            'propietario_id': solicitud.propietario.id if solicitud.propietario else (solicitud.creada_por.id if solicitud.creada_por else None),
            'subestado_actual': solicitud.subestado_actual.nombre if solicitud.subestado_actual else None,
        }

        # Cliente info
        cliente = solicitud.cliente
        cliente_info = {
            'nombre': cliente.nombreCliente if cliente else '-',
            'cedula': cliente.cedulaCliente if cliente else '-',
            'canal': '-',  # Campo no existe en el modelo, usar valor por defecto
        }

        # Acciones (permisos y flags)
        acciones = {
            'puede_procesar': True,  # TODO: lógica de permisos
            'puede_devolver': True,
            'puede_anular': True,
            'puede_comentar': True,
        }

        # Workflow progress (etapas)
        workflow = []
        if solicitud.pipeline:
            etapas = solicitud.pipeline.etapas.order_by('orden')
            for etapa in etapas:
                # Calcular SLA en días desde el campo sla (DurationField)
                sla_dias = None
                if etapa.sla:
                    sla_dias = etapa.sla.days
                
                etapa_dict = {
                    'nombre': etapa.nombre,
                    'completada': solicitud.historial.filter(etapa=etapa, fecha_fin__isnull=False).exists(),
                    'actual': solicitud.etapa_actual_id == etapa.id,
                    'responsable': '-',  # Campo no existe en el modelo
                    'sla': f"{sla_dias} días" if sla_dias else None
                }
                workflow.append(etapa_dict)

        # Historial - Combine stage changes, comments, and other events
        historial = []
        
        # Add stage changes from HistorialSolicitud
        for h in solicitud.historial.all().order_by('fecha_inicio'):
            historial.append({
                'etapa': h.etapa.nombre if h.etapa else '-',
                'subestado': h.subestado.nombre if h.subestado else '-',
                'usuario': h.usuario_responsable.get_full_name() if h.usuario_responsable else '-',
                'fecha_inicio': h.fecha_inicio.isoformat() if h.fecha_inicio else None,
                'fecha_fin': h.fecha_fin.isoformat() if h.fecha_fin else None,
                'tipo': 'etapa'
            })
        
        # Add comments
        if hasattr(solicitud, 'comentarios'):
            for c in solicitud.comentarios.all().order_by('-fecha_creacion'):
                historial.append({
                    'texto': c.comentario,
                    'usuario': c.usuario.get_full_name() if c.usuario else '-',
                    'fecha_creacion': c.fecha_creacion.isoformat() if c.fecha_creacion else None,
                    'tipo': 'comentario'
                })
        
        # Add document uploads from requisitos
        for req in solicitud.requisitos.all():
            if req.archivo and req.cumplido:
                historial.append({
                    'nombre': req.requisito.nombre,
                    'archivo': req.archivo.url if req.archivo else None,
                    'usuario': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else '-',
                    'fecha_creacion': solicitud.fecha_ultima_actualizacion.isoformat() if solicitud.fecha_ultima_actualizacion else None,
                    'tipo': 'documento'
                })
        
        # Sort all events by date (most recent first)
        historial.sort(key=lambda x: x.get('fecha_inicio') or x.get('fecha_creacion') or '', reverse=True)

        # Comentarios
        comentarios = []
        if hasattr(solicitud, 'comentarios'):
            comentarios = [
                {
                    'usuario': c.usuario.get_full_name() if c.usuario else '-',
                    'texto': c.comentario,  # Campo correcto del modelo
                    'fecha': c.fecha_creacion.strftime('%d/%m/%Y %H:%M') if c.fecha_creacion else '-',
                }
                for c in solicitud.comentarios.all().order_by('-fecha_creacion')
            ]

        # Datos personales
        datos_personales = {}
        if cliente:
            datos_personales = {
                'Nombre Completo': cliente.nombreCliente or '-',
                'Cédula de Identidad': cliente.cedulaCliente or '-',
                'Teléfono': getattr(cliente, 'telefono', '-') or '-',
                'Dirección': getattr(cliente, 'direccion', '-') or '-',
                'Email': getattr(cliente, 'email', '-') or '-',
            }
        elif solicitud.cotizacion:
            datos_personales = {
                'Nombre Completo': solicitud.cotizacion.nombreCliente or '-',
                'Cédula de Identidad': solicitud.cotizacion.cedulaCliente or '-',
                'Teléfono': getattr(solicitud.cotizacion, 'telefono', '-') or '-',
                'Dirección': getattr(solicitud.cotizacion, 'direccion', '-') or '-',
                'Email': getattr(solicitud.cotizacion, 'email', '-') or '-',
            }

        # Información financiera
        info_financiera = {}
        cotizacion = solicitud.cotizacion
        if cotizacion:
            info_financiera = {
                'Ingresos': str(cotizacion.ingresos) if cotizacion.ingresos is not None else '-',
                'Empresa': cotizacion.nombreEmpresa or '-',
                'Cargo': cotizacion.posicion or '-',
                'Salario Base Mensual': str(getattr(cotizacion, 'salarioBaseMensual', '-')),
                'Cartera': cotizacion.cartera or '-',
                'Referencias APC': cotizacion.referenciasAPC or '-',
            }

        # Referencias (pueden venir de cotizacion o modelos relacionados)
        referencias = []
        # Si hay referencias en cotizacion, agregarlas
        if cotizacion and hasattr(cotizacion, 'referenciasAPC') and cotizacion.referenciasAPC:
            referencias.append({'nombre': 'APC', 'tipo': 'APC', 'relacion': '', 'telefono': '', 'descripcion': cotizacion.referenciasAPC})
        # TODO: Agregar referencias personales/comerciales si existen modelos relacionados

        # Documentos (de requisitos) - CON INFORMACIÓN DE CALIFICACIÓN
        from .models import CalificacionDocumentoBackoffice, RequisitoTransicion
        
        documentos = []
        for req in solicitud.requisitos.all():
            # Obtener calificación más reciente si existe
            calificacion = CalificacionDocumentoBackoffice.objects.filter(
                requisito_solicitud=req
            ).order_by('-fecha_calificacion').first()
            
            # Obtener información de obligatoriedad - MEJORADA PARA INCLUIR MÁS CASOS
            es_obligatorio = False
            
            # 1. Primero verificar en RequisitoTransicion para la etapa actual
            if solicitud.etapa_actual:
                transiciones_entrada = TransicionEtapa.objects.filter(
                    pipeline=solicitud.pipeline,
                    etapa_destino=solicitud.etapa_actual
                )
                for transicion in transiciones_entrada:
                    req_transicion = RequisitoTransicion.objects.filter(
                        transicion=transicion,
                        requisito=req.requisito
                    ).first()
                    if req_transicion:
                        es_obligatorio = req_transicion.obligatorio
                        break
            
            # 2. Si no se encontró en RequisitoTransicion, verificar en RequisitoPipeline
            if not es_obligatorio:
                from .modelsWorkflow import RequisitoPipeline
                req_pipeline = RequisitoPipeline.objects.filter(
                    pipeline=solicitud.pipeline,
                    requisito=req.requisito
                ).first()
                if req_pipeline:
                    es_obligatorio = req_pipeline.obligatorio
            
            # 3. Para efectos del tab "Documentos Pendientes", si no está definido
            # en ningún lado, se considera NO obligatorio (opcional)
            
            documento_info = {
                'id': req.id,  # Add the RequisitoSolicitud ID
                'nombre': req.requisito.nombre,
                'url': req.archivo.url if req.archivo else '',
                'cumplido': req.cumplido,
                'observaciones': req.observaciones or '',
                # Nuevos campos para calificación
                'obligatorio': es_obligatorio,
                'calificacion_estado': calificacion.estado if calificacion else None,
                'motivo_calificacion': calificacion.opcion_desplegable.nombre if calificacion and calificacion.opcion_desplegable else None,
                'calificado_por': calificacion.calificado_por.get_full_name() or calificacion.calificado_por.username if calificacion else None,
                'fecha_calificacion': calificacion.fecha_calificacion.strftime('%d/%m/%Y %H:%M') if calificacion else None,
                'subsanado': calificacion.subsanado if calificacion else False,
                'subsanado_por': calificacion.subsanado_por.get_full_name() or calificacion.subsanado_por.username if calificacion and calificacion.subsanado_por else None,
                'fecha_subsanado': calificacion.fecha_subsanado.strftime('%d/%m/%Y %H:%M') if calificacion and calificacion.fecha_subsanado else None,
                # NUEVOS CAMPOS TEMPORALMENTE COMENTADOS HASTA EJECUTAR MIGRATION
                # 'subsanado_por_oficial': calificacion.subsanado_por_oficial if calificacion else False,
                # 'pendiente_completado': calificacion.pendiente_completado if calificacion else False,
                'subsanado_por_oficial': False,  # Temporal - hasta migration
                'pendiente_completado': False,   # Temporal - hasta migration
            }
            
            # DEBUGGING: Log documentos que pueden aparecer como pendientes
            if not es_obligatorio or not req.cumplido or not req.archivo:
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"🔍 DEBUG DOCUMENTO POTENCIAL PENDIENTE: {req.requisito.nombre} (ID:{req.id}) - obligatorio:{es_obligatorio}, cumplido:{req.cumplido}, tiene_archivo:{bool(req.archivo)}, url:'{req.archivo.url if req.archivo else 'VACIO'}")
            
            # Special handling for APC requisito
            if req.requisito.nombre.lower() == 'apc':
                # Check if APC is being processed by Makito RPA
                if solicitud.descargar_apc_makito and solicitud.apc_status in ['pending', 'in_progress']:
                    documento_info['apc_status'] = solicitud.apc_status
                    documento_info['apc_processing'] = True
                    documento_info['apc_fecha_solicitud'] = solicitud.apc_fecha_solicitud.strftime('%d/%m/%Y %H:%M') if solicitud.apc_fecha_solicitud else None
                    documento_info['apc_fecha_inicio'] = solicitud.apc_fecha_inicio.strftime('%d/%m/%Y %H:%M') if solicitud.apc_fecha_inicio else None
                    documento_info['apc_fecha_completado'] = solicitud.apc_fecha_completado.strftime('%d/%m/%Y %H:%M') if solicitud.apc_fecha_completado else None
                    documento_info['apc_observaciones'] = solicitud.apc_observaciones
                    
                    # If APC is completed, mark the requisito as fulfilled
                    if solicitud.apc_status == 'completed' and solicitud.apc_archivo:
                        documento_info['cumplido'] = True
                        documento_info['url'] = solicitud.apc_archivo.url if solicitud.apc_archivo else ''
                        documento_info['apc_processing'] = False
                        documento_info['apc_completed'] = True
                else:
                    documento_info['apc_processing'] = False
            
            # Special handling for SURA requisito
            if req.requisito.nombre.lower() == 'sura' or req.requisito.nombre.lower() == 'cotización sura':
                # Check if SURA is being processed by Makito RPA
                if solicitud.cotizar_sura_makito and solicitud.sura_status in ['pending', 'in_progress']:
                    documento_info['sura_status'] = solicitud.sura_status
                    documento_info['sura_processing'] = True
                    documento_info['sura_fecha_solicitud'] = solicitud.sura_fecha_solicitud.strftime('%d/%m/%Y %H:%M') if solicitud.sura_fecha_solicitud else None
                    documento_info['sura_fecha_inicio'] = solicitud.sura_fecha_inicio.strftime('%d/%m/%Y %H:%M') if solicitud.sura_fecha_inicio else None
                    documento_info['sura_fecha_completado'] = solicitud.sura_fecha_completado.strftime('%d/%m/%Y %H:%M') if solicitud.sura_fecha_completado else None
                    documento_info['sura_observaciones'] = solicitud.sura_observaciones
                    
                    # If SURA is completed, mark the requisito as fulfilled
                    if solicitud.sura_status == 'completed' and solicitud.sura_archivo:
                        documento_info['cumplido'] = True
                        documento_info['url'] = solicitud.sura_archivo.url if solicitud.sura_archivo else ''
                        documento_info['sura_processing'] = False
                        documento_info['sura_completed'] = True
                else:
                    documento_info['sura_processing'] = False
            
            documentos.append(documento_info)
            
            # DEBUG: Log específicamente documentos calificados como "malo"
            if calificacion and calificacion.estado == 'malo':
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"🔴 DOCUMENTO MALO ENVIADO AL FRONTEND: {req.requisito.nombre} (ID:{req.id}) - estado:{calificacion.estado}, subsanado:{calificacion.subsanado}, motivo:{calificacion.opcion_desplegable.nombre if calificacion.opcion_desplegable else 'Sin motivo'}")
            
            # DEBUG: Log todos los documentos que se envían al frontend
            if req.requisito.nombre.lower() in ['foto', 'proforma', 'excel']:  # Solo documentos comunes para no spam
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"📤 ENVIANDO AL FRONTEND: {req.requisito.nombre} - cumplido:{req.cumplido}, url:'{req.archivo.url if req.archivo else 'VACIO'}', obligatorio:{es_obligatorio}")

        # Cotización info
        cotizacion_info = {}
        import logging
        logger = logging.getLogger(__name__)
        
        if cotizacion:
            logger.debug(f"Cotizacion found: {cotizacion}")
            logger.debug(f"Cotizacion edad: {cotizacion.edad} (type: {type(cotizacion.edad)})")
            logger.debug(f"Cotizacion sexo: {cotizacion.sexo} (type: {type(cotizacion.sexo)})")
            logger.debug(f"Cotizacion cartera: {cotizacion.cartera} (type: {type(cotizacion.cartera)})")
            
            cotizacion_info = {
                'monto': float(cotizacion.montoPrestamo) if cotizacion.montoPrestamo else 0,
                'plazo': cotizacion.plazoPago or '-',
                'tasa': float(cotizacion.tasaInteres) if cotizacion.tasaInteres else '-',
                'cuota': float(getattr(cotizacion, 'wrkMontoLetra', 0)) if hasattr(cotizacion, 'wrkMontoLetra') and cotizacion.wrkMontoLetra else '-',
                'auxMonto2': float(getattr(cotizacion, 'auxMonto2', 0)) if getattr(cotizacion, 'auxMonto2', None) is not None else 0,
                'edad': cotizacion.edad if cotizacion.edad is not None else None,
                'sexo': cotizacion.sexo if cotizacion.sexo else None,
                'cartera': cotizacion.cartera if cotizacion.cartera else None,
                'tipoPrestamo': cotizacion.tipoPrestamo if cotizacion.tipoPrestamo else None,
                'marca': cotizacion.marca if cotizacion.marca else None,
                'modelo': cotizacion.modelo if cotizacion.modelo else None,
            }
            
            logger.debug(f"Final cotizacion_info: {cotizacion_info}")
        else:
            logger.debug("No cotizacion found")

        # Datos de entrevista asociada (formulario general)
        entrevista_info = None
        if hasattr(solicitud, 'entrevista_cliente') and solicitud.entrevista_cliente:
            entrevista = solicitud.entrevista_cliente
            # Construir cédula completa
            cedula_completa = ""
            if entrevista.provincia_cedula and entrevista.tipo_letra and entrevista.tomo_cedula and entrevista.partida_cedula:
                cedula_completa = f"{entrevista.provincia_cedula}-{entrevista.tipo_letra}-{entrevista.tomo_cedula}-{entrevista.partida_cedula}"
            elif entrevista.tomo_cedula and entrevista.partida_cedula:
                cedula_completa = f"{entrevista.tomo_cedula}-{entrevista.partida_cedula}"
            
            entrevista_info = {
                'id': entrevista.id,
                'nombre_completo': f"{entrevista.primer_nombre or ''} {entrevista.segundo_nombre or ''} {entrevista.primer_apellido or ''} {entrevista.segundo_apellido or ''}".strip(),
                'cedula': cedula_completa,
                'email': entrevista.email or '',
                'telefono': entrevista.telefono or '',
                'fecha_entrevista': entrevista.fecha_entrevista.strftime('%d/%m/%Y') if entrevista.fecha_entrevista else '',
                'tipo_producto': entrevista.tipo_producto or ''
            }

        # Datos completos de la solicitud para funcionalidades de entrevista
        solicitud_info = {
            'id': solicitud.id,
            'codigo': solicitud.codigo,
            'cliente_nombre_completo': cliente_info.get('nombre', ''),
            'cliente_cedula_completa': cliente_info.get('cedula', ''),
            'entrevista_cliente': entrevista_info
        }

        return JsonResponse({
            'general': general,
            'cliente': cliente_info,
            'acciones': acciones,
            'workflow': workflow,
            'historial': historial,
            'comentarios': comentarios,
            'datos_personales': datos_personales,
            'info_financiera': info_financiera,
            'referencias': referencias,
            'documentos': documentos,
            'cotizacion': cotizacion_info,
            # Include the related Cotizacion primary key for redirection
            'cotizacion_id': solicitud.cotizacion.id if solicitud.cotizacion else None,
            # Datos de solicitud y entrevista para funcionalidades del modal
            'solicitud': solicitud_info,
        }, encoder=DjangoJSONEncoder)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener datos de la solicitud: {str(e)}'
        }, status=500)


@login_required
def api_solicitud_detalle(request, solicitud_id):
    """API completa para obtener todos los datos de una solicitud específica"""
    try:
        print(f"DEBUG: Starting api_solicitud_detalle for solicitud_id: {solicitud_id}")
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        print(f"DEBUG: Solicitud found: {solicitud.codigo}")
        
        # Verificar permisos
        if solicitud.asignada_a and solicitud.asignada_a != request.user:
            if not (request.user.is_superuser or request.user.is_staff):
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=solicitud.etapa_actual,
                    grupo__in=grupos_usuario,
                    puede_ver=True
                ).exists()
                
                if not tiene_permiso:
                    return JsonResponse({'error': 'No tienes permisos para ver esta solicitud.'}, status=403)

        # Calcular SLA detallado
        sla_info = calcular_sla_detallado(solicitud)
        
        # Información general de la solicitud
        general = {
            'id': solicitud.id,
            'codigo': solicitud.codigo,
            'pipeline': {
                'id': solicitud.pipeline.id if solicitud.pipeline else None,
                'nombre': solicitud.pipeline.nombre if solicitud.pipeline else ''
            } if solicitud.pipeline else None,
            'etapa_actual': {
                'id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
                'nombre': solicitud.etapa_actual.nombre if solicitud.etapa_actual else '',
                'es_bandeja_grupal': solicitud.etapa_actual.es_bandeja_grupal if solicitud.etapa_actual else False,
                'sla': solicitud.etapa_actual.sla.total_seconds() / 86400 if (solicitud.etapa_actual and solicitud.etapa_actual.sla) else None  # días
            } if solicitud.etapa_actual else None,
            'subestado_actual': {
                'id': solicitud.subestado_actual.id if solicitud.subestado_actual else None,
                'nombre': solicitud.subestado_actual.nombre if solicitud.subestado_actual else ''
            } if solicitud.subestado_actual else None,
            'creada_por': {
                'id': solicitud.creada_por.id if solicitud.creada_por else None,
                'nombre_completo': solicitud.creada_por.get_full_name() if solicitud.creada_por else '',
                'username': solicitud.creada_por.username if solicitud.creada_por else ''
            } if solicitud.creada_por else None,
            'asignada_a': {
                'id': solicitud.asignada_a.id if solicitud.asignada_a else None,
                'nombre_completo': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else '',
                'username': solicitud.asignada_a.username if solicitud.asignada_a else ''
            } if solicitud.asignada_a else None,
            'fecha_creacion': solicitud.fecha_creacion.isoformat() if solicitud.fecha_creacion else None,
            'fecha_ultima_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat() if solicitud.fecha_ultima_actualizacion else None,
            'motivo_consulta': getattr(solicitud, 'motivo_consulta', ''),
            'sla': sla_info,
            'puede_asignar': not solicitud.asignada_a and solicitud.etapa_actual and getattr(solicitud.etapa_actual, 'es_bandeja_grupal', False),
            'puede_devolver': solicitud.asignada_a == request.user,
            'puede_cambiar_estado': True  # TODO: implementar lógica de permisos específica
        }

        # Información del cliente
        cliente_info = {}
        if solicitud.cliente:
            cliente_info = {
                'id': solicitud.cliente.id,
                'nombre': getattr(solicitud.cliente, 'nombreCliente', ''),
                'cedula': getattr(solicitud.cliente, 'cedulaCliente', ''),
                'telefono': getattr(solicitud.cliente, 'telefono', None),
                'email': getattr(solicitud.cliente, 'email', None),
                'direccion': getattr(solicitud.cliente, 'direccion', None),
                'fecha_creacion': solicitud.cliente.created_at.isoformat() if hasattr(solicitud.cliente, 'created_at') and solicitud.cliente.created_at else None
            }

        # Información de la cotización
        cotizacion_info = {}
        if solicitud.cotizacion:
            cotizacion_info = {
                'id': solicitud.cotizacion.id,
                'monto_prestamo': float(getattr(solicitud.cotizacion, 'montoPrestamo', 0)) if getattr(solicitud.cotizacion, 'montoPrestamo', None) else 0,
                'plazo_pago': getattr(solicitud.cotizacion, 'plazoPago', None),
                'tasa_interes': float(getattr(solicitud.cotizacion, 'tasaInteres', 0)) if getattr(solicitud.cotizacion, 'tasaInteres', None) else 0,
                'nombre_cliente': getattr(solicitud.cotizacion, 'nombreCliente', ''),
                'cedula_cliente': getattr(solicitud.cotizacion, 'cedulaCliente', ''),
                'nombre_empresa': getattr(solicitud.cotizacion, 'nombreEmpresa', ''),
                'posicion': getattr(solicitud.cotizacion, 'posicion', ''),
                'ingresos': float(getattr(solicitud.cotizacion, 'ingresos', 0)) if getattr(solicitud.cotizacion, 'ingresos', None) else 0,
                'cartera': getattr(solicitud.cotizacion, 'cartera', ''),
                'referencias_apc': getattr(solicitud.cotizacion, 'referenciasAPC', ''),
                'edad': getattr(solicitud.cotizacion, 'edad', None),
                'sexo': getattr(solicitud.cotizacion, 'sexo', ''),
                'aux_monto2': float(getattr(solicitud.cotizacion, 'auxMonto2', 0)) if getattr(solicitud.cotizacion, 'auxMonto2', None) is not None else 0,
                'wrk_monto_letra': float(getattr(solicitud.cotizacion, 'wrkMontoLetra', 0)) if hasattr(solicitud.cotizacion, 'wrkMontoLetra') and getattr(solicitud.cotizacion, 'wrkMontoLetra', None) else 0
            }

        # Transiciones disponibles
        transiciones_disponibles = []
        if solicitud.etapa_actual:
            transiciones = TransicionEtapa.objects.filter(
                pipeline=solicitud.pipeline,
                etapa_origen=solicitud.etapa_actual
            )
            
            for transicion in transiciones:
                requisitos_faltantes = verificar_requisitos_transicion(solicitud, transicion)
                
                # Verificar permisos para la transición
                puede_realizar = True
                if transicion.requiere_permiso and not (request.user.is_superuser or request.user.is_staff):
                    grupos_usuario = request.user.groups.all()
                    tiene_permiso = PermisoEtapa.objects.filter(
                        etapa=transicion.etapa_destino,
                        grupo__in=grupos_usuario
                    ).exists()
                    puede_realizar = tiene_permiso
                
                transiciones_disponibles.append({
                    'id': transicion.id,
                    'nombre': transicion.nombre,
                    'etapa_destino': {
                        'id': transicion.etapa_destino.id,
                        'nombre': transicion.etapa_destino.nombre
                    },
                    'requiere_permiso': transicion.requiere_permiso,
                    'puede_realizar': puede_realizar and len(requisitos_faltantes) == 0,
                    'requisitos_faltantes': [
                        {
                            'id': req['id'],
                            'nombre': req['nombre'],
                            'descripcion': req['descripcion']
                        } for req in requisitos_faltantes
                    ]
                })

        # Historial de actividades
        historial = []
        for h in solicitud.historial.all().order_by('-fecha_inicio'):
            historial.append({
                'id': h.id,
                'etapa': {
                    'id': h.etapa.id,
                    'nombre': h.etapa.nombre
                } if h.etapa else None,
                'subestado': {
                    'id': h.subestado.id,
                    'nombre': h.subestado.nombre
                } if h.subestado else None,
                'usuario_responsable': {
                    'id': h.usuario_responsable.id,
                    'nombre_completo': h.usuario_responsable.get_full_name(),
                    'username': h.usuario_responsable.username
                } if h.usuario_responsable else None,
                'fecha_inicio': h.fecha_inicio.isoformat() if h.fecha_inicio else None,
                'fecha_fin': h.fecha_fin.isoformat() if h.fecha_fin else None
            })

        # Requisitos de la solicitud
        requisitos = []
        for req in solicitud.requisitos.all():
            requisitos.append({
                'id': req.id,
                'requisito': {
                    'id': req.requisito.id,
                    'nombre': req.requisito.nombre,
                    'descripcion': req.requisito.descripcion
                },
                'cumplido': req.cumplido,
                'archivo': req.archivo.url if req.archivo else None,
                'observaciones': req.observaciones
            })

        # Campos personalizados
        campos_personalizados = []
        valores_dict = {v.campo.id: v for v in solicitud.valores_personalizados.all()}
        
        for campo in CampoPersonalizado.objects.filter(pipeline=solicitud.pipeline):
            valor = valores_dict.get(campo.id)
            valor_actual = None
            
            if valor:
                if campo.tipo == 'texto':
                    valor_actual = valor.valor_texto
                elif campo.tipo == 'numero':
                    valor_actual = valor.valor_numero
                elif campo.tipo == 'entero':
                    valor_actual = valor.valor_entero
                elif campo.tipo == 'fecha':
                    valor_actual = valor.valor_fecha.isoformat() if valor.valor_fecha else None
                elif campo.tipo == 'booleano':
                    valor_actual = valor.valor_booleano
            
            campos_personalizados.append({
                'id': campo.id,
                'nombre': campo.nombre,
                'tipo': campo.tipo,
                'requerido': campo.requerido,
                'valor': valor_actual
            })

        # Progreso del pipeline
        progreso = 0
        if solicitud.pipeline and solicitud.etapa_actual:
            etapas_pipeline = solicitud.pipeline.etapas.order_by('orden')
            total_etapas = etapas_pipeline.count()
            if total_etapas > 0:
                try:
                    etapa_actual_orden = solicitud.etapa_actual.orden
                    progreso = min(100, int((etapa_actual_orden / total_etapas) * 100))
                except:
                    progreso = 0

        return JsonResponse({
            'success': True,
            'general': general,
            'cliente': cliente_info,
            'cotizacion': cotizacion_info,
            'transiciones_disponibles': transiciones_disponibles,
            'historial': historial,
            'requisitos': requisitos,
            'campos_personalizados': campos_personalizados,
            'progreso': progreso
        }, encoder=DjangoJSONEncoder)
        
    except Exception as e:
        import traceback
        print(f"DEBUG: Exception in api_solicitud_detalle: {str(e)}")
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener datos de la solicitud: {str(e)}',
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=500)


@login_required
def api_test_solicitud_detalle(request, solicitud_id):
    """API de prueba para verificar que el endpoint funciona"""
    try:
        print(f"DEBUG: Testing api_test_solicitud_detalle for solicitud_id: {solicitud_id}")
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        print(f"DEBUG: Test solicitud found: {solicitud.codigo}")
        
        # Test basic fields
        basic_info = {
            'id': solicitud.id,
            'codigo': solicitud.codigo,
            'pipeline_id': solicitud.pipeline.id if solicitud.pipeline else None,
            'etapa_actual_id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
            'creada_por_id': solicitud.creada_por.id if solicitud.creada_por else None,
            'asignada_a_id': solicitud.asignada_a.id if solicitud.asignada_a else None,
        }
        
        print(f"DEBUG: Basic info created: {basic_info}")
        
        return JsonResponse({
            'success': True,
            'message': 'API funcionando correctamente',
            'solicitud_id': solicitud.id,
            'solicitud_codigo': solicitud.codigo,
            'basic_info': basic_info,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        print(f"DEBUG: Exception in test endpoint: {str(e)}")
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc() if settings.DEBUG else None
        }, status=500)


# ==========================================
# VISTAS DE API PARA COMENTARIOS
# ==========================================

@login_required
def api_obtener_comentarios(request, solicitud_id):
    """API para obtener comentarios de una solicitud"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos para ver la solicitud (incluye supervisores de grupo)
        if not usuario_puede_modificar_solicitud(request.user, solicitud):
            return JsonResponse({'error': 'No tienes permisos para ver esta solicitud'}, status=403)
        
        # Obtener tipo de comentario del query parameter (opcional)
        tipo_filtro = request.GET.get('tipo')
        
        # Filtrar comentarios por tipo si se especifica
        if tipo_filtro and tipo_filtro in ['general', 'analista']:
            comentarios = solicitud.comentarios.filter(tipo=tipo_filtro).order_by('-fecha_creacion')
        else:
            comentarios = solicitud.comentarios.all().order_by('-fecha_creacion')
        
        datos_comentarios = []
        for comentario in comentarios:
            datos_comentarios.append({
                'id': comentario.id,
                'usuario': {
                    'id': comentario.usuario.id,
                    'username': comentario.usuario.username,
                    'nombre_completo': comentario.usuario.get_full_name() or comentario.usuario.username
                },
                'comentario': comentario.comentario,
                'tipo': comentario.tipo,
                'fecha_creacion': comentario.fecha_creacion.isoformat(),
                'fecha_modificacion': comentario.fecha_modificacion.isoformat(),
                'es_editado': comentario.es_editado,
                'tiempo_transcurrido': comentario.get_tiempo_transcurrido(),
                'puede_editar': comentario.usuario == request.user or request.user.is_superuser,
                'puede_eliminar': comentario.usuario == request.user or request.user.is_superuser
            })
        
        return JsonResponse({
            'success': True,
            'comentarios': datos_comentarios,
            'total': len(datos_comentarios)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_crear_comentario(request, solicitud_id):
    """API para crear un nuevo comentario"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos para comentar en la solicitud (incluye supervisores de grupo)
        if not usuario_puede_modificar_solicitud(request.user, solicitud):
            return JsonResponse({'error': 'No tienes permisos para comentar en esta solicitud'}, status=403)
        
        data = json.loads(request.body)
        comentario_texto = data.get('comentario', '').strip()
        
        if not comentario_texto:
            return JsonResponse({'error': 'El comentario no puede estar vacío'}, status=400)
        
        # Obtener tipo de comentario (por defecto 'general')
        tipo_comentario = data.get('tipo', 'general')
        
        # Validar tipo de comentario
        if tipo_comentario not in ['general', 'analista']:
            return JsonResponse({'error': 'Tipo de comentario inválido'}, status=400)
        
        # Crear el comentario
        comentario = SolicitudComentario.objects.create(
            solicitud=solicitud,
            usuario=request.user,
            comentario=comentario_texto,
            tipo=tipo_comentario
        )
        
        # Notificar cambio en tiempo real
        notify_solicitud_change(solicitud, 'nuevo_comentario', request.user)
        
        return JsonResponse({
            'success': True,
            'comentario': {
                'id': comentario.id,
                'usuario': {
                    'id': comentario.usuario.id,
                    'username': comentario.usuario.username,
                    'nombre_completo': comentario.usuario.get_full_name() or comentario.usuario.username
                },
                'comentario': comentario.comentario,
                'tipo': comentario.tipo,
                'fecha_creacion': comentario.fecha_creacion.isoformat(),
                'fecha_modificacion': comentario.fecha_modificacion.isoformat(),
                'es_editado': comentario.es_editado,
                'tiempo_transcurrido': comentario.get_tiempo_transcurrido(),
                'puede_editar': True,
                'puede_eliminar': True
            },
            'mensaje': 'Comentario creado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_editar_comentario(request, comentario_id):
    """API para editar un comentario existente"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        comentario = get_object_or_404(SolicitudComentario, id=comentario_id)
        
        # Verificar permisos para editar el comentario
        if not (comentario.usuario == request.user or request.user.is_superuser):
            return JsonResponse({'error': 'No tienes permisos para editar este comentario'}, status=403)
        
        data = json.loads(request.body)
        nuevo_comentario = data.get('comentario', '').strip()
        
        if not nuevo_comentario:
            return JsonResponse({'error': 'El comentario no puede estar vacío'}, status=400)
        
        # Actualizar el comentario
        comentario.comentario = nuevo_comentario
        comentario.save()
        
        # Notificar cambio en tiempo real
        notify_solicitud_change(comentario.solicitud, 'comentario_editado', request.user)
        
        return JsonResponse({
            'success': True,
            'comentario': {
                'id': comentario.id,
                'usuario': {
                    'id': comentario.usuario.id,
                    'username': comentario.usuario.username,
                    'nombre_completo': comentario.usuario.get_full_name() or comentario.usuario.username
                },
                'comentario': comentario.comentario,
                'tipo': comentario.tipo,
                'fecha_creacion': comentario.fecha_creacion.isoformat(),
                'fecha_modificacion': comentario.fecha_modificacion.isoformat(),
                'es_editado': comentario.es_editado,
                'tiempo_transcurrido': comentario.get_tiempo_transcurrido(),
                'puede_editar': True,
                'puede_eliminar': True
            },
            'mensaje': 'Comentario actualizado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_eliminar_comentario(request, comentario_id):
    """API para eliminar un comentario"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        comentario = get_object_or_404(SolicitudComentario, id=comentario_id)
        
        # Verificar permisos para eliminar el comentario
        if not (comentario.usuario == request.user or request.user.is_superuser):
            return JsonResponse({'error': 'No tienes permisos para eliminar este comentario'}, status=403)
        
        solicitud = comentario.solicitud
        comentario.delete()
        
        # Notificar cambio en tiempo real
        notify_solicitud_change(solicitud, 'comentario_eliminado', request.user)
        
        return JsonResponse({
            'success': True,
            'mensaje': 'Comentario eliminado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==========================================
# VISTAS DE API PARA SOLICITUDES ACTUALIZADAS
# ==========================================

@login_required
def api_get_updated_solicitudes(request):
    """API para obtener solo las solicitudes que han sido actualizadas"""
    try:
        # Obtener timestamp de la última consulta
        last_check = request.GET.get('last_check')
        if last_check:
            try:
                last_check_time = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
            except:
                last_check_time = timezone.now() - timedelta(minutes=5)
        else:
            last_check_time = timezone.now() - timedelta(minutes=5)
        
        view_type = request.GET.get('view', 'bandejas')
        
        # Obtener solicitudes actualizadas
        solicitudes_base = Solicitud.objects.filter(
            etapa_actual__pipeline__grupos__in=request.user.groups.all(),
            fecha_ultima_actualizacion__gt=last_check_time
        ).select_related('etapa_actual', 'asignada_a', 'pipeline')
        
        # Formatear datos según la vista
        solicitudes_data = []
        
        for solicitud in solicitudes_base:
            # Información de cliente
            cliente_nombre = 'Sin cliente'
            cliente_cedula = 'Sin cédula'
            
            try:
                from pacifico.models import Cotizacion
                cotizacion = Cotizacion.objects.filter(
                    solicitud_workflow=solicitud
                ).first()
                
                if cotizacion:
                    cliente_nombre = cotizacion.cliente or 'Sin cliente'
                    cliente_cedula = cotizacion.cedulaCliente or 'Sin cédula'
            except:
                pass
            
            # Calcular SLA
            sla_info = {
                'color': 'text-secondary',
                'tiempo_restante': 'N/A'
            }
            
            if solicitud.etapa_actual and solicitud.etapa_actual.sla_horas:
                fecha_inicio = solicitud.fecha_creacion
                sla_horas = solicitud.etapa_actual.sla_horas
                fecha_vencimiento = fecha_inicio + timedelta(hours=sla_horas)
                ahora = timezone.now()
                
                segundos_restantes = (fecha_vencimiento - ahora).total_seconds()
                porcentaje_restante = (segundos_restantes / (sla_horas * 3600)) * 100
                abs_segundos = abs(segundos_restantes)
                horas = abs_segundos // 3600
                minutos = (abs_segundos % 3600) // 60
                
                if segundos_restantes < 0:
                    sla_info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    sla_info['color'] = 'text-danger'
                elif porcentaje_restante > 40:
                    sla_info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    sla_info['color'] = 'text-success'
                elif porcentaje_restante > 0:
                    sla_info['tiempo_restante'] = f"{int(horas)}h {int(minutos)}m" if horas > 0 else f"{int(minutos)}m"
                    sla_info['color'] = 'text-warning'
                else:
                    sla_info['tiempo_restante'] = f"-{int(horas)}h {int(minutos)}m" if horas > 0 else f"-{int(minutos)}m"
                    sla_info['color'] = 'text-danger'
            
            solicitudes_data.append({
                'id': solicitud.id,
                'codigo': solicitud.codigo,
                'cliente_nombre': cliente_nombre,
                'cliente_cedula': cliente_cedula,
                'etapa': {
                    'id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
                    'nombre': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
                    'es_bandeja_grupal': solicitud.etapa_actual.es_bandeja_grupal if solicitud.etapa_actual else False
                },
                'asignada_a': {
                    'id': solicitud.asignada_a.id if solicitud.asignada_a else None,
                    'username': solicitud.asignada_a.username if solicitud.asignada_a else None,
                    'nombre_completo': solicitud.asignada_a.get_full_name() if solicitud.asignada_a else None
                },
                'estado_actual': solicitud.subestado_actual.nombre if solicitud.subestado_actual else "En Proceso",
                'sla': sla_info,
                'fecha_actualizacion': solicitud.fecha_ultima_actualizacion.isoformat(),
                'fecha_creacion': solicitud.fecha_creacion.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'solicitudes': solicitudes_data,
            'total': len(solicitudes_data),
            'timestamp': timezone.now().isoformat(),
            'last_check': last_check_time.isoformat(),
            'view': view_type
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        })


@login_required
def api_obtener_requisitos_transicion(request, solicitud_id):
    """API para obtener requisitos faltantes de una transición específica"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        nueva_etapa_id = request.GET.get('nueva_etapa_id')
        
        if not nueva_etapa_id:
            return JsonResponse({'error': 'ID de nueva etapa requerido'}, status=400)
        
        # Verificar permisos (incluye supervisores de grupo)
        if not usuario_puede_modificar_solicitud(request.user, solicitud):
            return JsonResponse({'error': 'No tienes permisos para ver esta solicitud'}, status=403)
        
        nueva_etapa = get_object_or_404(Etapa, id=nueva_etapa_id, pipeline=solicitud.pipeline)
        
        # Buscar transición
        transicion = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual,
            etapa_destino=nueva_etapa
        ).first()
        
        if not transicion:
            return JsonResponse({
                'success': True,
                'requisitos_faltantes': [],
                'mensaje': 'No hay requisitos especiales para esta transición'
            })
        
        # Obtener requisitos faltantes
        requisitos_faltantes = verificar_requisitos_transicion(solicitud, transicion)
        
        return JsonResponse({
            'success': True,
            'requisitos_faltantes': requisitos_faltantes,
            'transicion': {
                'id': transicion.id,
                'nombre': transicion.nombre,
                'etapa_origen': transicion.etapa_origen.nombre,
                'etapa_destino': transicion.etapa_destino.nombre
            },
            'total_faltantes': len(requisitos_faltantes)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_subir_requisito_transicion(request, solicitud_id):
    """API para subir un archivo de requisito faltante"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        requisito_id = request.POST.get('requisito_id')
        
        if not requisito_id:
            return JsonResponse({'error': 'ID de requisito requerido'}, status=400)
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser):
            return JsonResponse({'error': 'No tienes permisos para modificar esta solicitud'}, status=403)
        
        requisito = get_object_or_404(Requisito, id=requisito_id)
        
        # Verificar que hay un archivo
        if 'archivo' not in request.FILES:
            return JsonResponse({'error': 'No se proporcionó ningún archivo'}, status=400)
        
        archivo = request.FILES['archivo']
        
        # Obtener o crear RequisitoSolicitud
        requisito_solicitud, created = RequisitoSolicitud.objects.get_or_create(
            solicitud=solicitud,
            requisito=requisito,
            defaults={
                'cumplido': True,
                'observaciones': f'Archivo subido por {request.user.get_full_name() or request.user.username} el {timezone.now().strftime("%d/%m/%Y %H:%M")}'
            }
        )
        
        # Actualizar archivo y marcar como cumplido
        requisito_solicitud.archivo = archivo
        requisito_solicitud.cumplido = True
        if not created:
            # Actualizar observaciones si ya existía
            observaciones_actuales = requisito_solicitud.observaciones or ''
            requisito_solicitud.observaciones = observaciones_actuales + f'\nActualizado por {request.user.get_full_name() or request.user.username} el {timezone.now().strftime("%d/%m/%Y %H:%M")}'
        
        requisito_solicitud.save()
        
        # Notificar cambio
        notify_solicitud_change(solicitud, 'requisito_actualizado', request.user)
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Archivo para "{requisito.nombre}" subido exitosamente',
            'requisito': {
                'id': requisito.id,
                'nombre': requisito.nombre,
                'archivo_url': requisito_solicitud.archivo.url if requisito_solicitud.archivo else None,
                'cumplido': requisito_solicitud.cumplido
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_validar_requisitos_antes_transicion(request, solicitud_id):
    """API para validar requisitos antes de realizar una transición"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        nueva_etapa_id = request.GET.get('nueva_etapa_id')
        
        if not nueva_etapa_id:
            return JsonResponse({'error': 'ID de nueva etapa requerido'}, status=400)
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser):
            return JsonResponse({'error': 'No tienes permisos para ver esta solicitud'}, status=403)
        
        nueva_etapa = get_object_or_404(Etapa, id=nueva_etapa_id, pipeline=solicitud.pipeline)
        
        # Buscar transición
        transicion = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual,
            etapa_destino=nueva_etapa
        ).first()
        
        if not transicion:
            return JsonResponse({
                'success': True,
                'puede_continuar': True,
                'mensaje': 'No hay requisitos especiales para esta transición'
            })
        
        # Verificar requisitos
        requisitos_faltantes = verificar_requisitos_transicion(solicitud, transicion)
        
        return JsonResponse({
            'success': True,
            'puede_continuar': len(requisitos_faltantes) == 0,
            'requisitos_faltantes': requisitos_faltantes,
            'total_faltantes': len(requisitos_faltantes),
            'mensaje': 'Todos los requisitos están completos' if len(requisitos_faltantes) == 0 else f'Faltan {len(requisitos_faltantes)} requisito(s)'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_obtener_transiciones_validas(request, solicitud_id):
    """API para obtener las transiciones válidas para una solicitud"""
    print(f"🔍 DEBUG: api_obtener_transiciones_validas llamado con solicitud_id={solicitud_id}")
    print(f"🔍 DEBUG: Usuario actual: {request.user.username}")
    print(f"🔍 DEBUG: Es superuser: {request.user.is_superuser}")
    print(f"🔍 DEBUG: Es staff: {request.user.is_staff}")
    
    try:
        # Verificar que el ID sea válido
        if not solicitud_id or not str(solicitud_id).isdigit():
            print(f"❌ ERROR: ID de solicitud inválido: {solicitud_id}")
            return JsonResponse({
                'success': False, 
                'error': 'ID de solicitud inválido'
            }, status=400)
        
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        print(f"✅ DEBUG: Solicitud encontrada: {solicitud.codigo}")
        
        # Verificar permisos (incluye supervisores de grupo)
        if not usuario_puede_modificar_solicitud(request.user, solicitud):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para ver esta solicitud'
            }, status=403)
        
        # Obtener transiciones válidas desde la etapa actual
        transiciones_validas = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual
        ).select_related('etapa_destino')
        
        transiciones_data = []
        for transicion in transiciones_validas:
            try:
                # Verificar requisitos para esta transición
                requisitos_faltantes = verificar_requisitos_transicion(solicitud, transicion)
                
                transiciones_data.append({
                    'id': transicion.id,
                    'nombre': transicion.nombre,
                    'etapa_destino': {
                        'id': transicion.etapa_destino.id,
                        'nombre': transicion.etapa_destino.nombre,
                        'orden': transicion.etapa_destino.orden
                    },
                    'requiere_permiso': transicion.requiere_permiso,
                    'puede_realizar': len(requisitos_faltantes) == 0,
                    'requisitos_faltantes': requisitos_faltantes,
                    'total_requisitos_faltantes': len(requisitos_faltantes)
                })
            except Exception as transicion_error:
                # Si hay error en una transición específica, continuar con las demás
                print(f"Error procesando transición {transicion.id}: {transicion_error}")
                continue
        
        return JsonResponse({
            'success': True,
            'transiciones': transiciones_data,
            'etapa_actual': {
                'id': solicitud.etapa_actual.id if solicitud.etapa_actual else None,
                'nombre': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
                'orden': solicitud.etapa_actual.orden if solicitud.etapa_actual else None
            },
            'total_transiciones': len(transiciones_data)
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'La solicitud no existe'
        }, status=404)
    except Exception as e:
        print(f"Error en api_obtener_transiciones_validas: {str(e)}")
        return JsonResponse({
            'success': False, 
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)


@login_required
def api_obtener_etapa_con_subestados(request, etapa_id):
    """API para obtener información de una etapa específica con sus subestados"""
    try:
        etapa = get_object_or_404(Etapa, id=etapa_id)
        
        # Obtener subestados de la etapa
        subestados = etapa.subestados.all().order_by('orden')
        
        subestados_data = []
        for subestado in subestados:
            subestados_data.append({
                'id': subestado.id,
                'nombre': subestado.nombre,
                'orden': subestado.orden
            })
        
        return JsonResponse({
            'success': True,
            'etapa': {
                'id': etapa.id,
                'nombre': etapa.nombre,
                'orden': etapa.orden,
                'es_bandeja_grupal': etapa.es_bandeja_grupal,
                'tiene_subestados': len(subestados_data) > 0
            },
            'subestados': subestados_data
        })
        
    except Etapa.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'La etapa no existe'
        }, status=404)
    except Exception as e:
        print(f"Error en api_obtener_etapa_con_subestados: {str(e)}")
        return JsonResponse({
            'success': False, 
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)


# ==========================================
# VISTAS DE API PARA REQUISITOS DE TRANSICIÓN
# ==========================================

@login_required
@superuser_permission_required('workflow.add_requisitotransicion')
def api_obtener_requisitos_transicion_pipeline(request, pipeline_id):
    """API para obtener todos los requisitos de transición de un pipeline"""
    try:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        
        # Obtener todas las transiciones del pipeline
        transiciones = TransicionEtapa.objects.filter(pipeline=pipeline).select_related(
            'etapa_origen', 'etapa_destino'
        )
        
        # Obtener requisitos de transición
        requisitos_transicion = RequisitoTransicion.objects.filter(
            transicion__pipeline=pipeline
        ).select_related('transicion', 'requisito', 'transicion__etapa_origen', 'transicion__etapa_destino')
        
        # Formatear datos para el frontend
        datos_transiciones = []
        for transicion in transiciones:
            requisitos_de_transicion = [
                {
                    'id': rt.id,
                    'requisito_id': rt.requisito.id,
                    'requisito_nombre': rt.requisito.nombre,
                    'obligatorio': rt.obligatorio,
                    'mensaje_personalizado': rt.mensaje_personalizado or ''
                }
                for rt in requisitos_transicion if rt.transicion_id == transicion.id
            ]
            
            datos_transiciones.append({
                'id': transicion.id,
                'nombre': transicion.nombre,
                'etapa_origen': {
                    'id': transicion.etapa_origen.id,
                    'nombre': transicion.etapa_origen.nombre
                },
                'etapa_destino': {
                    'id': transicion.etapa_destino.id,
                    'nombre': transicion.etapa_destino.nombre
                },
                'requisitos': requisitos_de_transicion
            })
        
        # Obtener solo los requisitos asignados a este pipeline
        requisitos_disponibles = Requisito.objects.filter(
            requisitopipeline__pipeline=pipeline
        ).values('id', 'nombre', 'descripcion').distinct()
        
        return JsonResponse({
            'success': True,
            'transiciones': datos_transiciones,
            'requisitos_disponibles': list(requisitos_disponibles)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@superuser_permission_required('workflow.add_requisitotransicion')
def api_crear_requisito_transicion(request):
    """API para crear un requisito de transición"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        # Debug logging
        print(f"Request body: {request.body}")
        print(f"Content-Type: {request.content_type}")
        
        data = json.loads(request.body)
        print(f"Parsed data: {data}")
        
        transicion_id = data.get('transicion_id')
        requisito_id = data.get('requisito_id')
        obligatorio = data.get('obligatorio', True)
        mensaje_personalizado = data.get('mensaje_personalizado', '')
        
        print(f"transicion_id: {transicion_id} (type: {type(transicion_id)})")
        print(f"requisito_id: {requisito_id} (type: {type(requisito_id)})")
        print(f"obligatorio: {obligatorio} (type: {type(obligatorio)})")
        print(f"mensaje_personalizado: {mensaje_personalizado}")
        
        if not all([transicion_id, requisito_id]):
            return JsonResponse({'error': 'Transición y requisito son obligatorios'}, status=400)
        
        transicion = get_object_or_404(TransicionEtapa, id=transicion_id)
        requisito = get_object_or_404(Requisito, id=requisito_id)
        
        # Verificar que no existe ya esta combinación
        if RequisitoTransicion.objects.filter(transicion=transicion, requisito=requisito).exists():
            return JsonResponse({'error': 'Este requisito ya está asignado a esta transición'}, status=400)
        
        # Crear el requisito de transición
        requisito_transicion = RequisitoTransicion.objects.create(
            transicion=transicion,
            requisito=requisito,
            obligatorio=obligatorio,
            mensaje_personalizado=mensaje_personalizado
        )
        
        return JsonResponse({
            'success': True,
            'requisito_transicion': {
                'id': requisito_transicion.id,
                'transicion_id': transicion.id,
                'transicion_nombre': transicion.nombre,
                'requisito_id': requisito.id,
                'requisito_nombre': requisito.nombre,
                'obligatorio': requisito_transicion.obligatorio,
                'mensaje_personalizado': requisito_transicion.mensaje_personalizado
            },
            'mensaje': f'Requisito "{requisito.nombre}" asignado a la transición "{transicion.nombre}"'
        })
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        print(f"Exception: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@superuser_permission_required('workflow.change_requisitotransicion')
def api_actualizar_requisito_transicion(request, requisito_transicion_id):
    """API para actualizar un requisito de transición"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        requisito_transicion = get_object_or_404(RequisitoTransicion, id=requisito_transicion_id)
        
        data = json.loads(request.body)
        obligatorio = data.get('obligatorio', requisito_transicion.obligatorio)
        mensaje_personalizado = data.get('mensaje_personalizado', requisito_transicion.mensaje_personalizado)
        
        # Actualizar campos
        requisito_transicion.obligatorio = obligatorio
        requisito_transicion.mensaje_personalizado = mensaje_personalizado
        requisito_transicion.save()
        
        return JsonResponse({
            'success': True,
            'requisito_transicion': {
                'id': requisito_transicion.id,
                'obligatorio': requisito_transicion.obligatorio,
                'mensaje_personalizado': requisito_transicion.mensaje_personalizado
            },
            'mensaje': 'Requisito de transición actualizado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@superuser_permission_required('workflow.delete_requisitotransicion')
def api_eliminar_requisito_transicion(request, requisito_transicion_id):
    """API para eliminar un requisito de transición"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        requisito_transicion = get_object_or_404(RequisitoTransicion, id=requisito_transicion_id)
        
        transicion_nombre = requisito_transicion.transicion.nombre
        requisito_nombre = requisito_transicion.requisito.nombre
        
        requisito_transicion.delete()
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Requisito "{requisito_nombre}" removido de la transición "{transicion_nombre}"'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_obtener_requisitos_faltantes_detallado(request, solicitud_id):
    """API para obtener requisitos faltantes con detalles completos para el modal"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        nueva_etapa_id = request.GET.get('nueva_etapa_id')
        
        if not nueva_etapa_id:
            return JsonResponse({'error': 'ID de nueva etapa requerido'}, status=400)
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser or
                request.user.is_staff):
            return JsonResponse({'error': 'No tienes permisos para ver esta solicitud'}, status=403)
        
        nueva_etapa = get_object_or_404(Etapa, id=nueva_etapa_id, pipeline=solicitud.pipeline)
        
        # Buscar transición
        transicion = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual,
            etapa_destino=nueva_etapa
        ).first()
        
        if not transicion:
            return JsonResponse({
                'success': False,
                'error': 'No existe una transición válida hacia esta etapa'
            }, status=400)
        
        # Obtener TODOS los requisitos para esta transición (obligatorios y opcionales)
        requisitos_transicion = RequisitoTransicion.objects.filter(
            transicion=transicion
        ).select_related('requisito')
        
        requisitos_detallados = []
        requisitos_obligatorios = []
        requisitos_opcionales = []
        total_requisitos = 0
        requisitos_completos = 0
        requisitos_obligatorios_completos = 0
        
        for req_transicion in requisitos_transicion:
            total_requisitos += 1
            
            # Verificar si el requisito existe para esta solicitud
            requisito_solicitud = RequisitoSolicitud.objects.filter(
                solicitud=solicitud,
                requisito=req_transicion.requisito
            ).first()
            
            # Lógica especial para requisito de agenda de firma
            if req_transicion.requisito.tipo_especial == 'agenda_firma':
                # Para agenda de firma, verificar si existe una cita agendada
                from workflow.modelsWorkflow import AgendaFirma
                tiene_cita_agendada = AgendaFirma.objects.filter(solicitud=solicitud).exists()
                esta_completo = tiene_cita_agendada
            else:
                # Determinar si está completo - considerar archivos subidos desde drawer
                # Un requisito está completo si:
                # 1. Existe el RequisitoSolicitud Y 
                # 2. (Tiene archivo O está marcado como cumplido)
                esta_completo = bool(requisito_solicitud and (requisito_solicitud.archivo or requisito_solicitud.cumplido))
            if esta_completo:
                requisitos_completos += 1
                if req_transicion.obligatorio:
                    requisitos_obligatorios_completos += 1
            
            # Incluir TODOS los requisitos, no solo los faltantes
            requisito_data = {
                'id': req_transicion.requisito.id,
                'nombre': req_transicion.requisito.nombre,
                'descripcion': req_transicion.requisito.descripcion,
                'mensaje_personalizado': req_transicion.mensaje_personalizado,
                'obligatorio': req_transicion.obligatorio,
                'tiene_archivo': bool(requisito_solicitud and requisito_solicitud.archivo),
                'esta_cumplido': esta_completo,
                'requisito_solicitud_id': requisito_solicitud.id if requisito_solicitud else None,
                'archivo_actual': {
                    'nombre': requisito_solicitud.archivo.name.split('/')[-1] if requisito_solicitud and requisito_solicitud.archivo else None,
                    'url': requisito_solicitud.archivo.url if requisito_solicitud and requisito_solicitud.archivo else None
                } if requisito_solicitud and requisito_solicitud.archivo else None,
                'observaciones': requisito_solicitud.observaciones if requisito_solicitud else '',
                'tipo_especial': req_transicion.requisito.tipo_especial
            }
            
            # Agregar información específica para agenda de firma
            if req_transicion.requisito.tipo_especial == 'agenda_firma':
                from workflow.modelsWorkflow import AgendaFirma
                cita_firma = AgendaFirma.objects.filter(solicitud=solicitud).first()
                requisito_data['agenda_firma'] = {
                    'tiene_cita': bool(cita_firma),
                    'fecha_hora': cita_firma.fecha_hora.isoformat() if cita_firma else None,
                    'fecha_formateada': cita_firma.fecha_formateada if cita_firma else None,
                    'lugar_firma': cita_firma.lugar_firma if cita_firma else None,
                    'lugar_firma_display': cita_firma.lugar_firma_display if cita_firma else None,
                    'comentarios': cita_firma.comentarios if cita_firma else None,
                    'cita_id': cita_firma.id if cita_firma else None
                }
            
            requisitos_detallados.append(requisito_data)
            
            # Separar en obligatorios y opcionales
            if req_transicion.obligatorio:
                requisitos_obligatorios.append(requisito_data)
            else:
                requisitos_opcionales.append(requisito_data)
        
        # Calculate mandatory requirements count
        total_requisitos_obligatorios = len(requisitos_obligatorios)
        requisitos_obligatorios_faltantes = [req for req in requisitos_obligatorios if not req['esta_cumplido']]
        total_obligatorios_faltantes = len(requisitos_obligatorios_faltantes)
        
        return JsonResponse({
            'success': True,
            'transicion': {
                'id': transicion.id,
                'nombre': transicion.nombre,
                'etapa_origen': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
                'etapa_destino': nueva_etapa.nombre
            },
            'requisitos': requisitos_detallados,
            'requisitos_obligatorios': requisitos_obligatorios,
            'requisitos_opcionales': requisitos_opcionales,
            'total_requisitos': total_requisitos,
            'total_requisitos_obligatorios': total_requisitos_obligatorios,
            'total_requisitos_opcionales': len(requisitos_opcionales),
            'requisitos_completos': requisitos_completos,
            'requisitos_obligatorios_completos': requisitos_obligatorios_completos,
            'requisitos_faltantes': [req for req in requisitos_detallados if not req['esta_cumplido']],
            'requisitos_obligatorios_faltantes': requisitos_obligatorios_faltantes,
            'total_faltantes': total_requisitos - requisitos_completos,
            'total_obligatorios_faltantes': total_obligatorios_faltantes,
            'puede_continuar_sin_requisitos': request.user.is_superuser or request.user.is_staff
        })
        
    except Exception as e:
        print(f"Error en api_obtener_requisitos_faltantes_detallado: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def api_subir_requisito_modal(request, solicitud_id):
    """API para subir un requisito desde el modal de requisitos faltantes"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser or
                request.user.is_staff):
            return JsonResponse({'error': 'No tienes permisos para modificar esta solicitud'}, status=403)
        
        requisito_id = request.POST.get('requisito_id')
        archivo = request.FILES.get('archivo')
        
        if not requisito_id:
            return JsonResponse({'error': 'ID de requisito requerido'}, status=400)
        
        if not archivo:
            return JsonResponse({'error': 'Archivo requerido'}, status=400)
        
        requisito = get_object_or_404(Requisito, id=requisito_id)
        
        # Crear o actualizar el requisito de solicitud
        requisito_solicitud, created = RequisitoSolicitud.objects.get_or_create(
            solicitud=solicitud,
            requisito=requisito,
            defaults={
                'archivo': archivo,
                'cumplido': True,
                'observaciones': ''  # Campo vacío por defecto
            }
        )
        
        if not created:
            # Actualizar existente
            requisito_solicitud.archivo = archivo
            requisito_solicitud.cumplido = True
            requisito_solicitud.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Requisito "{requisito.nombre}" subido exitosamente',
            'requisito': {
                'id': requisito.id,
                'nombre': requisito.nombre,
                'archivo_nombre': archivo.name,
                'cumplido': True
            }
        })
        
    except Exception as e:
        print(f"Error en api_subir_requisito_modal: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def debug_session(request):
    """Debug view to check session status"""
    session_info = {
        'user': request.user.username,
        'session_key': request.session.session_key,
        'session_expiry': request.session.get_expiry_date(),
        'session_age': request.session.get_expiry_age(),
        'session_modified': request.session.modified,
        'session_accessed': request.session.accessed,
        'is_authenticated': request.user.is_authenticated,
        'user_id': request.user.id,
        'session_data': dict(request.session.items()),
    }
    
    return JsonResponse({
        'success': True,
        'session_info': session_info,
        'timestamp': timezone.now().isoformat()
    })


@login_required
def detalle_solicitud_v2(request, solicitud_id):
    """Detalle de una solicitud específica (V2 UI)"""
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar permisos (igual que en detalle_solicitud)
    if solicitud.asignada_a and solicitud.asignada_a != request.user:
        if not (request.user.is_superuser or request.user.is_staff):
            grupos_usuario = request.user.groups.all()
            tiene_permiso = PermisoEtapa.objects.filter(
                etapa=solicitud.etapa_actual,
                grupo__in=grupos_usuario,
                puede_ver=True
            ).exists()
            if not tiene_permiso:
                messages.error(request, 'No tienes permisos para ver esta solicitud.')
                return redirect('workflow:bandeja_trabajo')
    
    # Obtener datos adicionales para el contexto
    context = {
        'solicitud': solicitud,
        'solicitud_id': solicitud.id,
        'pipeline': solicitud.pipeline,
        'etapa_actual': solicitud.etapa_actual,
        'cliente': solicitud.cliente if hasattr(solicitud, 'cliente') else None,
        'cotizacion': solicitud.cotizacion if hasattr(solicitud, 'cotizacion') else None,
        'timestamp': timezone.now().timestamp(),  # Force cache refresh
    }
    
    return render(request, 'workflow/detalleSolicitud_V2.html', context)


# ==========================================
# APIs PARA GESTIÓN DE PERMISOS DE PIPELINE
# ==========================================

@login_required
@permission_required('workflow.add_permisopipeline')
def api_obtener_permisos_pipeline(request, pipeline_id):
    """API para obtener permisos de un pipeline"""
    try:
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        permisos = PermisoPipeline.objects.filter(pipeline=pipeline).select_related('grupo', 'usuario')
        
        permisos_data = []
        for permiso in permisos:
            permisos_data.append({
                'id': permiso.id,
                'grupo': {
                    'id': permiso.grupo.id,
                    'name': permiso.grupo.name
                } if permiso.grupo else None,
                'usuario': {
                    'id': permiso.usuario.id,
                    'username': permiso.usuario.username,
                    'first_name': permiso.usuario.first_name,
                    'last_name': permiso.usuario.last_name
                } if permiso.usuario else None,
                'puede_ver': permiso.puede_ver,
                'puede_crear': permiso.puede_crear,
                'puede_editar': permiso.puede_editar,
                'puede_eliminar': permiso.puede_eliminar,
                'puede_admin': permiso.puede_admin
            })
        
        return JsonResponse({
            'success': True,
            'permisos': permisos_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@permission_required('workflow.add_permisopipeline')
def api_crear_permiso_pipeline(request, pipeline_id):
    """API para crear un permiso de pipeline"""
    if request.method == 'POST':
        try:
            pipeline = get_object_or_404(Pipeline, id=pipeline_id)
            data = json.loads(request.body)
            
            grupo_id = data.get('grupo_id')
            usuario_id = data.get('usuario_id')
            
            if not grupo_id and not usuario_id:
                return JsonResponse({'success': False, 'error': 'Debe especificar un grupo o un usuario'})
            
            if grupo_id and usuario_id:
                return JsonResponse({'success': False, 'error': 'No puede especificar tanto un grupo como un usuario'})
            
            # Verificar si ya existe el permiso
            if grupo_id:
                grupo = get_object_or_404(Group, id=grupo_id)
                permiso, created = PermisoPipeline.objects.get_or_create(
                    pipeline=pipeline,
                    grupo=grupo,
                    defaults={
                        'puede_ver': data.get('puede_ver', True),
                        'puede_crear': data.get('puede_crear', False),
                        'puede_editar': data.get('puede_editar', False),
                        'puede_eliminar': data.get('puede_eliminar', False),
                        'puede_admin': data.get('puede_admin', False)
                    }
                )
                if not created:
                    # Actualizar permisos existentes
                    permiso.puede_ver = data.get('puede_ver', True)
                    permiso.puede_crear = data.get('puede_crear', False)
                    permiso.puede_editar = data.get('puede_editar', False)
                    permiso.puede_eliminar = data.get('puede_eliminar', False)
                    permiso.puede_admin = data.get('puede_admin', False)
                    permiso.save()
            else:
                usuario = get_object_or_404(User, id=usuario_id)
                permiso, created = PermisoPipeline.objects.get_or_create(
                    pipeline=pipeline,
                    usuario=usuario,
                    defaults={
                        'puede_ver': data.get('puede_ver', True),
                        'puede_crear': data.get('puede_crear', False),
                        'puede_editar': data.get('puede_editar', False),
                        'puede_eliminar': data.get('puede_eliminar', False),
                        'puede_admin': data.get('puede_admin', False)
                    }
                )
                if not created:
                    # Actualizar permisos existentes
                    permiso.puede_ver = data.get('puede_ver', True)
                    permiso.puede_crear = data.get('puede_crear', False)
                    permiso.puede_editar = data.get('puede_editar', False)
                    permiso.puede_eliminar = data.get('puede_eliminar', False)
                    permiso.puede_admin = data.get('puede_admin', False)
                    permiso.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso creado/actualizado exitosamente',
                'permiso': {
                    'id': permiso.id,
                    'grupo': {
                        'id': permiso.grupo.id,
                        'name': permiso.grupo.name
                    } if permiso.grupo else None,
                    'usuario': {
                        'id': permiso.usuario.id,
                        'username': permiso.usuario.username,
                        'first_name': permiso.usuario.first_name,
                        'last_name': permiso.usuario.last_name
                    } if permiso.usuario else None,
                    'puede_ver': permiso.puede_ver,
                    'puede_crear': permiso.puede_crear,
                    'puede_editar': permiso.puede_editar,
                    'puede_eliminar': permiso.puede_eliminar,
                    'puede_admin': permiso.puede_admin
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.change_permisopipeline')
def api_actualizar_permiso_pipeline(request, pipeline_id, permiso_id):
    """API para actualizar un permiso de pipeline"""
    if request.method == 'POST':
        try:
            permiso = get_object_or_404(PermisoPipeline, id=permiso_id, pipeline_id=pipeline_id)
            data = json.loads(request.body)
            
            permiso.puede_ver = data.get('puede_ver', True)
            permiso.puede_crear = data.get('puede_crear', False)
            permiso.puede_editar = data.get('puede_editar', False)
            permiso.puede_eliminar = data.get('puede_eliminar', False)
            permiso.puede_admin = data.get('puede_admin', False)
            permiso.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso actualizado exitosamente'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.delete_permisopipeline')
def api_eliminar_permiso_pipeline(request, pipeline_id, permiso_id):
    """API para eliminar un permiso de pipeline"""
    if request.method == 'POST':
        try:
            permiso = get_object_or_404(PermisoPipeline, id=permiso_id, pipeline_id=pipeline_id)
            permiso.delete()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso eliminado exitosamente'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# ==========================================
# APIs PARA GESTIÓN DE PERMISOS DE BANDEJA
# ==========================================

@login_required
@permission_required('workflow.add_permisobandeja')
def api_obtener_permisos_bandeja(request, etapa_id):
    """API para obtener permisos de una bandeja (etapa)"""
    try:
        etapa = get_object_or_404(Etapa, id=etapa_id)
        permisos = PermisoBandeja.objects.filter(etapa=etapa).select_related('grupo', 'usuario')
        
        permisos_data = []
        for permiso in permisos:
            permisos_data.append({
                'id': permiso.id,
                'grupo': {
                    'id': permiso.grupo.id,
                    'name': permiso.grupo.name
                } if permiso.grupo else None,
                'usuario': {
                    'id': permiso.usuario.id,
                    'username': permiso.usuario.username,
                    'first_name': permiso.usuario.first_name,
                    'last_name': permiso.usuario.last_name
                } if permiso.usuario else None,
                'puede_ver': permiso.puede_ver,
                'puede_tomar': permiso.puede_tomar,
                'puede_devolver': permiso.puede_devolver,
                'puede_transicionar': permiso.puede_transicionar,
                'puede_editar': permiso.puede_editar
            })
        
        return JsonResponse({
            'success': True,
            'permisos': permisos_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@permission_required('workflow.add_permisobandeja')
def api_crear_permiso_bandeja(request, etapa_id):
    """API para crear un permiso de bandeja"""
    if request.method == 'POST':
        try:
            # Debug logging
            print(f"Creating bandeja permission for etapa_id: {etapa_id}")
            print(f"Request body: {request.body}")
            print(f"Content-Type: {request.content_type}")
            
            etapa = get_object_or_404(Etapa, id=etapa_id)
            data = json.loads(request.body)
            
            print(f"Parsed data: {data}")
            
            grupo_id = data.get('grupo_id')
            usuario_id = data.get('usuario_id')
            
            print(f"grupo_id: {grupo_id}")
            print(f"usuario_id: {usuario_id}")
            
            if not grupo_id and not usuario_id:
                return JsonResponse({'success': False, 'error': 'Debe especificar un grupo o un usuario'})
            
            if grupo_id and usuario_id:
                return JsonResponse({'success': False, 'error': 'No puede especificar tanto un grupo como un usuario'})
            
            # Verificar si ya existe el permiso
            if grupo_id:
                grupo = get_object_or_404(Group, id=grupo_id)
                permiso, created = PermisoBandeja.objects.get_or_create(
                    etapa=etapa,
                    grupo=grupo,
                    defaults={
                        'puede_ver': data.get('puede_ver', True),
                        'puede_tomar': data.get('puede_tomar', True),
                        'puede_devolver': data.get('puede_devolver', True),
                        'puede_transicionar': data.get('puede_transicionar', True),
                        'puede_editar': data.get('puede_editar', False)
                    }
                )
                if not created:
                    # Actualizar permisos existentes
                    permiso.puede_ver = data.get('puede_ver', True)
                    permiso.puede_tomar = data.get('puede_tomar', True)
                    permiso.puede_devolver = data.get('puede_devolver', True)
                    permiso.puede_transicionar = data.get('puede_transicionar', True)
                    permiso.puede_editar = data.get('puede_editar', False)
                    permiso.save()
            else:
                usuario = get_object_or_404(User, id=usuario_id)
                permiso, created = PermisoBandeja.objects.get_or_create(
                    etapa=etapa,
                    usuario=usuario,
                    defaults={
                        'puede_ver': data.get('puede_ver', True),
                        'puede_tomar': data.get('puede_tomar', True),
                        'puede_devolver': data.get('puede_devolver', True),
                        'puede_transicionar': data.get('puede_transicionar', True),
                        'puede_editar': data.get('puede_editar', False)
                    }
                )
                if not created:
                    # Actualizar permisos existentes
                    permiso.puede_ver = data.get('puede_ver', True)
                    permiso.puede_tomar = data.get('puede_tomar', True)
                    permiso.puede_devolver = data.get('puede_devolver', True)
                    permiso.puede_transicionar = data.get('puede_transicionar', True)
                    permiso.puede_editar = data.get('puede_editar', False)
                    permiso.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso creado/actualizado exitosamente',
                'permiso': {
                    'id': permiso.id,
                    'grupo': {
                        'id': permiso.grupo.id,
                        'name': permiso.grupo.name
                    } if permiso.grupo else None,
                    'usuario': {
                        'id': permiso.usuario.id,
                        'username': permiso.usuario.username,
                        'first_name': permiso.usuario.first_name,
                        'last_name': permiso.usuario.last_name
                    } if permiso.usuario else None,
                    'puede_ver': permiso.puede_ver,
                    'puede_tomar': permiso.puede_tomar,
                    'puede_devolver': permiso.puede_devolver,
                    'puede_transicionar': permiso.puede_transicionar,
                    'puede_editar': permiso.puede_editar
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.change_permisobandeja')
def api_actualizar_permiso_bandeja(request, etapa_id, permiso_id):
    """API para actualizar un permiso de bandeja"""
    if request.method == 'POST':
        try:
            permiso = get_object_or_404(PermisoBandeja, id=permiso_id, etapa_id=etapa_id)
            data = json.loads(request.body)
            
            permiso.puede_ver = data.get('puede_ver', True)
            permiso.puede_tomar = data.get('puede_tomar', True)
            permiso.puede_devolver = data.get('puede_devolver', True)
            permiso.puede_transicionar = data.get('puede_transicionar', True)
            permiso.puede_editar = data.get('puede_editar', False)
            permiso.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso actualizado exitosamente'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
@permission_required('workflow.delete_permisobandeja')
def api_eliminar_permiso_bandeja(request, etapa_id, permiso_id):
    """API para eliminar un permiso de bandeja"""
    if request.method == 'POST':
        try:
            permiso = get_object_or_404(PermisoBandeja, id=permiso_id, etapa_id=etapa_id)
            permiso.delete()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Permiso eliminado exitosamente'
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


# ==========================================
# APIs PARA OBTENER USUARIOS Y GRUPOS
# ==========================================

@login_required
def api_obtener_usuarios(request):
    """API para obtener lista de usuarios activos"""
    try:
        usuarios = User.objects.filter(is_active=True).order_by('username')
        usuarios_data = []
        
        for usuario in usuarios:
            usuarios_data.append({
                'id': usuario.id,
                'username': usuario.username,
                'first_name': usuario.first_name,
                'last_name': usuario.last_name,
                'email': usuario.email,
                'full_name': f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username
            })
        
        return JsonResponse({
            'success': True,
            'usuarios': usuarios_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_obtener_grupos(request):
    """API para obtener lista de grupos"""
    try:
        grupos = Group.objects.all().order_by('name')
        grupos_data = []
        
        for grupo in grupos:
            grupos_data.append({
                'id': grupo.id,
                'name': grupo.name,
                'user_count': grupo.user_set.count()
            })
        
        return JsonResponse({
            'success': True,
            'grupos': grupos_data
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ==========================================
# FUNCIONES PARA REQUISITOS DE TRANSICIÓN
# ==========================================

# ==========================================
# VISTA DE ANÁLISIS PARA ANALISTAS
# ==========================================

@login_required
def detalle_solicitud_analisis(request, solicitud_id):
    """Vista especializada para análisis de solicitudes por parte de analistas"""
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar permisos - Permitir acceso si no está asignada o si el usuario tiene permisos
    if solicitud.asignada_a and solicitud.asignada_a != request.user:
        if not (request.user.is_superuser or request.user.is_staff):
            grupos_usuario = request.user.groups.all()
            tiene_permiso = PermisoEtapa.objects.filter(
                etapa=solicitud.etapa_actual,
                grupo__in=grupos_usuario,
                puede_ver=True
            ).exists()
            if not tiene_permiso:
                messages.error(request, 'No tienes permisos para ver esta solicitud asignada a otro usuario.')
                return redirect('workflow:vista_mixta_bandejas')
    
    cliente = solicitud.cliente if hasattr(solicitud, 'cliente') else None
    cotizacion = solicitud.cotizacion if hasattr(solicitud, 'cotizacion') else None
    historial = solicitud.historial.all().order_by('-fecha_inicio')
    
    # Get requisitos específicos para la transición hacia "Consulta"
    # Buscar la etapa "Consulta" 
    etapa_consulta = solicitud.pipeline.etapas.filter(nombre__icontains='Consulta').first()
    requisitos_consulta = []
    requisitos_consulta_info = []  # Información detallada de requisitos con obligatorio/opcional
    
    if etapa_consulta:
        # Buscar transiciones que van hacia "Consulta"
        transiciones_a_consulta = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_destino=etapa_consulta
        )
        
        # Obtener RequisitoTransicion con información de obligatorio/opcional
        requisitos_transicion = RequisitoTransicion.objects.filter(
            transicion__in=transiciones_a_consulta
        ).select_related('requisito', 'transicion')
        
        # Crear diccionario de requisitos con su estado obligatorio/opcional
        requisitos_info_map = {}
        for req_trans in requisitos_transicion:
            requisitos_info_map[req_trans.requisito.id] = {
                'obligatorio': req_trans.obligatorio,
                'mensaje_personalizado': req_trans.mensaje_personalizado,
                'transicion_nombre': req_trans.transicion.nombre
            }
        
        # Obtener requisitos de la solicitud que están configurados para transiciones a Consulta
        requisitos_ids = list(requisitos_info_map.keys())
        requisitos_consulta = solicitud.requisitos.filter(
            requisito_id__in=requisitos_ids
        ).select_related('requisito')
        
        # Agregar información de obligatorio/opcional a cada requisito
        for req_sol in requisitos_consulta:
            if req_sol.requisito.id in requisitos_info_map:
                req_sol.es_obligatorio = requisitos_info_map[req_sol.requisito.id]['obligatorio']
                req_sol.mensaje_personalizado = requisitos_info_map[req_sol.requisito.id]['mensaje_personalizado']
                req_sol.transicion_nombre = requisitos_info_map[req_sol.requisito.id]['transicion_nombre']
    
    # Mantener requisitos originales para compatibilidad, pero agregar requisitos_consulta
    requisitos = solicitud.requisitos.all().select_related('requisito')
    comentarios = solicitud.comentarios.all().order_by('-fecha_creacion')
    etapas_pipeline = solicitud.pipeline.etapas.all().order_by('orden')
    
    # Solicitudes relacionadas (por cédula del cliente, excluyendo la actual)
    solicitudes_relacionadas = []
    mostrar_mensaje_sin_cliente = False
    cedula_cliente = None
    
    # Obtener cédula desde cliente o cotización
    if solicitud.cliente and solicitud.cliente.cedulaCliente:
        cedula_cliente = solicitud.cliente.cedulaCliente
    elif solicitud.cotizacion and solicitud.cotizacion.cedulaCliente:
        cedula_cliente = solicitud.cotizacion.cedulaCliente
    
    if cedula_cliente:
        # Buscar todas las solicitudes con la misma cédula (en cliente o cotización)
        solicitudes_relacionadas = Solicitud.objects.filter(
            (models.Q(cliente__cedulaCliente=cedula_cliente) | 
             models.Q(cotizacion__cedulaCliente=cedula_cliente))
        ).exclude(id=solicitud.id).select_related('cotizacion', 'cliente').order_by('-fecha_creacion')
    else:
        mostrar_mensaje_sin_cliente = True
    
    # Calcular información de progreso
    total_etapas = etapas_pipeline.count()
    if total_etapas > 0:
        etapa_actual_orden = solicitud.etapa_actual.orden if solicitud.etapa_actual else 0
        progreso_porcentaje = (etapa_actual_orden / total_etapas) * 100
    else:
        progreso_porcentaje = 0
    
    sla_info = calcular_sla_detallado(solicitud)
    
    # Obtener transiciones disponibles
    transiciones_disponibles = []
    if solicitud.etapa_actual:
        transiciones = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual
        )
        
        for transicion in transiciones:
            # Verificar requisitos para esta transición
            requisitos_faltantes = verificar_requisitos_transicion(solicitud, transicion)
            
            if not transicion.requiere_permiso:
                transiciones_disponibles.append({
                    'transicion': transicion,
                    'puede_realizar': len(requisitos_faltantes) == 0,
                    'requisitos_faltantes': requisitos_faltantes,
                    'total_requisitos_faltantes': len(requisitos_faltantes)
                })
            else:
                # Verificar si el usuario tiene permisos específicos
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=transicion.etapa_destino,
                    grupo__in=grupos_usuario
                ).exists()
                if tiene_permiso:
                    transiciones_disponibles.append({
                        'transicion': transicion,
                        'puede_realizar': len(requisitos_faltantes) == 0,
                        'requisitos_faltantes': requisitos_faltantes,
                        'total_requisitos_faltantes': len(requisitos_faltantes)
                    })
    
    context = {
        'solicitud': solicitud,
        'cliente': cliente,
        'cotizacion': cotizacion,
        'historial': historial,
        'requisitos': requisitos,
        'requisitos_consulta': requisitos_consulta,  # Requisitos específicos para transición a Consulta
        'comentarios': comentarios,
        'etapas_pipeline': etapas_pipeline,
        'transiciones_disponibles': transiciones_disponibles,
        'progreso_porcentaje': progreso_porcentaje,
        'sla_info': sla_info,
        'puede_editar': request.user.is_superuser or request.user.is_staff or solicitud.asignada_a == request.user,
        'timestamp': timezone.now().timestamp(),
        'solicitudes_relacionadas': solicitudes_relacionadas,
        'mostrar_mensaje_sin_cliente': mostrar_mensaje_sin_cliente,
    }
    
    return render(request, 'workflow/detalle_solicitud_analisis.html', context)


def calcular_sla_detallado(solicitud):
    """Calcula información detallada del SLA para una solicitud"""
    
    if not solicitud.etapa_actual:
        return {
            'estado': 'sin_etapa',
            'tiempo_restante': None,
            'tiempo_transcurrido': None,
            'color_clase': 'text-muted',
            'porcentaje_usado': 0
        }
    
    # Buscar historial actual (sin fecha_fin)
    historial_actual = solicitud.historial.filter(fecha_fin__isnull=True).first()
    
    if not historial_actual:
        return {
            'estado': 'sin_historial',
            'tiempo_restante': None,
            'tiempo_transcurrido': None,
            'color_clase': 'text-muted',
            'porcentaje_usado': 0
        }
    
    # Calcular tiempo transcurrido
    tiempo_transcurrido = timezone.now() - historial_actual.fecha_inicio
    sla_total = solicitud.etapa_actual.sla
    
    # Formatear tiempo transcurrido de manera legible
    def formatear_timedelta(td):
        days = td.days
        hours, remainder = divmod(td.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days} día{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hora{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minuto{'s' if minutes != 1 else ''}")
        
        if not parts:
            return "menos de 1 minuto"
        return ", ".join(parts)
    
    tiempo_transcurrido_formateado = formatear_timedelta(tiempo_transcurrido)
    
    if sla_total:
        tiempo_restante = sla_total - tiempo_transcurrido
        porcentaje_usado = (tiempo_transcurrido.total_seconds() / sla_total.total_seconds()) * 100
        
        if tiempo_restante.total_seconds() <= 0:
            # SLA vencido
            estado = 'vencido'
            color_clase = 'text-danger'
        elif porcentaje_usado >= 75:
            # Por vencer (75% o más del SLA usado)
            estado = 'por_vencer'
            color_clase = 'text-warning'
        else:
            # En tiempo
            estado = 'en_tiempo'
            color_clase = 'text-success'
        
        tiempo_restante_formateado = formatear_timedelta(abs(tiempo_restante)) if tiempo_restante.total_seconds() < 0 else formatear_timedelta(tiempo_restante)
        
        return {
            'estado': estado,
            'tiempo_restante': tiempo_restante,
            'tiempo_restante_formateado': tiempo_restante_formateado,
            'tiempo_transcurrido': tiempo_transcurrido,
            'tiempo_transcurrido_formateado': tiempo_transcurrido_formateado,
            'color_clase': color_clase,
            'porcentaje_usado': min(porcentaje_usado, 100),
            'sla_total': sla_total
        }
    
    return {
        'estado': 'sin_sla',
        'tiempo_restante': None,
        'tiempo_transcurrido': tiempo_transcurrido,
        'tiempo_transcurrido_formateado': tiempo_transcurrido_formateado,
        'color_clase': 'text-muted',
        'porcentaje_usado': 0
    }


def convert_image_to_pdf(image_path, output_path):
    """
    Convierte una imagen a PDF usando ReportLab
    """
    try:
        # Abrir la imagen con PIL
        with Image.open(image_path) as img:
            # Convertir a RGB si es necesario (para PNG con transparencia)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Crear fondo blanco
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Obtener dimensiones de la imagen
            img_width, img_height = img.size
            
            # Crear PDF con ReportLab
            c = canvas.Canvas(output_path, pagesize=A4)
            page_width, page_height = A4
            
            # Calcular escala para que la imagen quepa en la página
            scale_x = page_width / img_width
            scale_y = page_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # No escalar más allá del 100%
            
            # Calcular posición centrada
            scaled_width = img_width * scale
            scaled_height = img_height * scale
            x = (page_width - scaled_width) / 2
            y = (page_height - scaled_height) / 2
            
            # Guardar imagen temporalmente para ReportLab
            temp_img_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_img_path.close()
            img.save(temp_img_path.name, 'PNG')
            
            # Dibujar imagen en el PDF
            c.drawImage(temp_img_path.name, x, y, width=scaled_width, height=scaled_height)
            c.save()
            
            # Limpiar archivo temporal
            try:
                os.unlink(temp_img_path.name)
            except:
                pass
                
    except Exception as e:
        raise Exception(f"Error al convertir imagen a PDF: {str(e)}")


def is_image_file(file_path):
    """
    Verifica si un archivo es una imagen basándose en su extensión
    """
    image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in image_extensions


@login_required
@csrf_exempt
def api_download_merged_pdf(request, solicitud_id):
    """API para descargar un PDF con todos los documentos de la solicitud"""
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if solicitud.asignada_a and solicitud.asignada_a != request.user:
            if not (request.user.is_superuser or request.user.is_staff):
                grupos_usuario = request.user.groups.all()
                tiene_permiso = PermisoEtapa.objects.filter(
                    etapa=solicitud.etapa_actual,
                    grupo__in=grupos_usuario,
                    puede_ver=True
                ).exists()
                if not tiene_permiso:
                    return JsonResponse({'success': False, 'error': 'No tienes permisos para acceder a esta solicitud'})
        
        # Obtener todos los requisitos con archivos
        requisitos_con_archivos = solicitud.requisitos.filter(archivo__isnull=False).exclude(archivo='')
        
        if not requisitos_con_archivos.exists():
            return JsonResponse({'success': False, 'error': 'No hay documentos disponibles para generar el PDF'})
        
        # Crear un merger de PDFs
        merger = PdfMerger()
        temp_files = []
        
        try:
            # Agregar cada documento al merger
            for requisito_solicitud in requisitos_con_archivos:
                if requisito_solicitud.archivo and os.path.exists(requisito_solicitud.archivo.path):
                    file_path = requisito_solicitud.archivo.path
                    
                    # Crear archivo temporal para el PDF
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
                    temp_files.append(temp_file.name)
                    temp_file.close()
                    
                    # Verificar si es una imagen y convertirla a PDF
                    if is_image_file(file_path):
                        try:
                            convert_image_to_pdf(file_path, temp_file.name)
                        except Exception as img_error:
                            # Si falla la conversión de imagen, crear un PDF con mensaje de error
                            c = canvas.Canvas(temp_file.name, pagesize=A4)
                            c.drawString(100, 750, f"Error al procesar imagen: {os.path.basename(file_path)}")
                            c.drawString(100, 730, f"Error: {str(img_error)}")
                            c.save()
                    else:
                        # Para archivos PDF, copiar directamente
                        with open(file_path, 'rb') as source_file:
                            with open(temp_file.name, 'wb') as temp_file_write:
                                temp_file_write.write(source_file.read())
                    
                    # Agregar al merger
                    merger.append(temp_file.name)
            
            # Crear archivo temporal para el PDF final
            output_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            output_temp.close()
            
            # Escribir el PDF combinado
            merger.write(output_temp.name)
            merger.close()
            
            # Leer el archivo final y enviarlo como respuesta
            with open(output_temp.name, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="Solicitud_{solicitud.codigo}_Documentos_Completos.pdf"'
            
            # Limpiar archivos temporales
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
            
            try:
                os.unlink(output_temp.name)
            except:
                pass
            
            return response
            
        except Exception as e:
            # Limpiar archivos temporales en caso de error
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass
            
            raise e
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al generar el PDF: {str(e)}'})


@login_required
def api_obtener_niveles_comite(request):
    """API para obtener todos los niveles de comité"""
    try:
        # Verificar permisos manualmente
        if not (request.user.is_superuser or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para acceder a esta funcionalidad'
            }, status=403)
        
        niveles = NivelComite.objects.all().order_by('orden')
        
        data = []
        for nivel in niveles:
            # Contar usuarios asignados
            usuarios_count = nivel.usuarionivelcomite_set.filter(activo=True).count()
            
            data.append({
                'id': nivel.id,
                'nombre': nivel.nombre,
                'orden': nivel.orden,
                'usuarios_count': usuarios_count,
                'usuarios': [
                    {
                        'id': u.usuario.id,
                        'username': u.usuario.username,
                        'nombre_completo': u.usuario.get_full_name() or u.usuario.username,
                        'fecha_asignacion': u.fecha_asignacion.strftime('%d/%m/%Y %H:%M'),
                        'activo': u.activo
                    }
                    for u in nivel.usuarionivelcomite_set.select_related('usuario').filter(activo=True)
                ]
            })
        
        return JsonResponse({
            'success': True,
            'niveles': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener niveles: {str(e)}'
        }, status=500)


@login_required
def api_crear_nivel_comite(request):
    """API para crear un nuevo nivel de comité"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Verificar permisos manualmente
        if not (request.user.is_superuser or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para acceder a esta funcionalidad'
            }, status=403)
        
        data = json.loads(request.body)
        
        nombre = data.get('nombre', '').strip()
        orden = data.get('orden')
        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre es requerido'}, status=400)
        
        if not orden:
            return JsonResponse({'success': False, 'error': 'El orden es requerido'}, status=400)
        
        # Verificar que no exista un nivel con el mismo nombre
        if NivelComite.objects.filter(nombre=nombre).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un nivel con ese nombre'}, status=400)
        
        # Verificar que no exista un nivel con el mismo orden
        if NivelComite.objects.filter(orden=orden).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un nivel con ese orden'}, status=400)
        
        # Crear el nivel
        nivel = NivelComite.objects.create(
            nombre=nombre,
            orden=orden
        )
        
        return JsonResponse({
            'success': True,
            'nivel': {
                'id': nivel.id,
                'nombre': nivel.nombre,
                'orden': nivel.orden,
                'usuarios_count': 0
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al crear nivel: {str(e)}'}, status=500)


@login_required
def api_actualizar_nivel_comite(request, nivel_id):
    """API para actualizar un nivel de comité"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Verificar permisos manualmente
        if not (request.user.is_superuser or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para acceder a esta funcionalidad'
            }, status=403)
        
        data = json.loads(request.body)
        
        nivel = NivelComite.objects.get(id=nivel_id)
        
        nombre = data.get('nombre', '').strip()
        orden = data.get('orden')
        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre es requerido'}, status=400)
        
        if not orden:
            return JsonResponse({'success': False, 'error': 'El orden es requerido'}, status=400)
        
        # Verificar que no exista otro nivel con el mismo nombre
        if NivelComite.objects.filter(nombre=nombre).exclude(id=nivel_id).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un nivel con ese nombre'}, status=400)
        
        # Verificar que no exista otro nivel con el mismo orden
        if NivelComite.objects.filter(orden=orden).exclude(id=nivel_id).exists():
            return JsonResponse({'success': False, 'error': 'Ya existe un nivel con ese orden'}, status=400)
        
        # Actualizar el nivel
        nivel.nombre = nombre
        nivel.orden = orden
        nivel.save()
        
        return JsonResponse({
            'success': True,
            'nivel': {
                'id': nivel.id,
                'nombre': nivel.nombre,
                'orden': nivel.orden,
                'usuarios_count': nivel.usuarionivecomite_set.filter(activo=True).count()
            }
        })
        
    except NivelComite.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Nivel no encontrado'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al actualizar nivel: {str(e)}'}, status=500)


@login_required
def api_eliminar_nivel_comite(request, nivel_id):
    """API para eliminar un nivel de comité"""
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Verificar permisos manualmente
        if not (request.user.is_superuser or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para acceder a esta funcionalidad'
            }, status=403)
        
        nivel = NivelComite.objects.get(id=nivel_id)
        
        # Verificar que no tenga usuarios asignados
        if nivel.usuarionivelcomite_set.filter(activo=True).exists():
            return JsonResponse({
                'success': False, 
                'error': 'No se puede eliminar un nivel que tiene usuarios asignados'
            }, status=400)
        
        # Verificar que no tenga participaciones en comité
        if nivel.participacioncomite_set.exists():
            return JsonResponse({
                'success': False, 
                'error': 'No se puede eliminar un nivel que tiene participaciones registradas'
            }, status=400)
        
        nivel.delete()
        
        return JsonResponse({'success': True})
        
    except NivelComite.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Nivel no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al eliminar nivel: {str(e)}'}, status=500)


@login_required
def api_asignar_usuario_nivel_comite(request):
    """API para asignar un usuario a un nivel de comité"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Verificar permisos manualmente
        if not (request.user.is_superuser or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para acceder a esta funcionalidad'
            }, status=403)
        
        data = json.loads(request.body)
        
        usuario_id = data.get('usuario_id')
        nivel_id = data.get('nivel_id')
        activo = data.get('activo', True)
        observaciones = data.get('observaciones', '').strip()
        
        if not usuario_id or not nivel_id:
            return JsonResponse({'success': False, 'error': 'Usuario y nivel son requeridos'}, status=400)
        
        # Verificar que el usuario y nivel existen
        try:
            usuario = User.objects.get(id=usuario_id)
            nivel = NivelComite.objects.get(id=nivel_id)
        except (User.DoesNotExist, NivelComite.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'Usuario o nivel no encontrado'}, status=404)
        
        # Crear o actualizar la asignación
        asignacion, created = UsuarioNivelComite.objects.get_or_create(
            usuario=usuario,
            nivel=nivel,
            defaults={
                'activo': activo,
                'observaciones': observaciones
            }
        )
        
        if not created:
            asignacion.activo = activo
            asignacion.observaciones = observaciones
            asignacion.save()
        
        return JsonResponse({
            'success': True,
            'asignacion': {
                'id': asignacion.id,
                'usuario': {
                    'id': usuario.id,
                    'username': usuario.username,
                    'nombre_completo': usuario.get_full_name() or usuario.username
                },
                'nivel': {
                    'id': nivel.id,
                    'nombre': nivel.nombre,
                    'orden': nivel.orden
                },
                'fecha_asignacion': asignacion.fecha_asignacion.strftime('%d/%m/%Y %H:%M'),
                'activo': asignacion.activo,
                'observaciones': asignacion.observaciones or ''
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Datos JSON inválidos'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al asignar usuario: {str(e)}'}, status=500)


@login_required
def api_desasignar_usuario_nivel_comite(request, usuario_id, nivel_id):
    """API para desasignar un usuario de un nivel de comité"""
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        # Verificar permisos manualmente
        if not (request.user.is_superuser or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para acceder a esta funcionalidad'
            }, status=403)
        
        asignacion = UsuarioNivelComite.objects.get(
            usuario_id=usuario_id,
            nivel_id=nivel_id
        )
        
        # En lugar de eliminar, desactivar
        asignacion.activo = False
        asignacion.save()
        
        return JsonResponse({'success': True})
        
    except UsuarioNivelComite.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Asignación no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al desasignar usuario: {str(e)}'}, status=500)


@login_required
def api_obtener_asignaciones_comite(request):
    """Obtener todas las asignaciones de usuarios a niveles del comité"""
    try:
        from .modelsWorkflow import UsuarioNivelComite
        
        asignaciones = UsuarioNivelComite.objects.select_related(
            'usuario', 'nivel', 'usuario__userprofile'
        ).order_by('nivel__orden', 'usuario__username')
        
        data = []
        for asignacion in asignaciones:
            data.append({
                'id': asignacion.id,
                'usuario': {
                    'id': asignacion.usuario.id,
                    'username': asignacion.usuario.username,
                    'full_name': asignacion.usuario.get_full_name() or asignacion.usuario.username,
                    'email': asignacion.usuario.email,
                    'profile_picture': asignacion.usuario.userprofile.profile_picture.url if hasattr(asignacion.usuario, 'userprofile') and asignacion.usuario.userprofile.profile_picture else None
                },
                'nivel': {
                    'id': asignacion.nivel.id,
                    'nombre': asignacion.nivel.nombre,
                    'orden': asignacion.nivel.orden
                },
                'activo': asignacion.activo,
                'fecha_asignacion': asignacion.fecha_asignacion.strftime('%d/%m/%Y %H:%M'),
                'observaciones': asignacion.observaciones or ''
            })
        
        return JsonResponse({
            'success': True,
            'asignaciones': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener asignaciones: {str(e)}'
        })


@login_required
def api_cambiar_estado_asignacion_comite(request, asignacion_id):
    """Cambiar el estado activo/inactivo de una asignación"""
    try:
        from .modelsWorkflow import UsuarioNivelComite
        import json
        
        asignacion = get_object_or_404(UsuarioNivelComite, id=asignacion_id)
        data = json.loads(request.body)
        activo = data.get('activo', True)
        
        asignacion.activo = activo
        asignacion.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Asignación {"activada" if activo else "desactivada"} exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al cambiar estado: {str(e)}'
        })


@login_required
def api_eliminar_asignacion_comite(request, asignacion_id):
    """Eliminar una asignación de usuario a nivel"""
    try:
        from .modelsWorkflow import UsuarioNivelComite
        
        asignacion = get_object_or_404(UsuarioNivelComite, id=asignacion_id)
        asignacion.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Asignación eliminada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al eliminar asignación: {str(e)}'
        })


@login_required
def api_estadisticas_comite(request):
    """Obtener estadísticas del comité"""
    try:
        from .modelsWorkflow import NivelComite, UsuarioNivelComite
        
        total_niveles = NivelComite.objects.count()
        usuarios_asignados = UsuarioNivelComite.objects.count()
        usuarios_activos = UsuarioNivelComite.objects.filter(activo=True).count()
        
        # Obtener el nivel más alto (menor orden)
        nivel_mas_alto = NivelComite.objects.order_by('orden').first()
        nivel_mas_alto_nombre = nivel_mas_alto.nombre if nivel_mas_alto else None
        
        return JsonResponse({
            'success': True,
            'estadisticas': {
                'total_niveles': total_niveles,
                'usuarios_asignados': usuarios_asignados,
                'usuarios_activos': usuarios_activos,
                'nivel_mas_alto': nivel_mas_alto_nombre
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener estadísticas: {str(e)}'
        })


@login_required
def api_obtener_usuarios_disponibles_comite(request):
    """API para obtener usuarios disponibles para asignar al comité"""
    try:
        # Verificar permisos manualmente
        if not (request.user.is_superuser or request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para acceder a esta funcionalidad'
            }, status=403)
        
        # Obtener usuarios activos
        usuarios = User.objects.filter(is_active=True).order_by('username')
        
        data = []
        for usuario in usuarios:
            # Obtener niveles asignados
            niveles_asignados = usuario.usuarionivelcomite_set.filter(activo=True).select_related('nivel')
            
            data.append({
                'id': usuario.id,
                'username': usuario.username,
                'nombre_completo': usuario.get_full_name() or usuario.username,
                'email': usuario.email,
                'is_staff': usuario.is_staff,
                'is_superuser': usuario.is_superuser,
                'niveles_asignados': [
                    {
                        'id': n.nivel.id,
                        'nombre': n.nivel.nombre,
                        'orden': n.nivel.orden
                    }
                    for n in niveles_asignados
                ]
            })
        
        return JsonResponse({
            'success': True,
            'usuarios': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener usuarios: {str(e)}'
        }, status=500)


# ==========================================
# VISTAS Y APIs PARA TRACKING DE APC MAKITO
# ==========================================

@login_required
def apc_tracking_view(request):
    """
    Vista para mostrar el tracking de solicitudes APC pendientes con Makito
    """
    # Obtener todas las solicitudes que tienen APC habilitado
    solicitudes_apc = Solicitud.objects.filter(
        descargar_apc_makito=True
    ).select_related(
        'pipeline', 'creada_por', 'etapa_actual', 'cliente', 'cotizacion'
    )
    
    # Aplicar filtro de usuario si no es superuser
    if not request.user.is_superuser:
        solicitudes_apc = solicitudes_apc.filter(propietario=request.user)
    
    solicitudes_apc = solicitudes_apc.order_by('-apc_fecha_solicitud')
    
    context = {
        'solicitudes_apc': solicitudes_apc,
        'title': 'Tracking APC Makito',
        'tracking_type': 'apc',
    }
    
    return render(request, 'workflow/makito_tracking.html', context)


@login_required
def makito_tracking_view(request):
    """
    Vista unificada para mostrar el tracking de solicitudes APC, SURA y Debida Diligencia con Makito
    """
    # Obtener todas las solicitudes que tienen APC, SURA o Debida Diligencia habilitado
    solicitudes_apc = Solicitud.objects.filter(
        descargar_apc_makito=True
    ).select_related(
        'pipeline', 'creada_por', 'etapa_actual', 'cliente', 'cotizacion'
    )
    
    solicitudes_sura = Solicitud.objects.filter(
        cotizar_sura_makito=True
    ).select_related(
        'pipeline', 'creada_por', 'etapa_actual', 'cliente', 'cotizacion'
    )
    
    solicitudes_diligencia = Solicitud.objects.filter(
        debida_diligencia_status__in=['solicitado', 'en_progreso', 'completado', 'error']
    ).select_related(
        'pipeline', 'creada_por', 'etapa_actual', 'cliente', 'cotizacion'
    )
    
    # Aplicar filtro de usuario si no es superuser
    if not request.user.is_superuser:
        solicitudes_apc = solicitudes_apc.filter(propietario=request.user)
        solicitudes_sura = solicitudes_sura.filter(propietario=request.user)
        solicitudes_diligencia = solicitudes_diligencia.filter(propietario=request.user)
    
    # Ordenar por fecha
    solicitudes_apc = solicitudes_apc.order_by('-apc_fecha_solicitud')
    solicitudes_sura = solicitudes_sura.order_by('-sura_fecha_solicitud')
    solicitudes_diligencia = solicitudes_diligencia.order_by('-diligencia_fecha_solicitud')
    
    context = {
        'solicitudes_apc': solicitudes_apc,
        'solicitudes_sura': solicitudes_sura,
        'solicitudes_diligencia': solicitudes_diligencia,
        'title': 'Tracking Solicitudes Makito',
        'tracking_type': 'unified',
    }
    
    return render(request, 'workflow/makito_tracking.html', context)


@login_required
def sura_tracking_view(request):
    """
    Vista para mostrar el tracking de cotizaciones SURA con Makito
    """
    # Obtener todas las solicitudes que tienen SURA habilitado
    solicitudes_sura = Solicitud.objects.filter(
        cotizar_sura_makito=True
    ).select_related(
        'pipeline', 'creada_por', 'etapa_actual', 'cliente', 'cotizacion'
    )
    
    # Aplicar filtro de usuario si no es superuser
    if not request.user.is_superuser:
        solicitudes_sura = solicitudes_sura.filter(propietario=request.user)
    
    solicitudes_sura = solicitudes_sura.order_by('-sura_fecha_solicitud')
    
    context = {
        'solicitudes_sura': solicitudes_sura,
        'title': 'Tracking SURA Makito',
        'tracking_type': 'sura',
    }
    
    return render(request, 'workflow/makito_tracking.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def api_makito_update_status(request, solicitud_codigo):
    """
    API para que Makito RPA actualice el estado de una solicitud APC
    URL: /workflow/api/makito/update-status/{codigo}/
    
    Body esperado:
    {
        "status": "in_progress" | "completed" | "error",
        "observaciones": "Opcional: descripción del proceso"
    }
    """
    try:
        import json
        from django.utils import timezone
        
        # Parsear datos JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Datos JSON inválidos'
            }, status=400)
        
        # Validar campos requeridos
        nuevo_status = data.get('status')
        observaciones = data.get('observaciones', '')
        
        if not nuevo_status:
            return JsonResponse({
                'success': False,
                'error': 'Campo status es requerido'
            }, status=400)
        
        # Validar que el status sea válido
        status_validos = ['pending', 'in_progress', 'completed', 'error']
        if nuevo_status not in status_validos:
            return JsonResponse({
                'success': False,
                'error': f'Status inválido. Valores permitidos: {status_validos}'
            }, status=400)
        
        # Buscar la solicitud por código
        try:
            solicitud = Solicitud.objects.get(codigo=solicitud_codigo, descargar_apc_makito=True)
        except Solicitud.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Solicitud con código {solicitud_codigo} no encontrada o no tiene APC habilitado'
            }, status=404)
        
        # Actualizar el status y timestamps correspondientes
        solicitud.apc_status = nuevo_status
        solicitud.apc_observaciones = observaciones
        
        now = timezone.now()
        fields_to_update = ['apc_status', 'apc_observaciones']
        
        if nuevo_status == 'in_progress' and not solicitud.apc_fecha_inicio:
            solicitud.apc_fecha_inicio = now
            fields_to_update.append('apc_fecha_inicio')
        
        if nuevo_status == 'completed' and not solicitud.apc_fecha_completado:
            solicitud.apc_fecha_completado = now
            fields_to_update.append('apc_fecha_completado')
        
        solicitud.save(update_fields=fields_to_update)
        
        # Enviar notificación por correo según el estado
        try:
            if nuevo_status == 'in_progress' and 'apc_fecha_inicio' in fields_to_update:
                # Solo enviar si es la primera vez que se marca como in_progress
                enviar_correo_apc_iniciado(solicitud)
            elif nuevo_status == 'completed' and 'apc_fecha_completado' in fields_to_update:
                # Solo enviar si es la primera vez que se marca como completed
                enviar_correo_apc_completado(solicitud)
        except Exception as e:
            # Log the error but don't fail the API call
            print(f"⚠️ Error al enviar notificación por correo para solicitud {solicitud_codigo}: {str(e)}")
        
        return JsonResponse({
            'success': True,
            'message': f'Status APC actualizado a {nuevo_status} para solicitud {solicitud_codigo}',
            'data': {
                'codigo': solicitud.codigo,
                'status': solicitud.apc_status,
                'fecha_solicitud': solicitud.apc_fecha_solicitud.isoformat() if solicitud.apc_fecha_solicitud else None,
                'fecha_inicio': solicitud.apc_fecha_inicio.isoformat() if solicitud.apc_fecha_inicio else None,
                'fecha_completado': solicitud.apc_fecha_completado.isoformat() if solicitud.apc_fecha_completado else None,
                'observaciones': solicitud.apc_observaciones
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_makito_upload_apc(request, solicitud_codigo):
    """
    API para que Makito RPA suba el archivo APC y marque como completado
    URL: /workflow/api/makito/upload-apc/{codigo}/
    
    Form data esperado:
    - apc_file: archivo PDF
    - observaciones: (opcional) descripción del proceso
    """
    try:
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        from django.db import transaction
        import uuid
        
        # Buscar la solicitud por código
        try:
            solicitud = Solicitud.objects.get(codigo=solicitud_codigo, descargar_apc_makito=True)
        except Solicitud.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': f'Solicitud con código {solicitud_codigo} no encontrada o no tiene APC habilitado'
            }, status=404)
        
        # Verificar que hay un archivo
        if 'apc_file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No se proporcionó archivo APC'
            }, status=400)
        
        apc_file = request.FILES['apc_file']
        
        # Validar que es un PDF
        if not apc_file.name.lower().endswith('.pdf'):
            return JsonResponse({
                'success': False,
                'error': 'El archivo debe ser un PDF'
            }, status=400)
        
        # Validar tamaño del archivo (máx 10MB)
        if apc_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'El archivo es demasiado grande (máx 10MB)'
            }, status=400)
        
        # Generar nombre único para el archivo
        file_extension = '.pdf'
        unique_filename = f"apc_{solicitud.codigo}_{uuid.uuid4().hex[:8]}{file_extension}"
        
        # Actualizar la solicitud
        with transaction.atomic():
            # Guardar el archivo directamente en el campo FileField
            solicitud.apc_archivo.save(unique_filename, apc_file)
            
            # Actualizar campos de estado
            solicitud.apc_status = 'completed'
            solicitud.apc_fecha_completado = timezone.now()
            solicitud.apc_observaciones = request.POST.get('observaciones', 'APC generado exitosamente por Makito RPA')
            solicitud.save()
            
            # Crear historial
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=solicitud.etapa_actual,
                usuario_responsable=None,  # Sistema automático
                fecha_inicio=timezone.now()
            )
        
        # Notificar al propietario de la solicitud
        try:
            print(f"🔔 Enviando correo de APC completado para solicitud {solicitud.codigo}...")
            enviar_correo_apc_completado(solicitud)
            print(f"✅ Correo de APC completado enviado exitosamente")
        except Exception as e:
            print(f"❌ Error enviando correo APC completado: {e}")
            import traceback
            print(f"❌ Traceback completo: {traceback.format_exc()}")
            # No fallar la operación si el correo falla
        
        return JsonResponse({
            'success': True,
            'message': 'APC subido y marcado como completado exitosamente',
            'data': {
                'codigo': solicitud.codigo,
                'apc_status': solicitud.apc_status,
                'apc_observaciones': solicitud.apc_observaciones,
                'apc_fecha_completado': solicitud.apc_fecha_completado.isoformat(),
                'apc_archivo_url': solicitud.apc_archivo.url if solicitud.apc_archivo else None
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


def enviar_correo_apc_completado(solicitud):
    """
    Función para enviar correo automático cuando el APC es completado por Makito.
    """
    try:
        # Obtener usuarios a notificar
        usuarios_notificar = [solicitud.creada_por]
        if solicitud.asignada_a and solicitud.asignada_a != solicitud.creada_por:
            usuarios_notificar.append(solicitud.asignada_a)
        
        # Obtener emails válidos
        destinatarios = []
        for usuario in usuarios_notificar:
            if usuario.email:
                destinatarios.append(usuario.email)
        
        if not destinatarios:
            print(f"⚠️ No se encontraron emails válidos para notificar sobre solicitud {solicitud.codigo}")
            return
        
        # Obtener nombre del cliente usando las propiedades del modelo
        cliente_nombre = solicitud.cliente_nombre or "Cliente no asignado"
        
        # Obtener la URL base dinámicamente
        from django.conf import settings
        
        # Try to get base URL from settings, fallback to request if available
        base_url = getattr(settings, 'SITE_URL', 'https://pacifico.com')
        
        # URL para ver la solicitud
        solicitud_url = f"{base_url}/workflow/solicitud/{solicitud.id}/"
        
        # URL para descargar el archivo APC (si está disponible)
        archivo_url = None
        if solicitud.apc_archivo:
            try:
                archivo_url = f"{base_url}{solicitud.apc_archivo.url}"
            except:
                archivo_url = "Archivo disponible en el sistema"
        
        # Contexto para el template HTML
        context = {
            'solicitud': solicitud,
            'cliente_nombre': cliente_nombre,
            'solicitud_url': solicitud_url,
            'archivo_url': archivo_url,
        }
        
        # Cargar el template HTML
        html_content = render_to_string('workflow/emails/apc_completado_notification.html', context)
        
        # Crear el asunto
        subject = f'✅ APC Completado - Solicitud {solicitud.codigo} - {cliente_nombre}'
        
        # Mensaje de texto plano como respaldo
        text_content = f"""
APC Completado Exitosamente

Estimado {solicitud.creada_por.get_full_name() or solicitud.creada_por.username},

El proceso de APC para la solicitud {solicitud.codigo} ha sido completado exitosamente por Makito RPA.

DETALLES DE LA SOLICITUD:
• Código: {solicitud.codigo}
• Cliente: {cliente_nombre}
• Pipeline: {solicitud.pipeline.nombre}
• Fecha de completado: {solicitud.apc_fecha_completado.strftime('%d/%m/%Y %H:%M')}
• Tipo de documento: {solicitud.get_apc_tipo_documento_display() if solicitud.apc_tipo_documento else 'No especificado'}
• Número de documento: {solicitud.apc_no_cedula or 'No especificado'}

ARCHIVO APC:
{f'• Archivo disponible: {archivo_url}' if archivo_url else '• El archivo está disponible en el sistema'}

OBSERVACIONES:
{solicitud.apc_observaciones or 'Sin observaciones adicionales'}

Para ver todos los detalles de la solicitud:
{solicitud_url}

Saludos,
Sistema de Workflow - Financiera Pacífico

---
Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=destinatarios,
        )
        
        # Agregar el contenido HTML
        email.attach_alternative(html_content, "text/html")
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
            print(f"✅ Correo APC completado enviado correctamente para solicitud {solicitud.codigo}")
            print(f"✅ Destinatarios: {', '.join(destinatarios)}")
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
            print(f"✅ Correo APC completado enviado correctamente (con SSL personalizado) para solicitud {solicitud.codigo}")
        except Exception as e:
            print(f"❌ Error específico al enviar correo APC completado: {str(e)}")
            raise  # Re-raise para que se maneje en el nivel superior
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo APC completado para solicitud {solicitud.codigo}: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")


def enviar_correo_apc_iniciado(solicitud):
    """
    Función para enviar correo automático cuando el APC es iniciado (in_progress) por Makito.
    """
    try:
        # Obtener usuarios a notificar
        usuarios_notificar = [solicitud.creada_por]
        if solicitud.asignada_a and solicitud.asignada_a != solicitud.creada_por:
            usuarios_notificar.append(solicitud.asignada_a)
        
        # Obtener emails válidos
        destinatarios = []
        for usuario in usuarios_notificar:
            if usuario.email:
                destinatarios.append(usuario.email)
        
        if not destinatarios:
            print(f"⚠️ No se encontraron emails válidos para notificar sobre solicitud {solicitud.codigo}")
            return
        
        # Obtener nombre del cliente usando las propiedades del modelo
        cliente_nombre = solicitud.cliente_nombre or "Cliente no asignado"
        
        # Obtener la URL base dinámicamente
        from django.conf import settings
        
        # Try to get base URL from settings, fallback to request if available
        base_url = getattr(settings, 'SITE_URL', 'https://pacifico.com')
        
        # URL para ver la solicitud
        solicitud_url = f"{base_url}/workflow/solicitud/{solicitud.id}/"
        
        # Contexto para el template HTML
        context = {
            'solicitud': solicitud,
            'cliente_nombre': cliente_nombre,
            'solicitud_url': solicitud_url,
        }
        
        # Cargar el template HTML
        html_content = render_to_string('workflow/emails/apc_iniciado_notification.html', context)
        
        # Crear el asunto
        subject = f'🔄 APC En Proceso - Solicitud {solicitud.codigo} - {cliente_nombre}'
        
        # Mensaje de texto plano como respaldo
        text_content = f"""
APC En Proceso de Extracción

Estimado {solicitud.creada_por.get_full_name() or solicitud.creada_por.username},

El proceso de APC para la solicitud {solicitud.codigo} ha sido iniciado por Makito RPA y se encuentra actualmente en proceso de extracción.

DETALLES DE LA SOLICITUD:
• Código: {solicitud.codigo}
• Cliente: {cliente_nombre}
• Pipeline: {solicitud.pipeline.nombre}
• Fecha de inicio del proceso: {solicitud.apc_fecha_inicio.strftime('%d/%m/%Y %H:%M') if solicitud.apc_fecha_inicio else 'En proceso'}
• Tipo de documento: {solicitud.get_apc_tipo_documento_display() if solicitud.apc_tipo_documento else 'No especificado'}
• Número de documento: {solicitud.apc_no_cedula or 'No especificado'}

ESTADO ACTUAL:
• El proceso de extracción de APC está en curso
• Recibirás una notificación adicional cuando el proceso se complete
• El archivo APC estará disponible una vez finalizado el proceso

OBSERVACIONES:
{solicitud.apc_observaciones or 'Sin observaciones adicionales'}

Para ver todos los detalles de la solicitud:
{solicitud_url}

Saludos,
Sistema de Workflow - Financiera Pacífico

---
Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=destinatarios,
        )
        
        # Agregar el contenido HTML
        email.attach_alternative(html_content, "text/html")
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
            print(f"✅ Correo APC iniciado enviado correctamente para solicitud {solicitud.codigo}")
            print(f"✅ Destinatarios: {', '.join(destinatarios)}")
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
            print(f"✅ Correo APC iniciado enviado correctamente (con SSL personalizado) para solicitud {solicitud.codigo}")
        except Exception as e:
            print(f"❌ Error específico al enviar correo APC iniciado: {str(e)}")
            raise  # Re-raise para que se maneje en el nivel superior
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo APC iniciado para solicitud {solicitud.codigo}: {str(e)}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")


# ==========================================
# SURA EMAIL NOTIFICATIONS
# ==========================================

def enviar_correo_sura_completado(solicitud):
    """
    Función para enviar correo automático cuando la cotización SURA es completada por Makito.
    """
    try:
        # Obtener usuarios a notificar
        usuarios_notificar = [solicitud.creada_por]
        if solicitud.asignada_a and solicitud.asignada_a != solicitud.creada_por:
            usuarios_notificar.append(solicitud.asignada_a)
        
        # Obtener emails válidos
        destinatarios = []
        for usuario in usuarios_notificar:
            if usuario.email:
                destinatarios.append(usuario.email)
        
        if not destinatarios:
            print(f"⚠️ No se encontraron emails válidos para notificar sobre solicitud SURA {solicitud.codigo}")
            return
        
        # Obtener nombre del cliente usando las propiedades del modelo
        cliente_nombre = solicitud.cliente_nombre_completo or "Cliente no asignado"
        
        # Obtener la URL base dinámicamente
        from django.conf import settings
        
        # Try to get base URL from settings, fallback to request if available
        base_url = getattr(settings, 'SITE_URL', 'https://pacifico.com')
        
        # URL para ver el tracking de Makito SURA
        solicitud_url = f"{base_url}/workflow/makito-tracking/"
        
        # URL para descargar el archivo SURA (si está disponible)
        archivo_url = None
        if solicitud.sura_archivo:
            try:
                archivo_url = f"{base_url}{solicitud.sura_archivo.url}"
            except:
                archivo_url = "Archivo disponible en el sistema"
        
        # Crear el asunto
        subject = f'✅ Cotización SURA Completada - Solicitud {solicitud.codigo} - {cliente_nombre}'
        
        # Mensaje de texto plano
        text_content = f"""
Cotización SURA Completada Exitosamente

Estimado {solicitud.creada_por.get_full_name() or solicitud.creada_por.username},

La cotización SURA para la solicitud {solicitud.codigo} ha sido completada exitosamente por Makito RPA.

DETALLES DE LA SOLICITUD:
• Código: {solicitud.codigo}
• Cliente: {cliente_nombre}
• Pipeline: {solicitud.pipeline.nombre}
• Fecha de completado: {solicitud.sura_fecha_completado.strftime('%d/%m/%Y %H:%M') if solicitud.sura_fecha_completado else 'Recién completado'}

INFORMACIÓN DEL CLIENTE PARA SURA:
• Primer Nombre: {solicitud.sura_primer_nombre or 'N/A'}
• Segundo Nombre: {solicitud.sura_segundo_nombre or 'N/A'}
• Primer Apellido: {solicitud.sura_primer_apellido or 'N/A'}
• Segundo Apellido: {solicitud.sura_segundo_apellido or 'N/A'}
• Número de Documento: {solicitud.sura_no_documento or 'N/A'}

INFORMACIÓN DEL VEHÍCULO:
• Valor del Auto: ${solicitud.sura_valor_auto or 'N/A'}
• Año del Auto: {solicitud.sura_ano_auto or 'N/A'}
• Marca: {solicitud.sura_marca or 'N/A'}
• Modelo: {solicitud.sura_modelo or 'N/A'}

ARCHIVO DE COTIZACIÓN:
{f'• Archivo disponible: {archivo_url}' if archivo_url else '• El archivo está disponible en el sistema'}

OBSERVACIONES:
{solicitud.sura_observaciones or 'Sin observaciones adicionales'}

Para ver el tracking de todas las solicitudes SURA:
{solicitud_url}

Saludos,
Sistema de Workflow - Financiera Pacífico

---
Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Render HTML content using template
        from django.template.loader import render_to_string
        html_content = render_to_string('workflow/emails/sura_completado_notification.html', {
            'solicitud': solicitud,
            'cliente_nombre': cliente_nombre,
            'solicitud_url': solicitud_url,
            'archivo_url': archivo_url,
        })
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=destinatarios,
        )
        
        # Attach HTML version
        email.attach_alternative(html_content, "text/html")
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
            print(f"✅ Correo SURA completado enviado correctamente para solicitud {solicitud.codigo}")
            print(f"✅ Destinatarios: {', '.join(destinatarios)}")
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
            print(f"✅ Correo SURA completado enviado correctamente (con SSL personalizado) para solicitud {solicitud.codigo}")
        except Exception as e:
            print(f"❌ Error específico al enviar correo SURA completado: {str(e)}")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo SURA completado para solicitud {solicitud.codigo}: {str(e)}")


def enviar_correo_sura_iniciado(solicitud):
    """
    Función para enviar correo automático cuando la cotización SURA es iniciada (in_progress) por Makito.
    """
    try:
        # Obtener usuarios a notificar
        usuarios_notificar = [solicitud.creada_por]
        if solicitud.asignada_a and solicitud.asignada_a != solicitud.creada_por:
            usuarios_notificar.append(solicitud.asignada_a)
        
        # Obtener emails válidos
        destinatarios = []
        for usuario in usuarios_notificar:
            if usuario.email:
                destinatarios.append(usuario.email)
        
        if not destinatarios:
            print(f"⚠️ No se encontraron emails válidos para notificar sobre solicitud SURA {solicitud.codigo}")
            return
        
        # Obtener nombre del cliente usando las propiedades del modelo
        cliente_nombre = solicitud.cliente_nombre_completo or "Cliente no asignado"
        
        # Obtener la URL base dinámicamente
        from django.conf import settings
        
        # Try to get base URL from settings, fallback to request if available
        base_url = getattr(settings, 'SITE_URL', 'https://pacifico.com')
        
        # URL para ver el tracking de Makito SURA
        solicitud_url = f"{base_url}/workflow/makito-tracking/"
        
        # Crear el asunto
        subject = f'🔄 Cotización SURA En Proceso - Solicitud {solicitud.codigo} - {cliente_nombre}'
        
        # Mensaje de texto plano
        text_content = f"""
Cotización SURA En Proceso

Estimado {solicitud.creada_por.get_full_name() or solicitud.creada_por.username},

La cotización SURA para la solicitud {solicitud.codigo} ha sido iniciada por Makito RPA y se encuentra actualmente en proceso.

DETALLES DE LA SOLICITUD:
• Código: {solicitud.codigo}
• Cliente: {cliente_nombre}
• Pipeline: {solicitud.pipeline.nombre}
• Fecha de inicio del proceso: {solicitud.sura_fecha_inicio.strftime('%d/%m/%Y %H:%M') if solicitud.sura_fecha_inicio else 'En proceso'}

INFORMACIÓN DEL CLIENTE PARA SURA:
• Primer Nombre: {solicitud.sura_primer_nombre or 'N/A'}
• Segundo Nombre: {solicitud.sura_segundo_nombre or 'N/A'}
• Primer Apellido: {solicitud.sura_primer_apellido or 'N/A'}
• Segundo Apellido: {solicitud.sura_segundo_apellido or 'N/A'}
• Número de Documento: {solicitud.sura_no_documento or 'N/A'}

INFORMACIÓN DEL VEHÍCULO:
• Valor del Auto: ${solicitud.sura_valor_auto or 'N/A'}
• Año del Auto: {solicitud.sura_ano_auto or 'N/A'}
• Marca: {solicitud.sura_marca or 'N/A'}
• Modelo: {solicitud.sura_modelo or 'N/A'}

ESTADO ACTUAL:
• El proceso de cotización SURA está en curso
• Recibirás una notificación adicional cuando el proceso se complete
• El archivo de cotización estará disponible una vez finalizado el proceso

OBSERVACIONES:
{solicitud.sura_observaciones or 'Sin observaciones adicionales'}

Para ver el tracking de todas las solicitudes SURA:
{solicitud_url}

Saludos,
Sistema de Workflow - Financiera Pacífico

---
Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Render HTML content using template
        from django.template.loader import render_to_string
        html_content = render_to_string('workflow/emails/sura_iniciado_notification.html', {
            'solicitud': solicitud,
            'cliente_nombre': cliente_nombre,
            'solicitud_url': solicitud_url,
        })
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=destinatarios,
        )
        
        # Attach HTML version
        email.attach_alternative(html_content, "text/html")
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
            print(f"✅ Correo SURA iniciado enviado correctamente para solicitud {solicitud.codigo}")
            print(f"✅ Destinatarios: {', '.join(destinatarios)}")
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
            print(f"✅ Correo SURA iniciado enviado correctamente (con SSL personalizado) para solicitud {solicitud.codigo}")
        except Exception as e:
            print(f"❌ Error específico al enviar correo SURA iniciado: {str(e)}")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo SURA iniciado para solicitud {solicitud.codigo}: {str(e)}")


def enviar_correo_sura_error(solicitud, mensaje_error="Error en el procesamiento"):
    """
    Función para enviar correo automático cuando hay un error en la cotización SURA.
    """
    try:
        # Obtener usuarios a notificar
        usuarios_notificar = [solicitud.creada_por]
        if solicitud.asignada_a and solicitud.asignada_a != solicitud.creada_por:
            usuarios_notificar.append(solicitud.asignada_a)
        
        # Obtener emails válidos
        destinatarios = []
        for usuario in usuarios_notificar:
            if usuario.email:
                destinatarios.append(usuario.email)
        
        if not destinatarios:
            print(f"⚠️ No se encontraron emails válidos para notificar sobre error SURA {solicitud.codigo}")
            return
        
        # Obtener nombre del cliente usando las propiedades del modelo
        cliente_nombre = solicitud.cliente_nombre_completo or "Cliente no asignado"
        
        # Obtener la URL base dinámicamente
        from django.conf import settings
        
        # Try to get base URL from settings, fallback to request if available
        base_url = getattr(settings, 'SITE_URL', 'https://pacifico.com')
        
        # URL para ver el tracking de Makito SURA
        solicitud_url = f"{base_url}/workflow/makito-tracking/"
        
        # Crear el asunto
        subject = f'❌ Error en Cotización SURA - Solicitud {solicitud.codigo} - {cliente_nombre}'
        
        # Mensaje de texto plano
        text_content = f"""
Error en Cotización SURA

Estimado {solicitud.creada_por.get_full_name() or solicitud.creada_por.username},

Se ha producido un error durante el procesamiento de la cotización SURA para la solicitud {solicitud.codigo}.

DETALLES DE LA SOLICITUD:
• Código: {solicitud.codigo}
• Cliente: {cliente_nombre}
• Pipeline: {solicitud.pipeline.nombre}
• Fecha del error: {timezone.now().strftime('%d/%m/%Y %H:%M')}

INFORMACIÓN DEL CLIENTE PARA SURA:
• Primer Nombre: {solicitud.sura_primer_nombre or 'N/A'}
• Segundo Nombre: {solicitud.sura_segundo_nombre or 'N/A'}
• Primer Apellido: {solicitud.sura_primer_apellido or 'N/A'}
• Segundo Apellido: {solicitud.sura_segundo_apellido or 'N/A'}
• Número de Documento: {solicitud.sura_no_documento or 'N/A'}

INFORMACIÓN DEL VEHÍCULO:
• Valor del Auto: ${solicitud.sura_valor_auto or 'N/A'}
• Año del Auto: {solicitud.sura_ano_auto or 'N/A'}
• Marca: {solicitud.sura_marca or 'N/A'}
• Modelo: {solicitud.sura_modelo or 'N/A'}

DESCRIPCIÓN DEL ERROR:
{mensaje_error}

OBSERVACIONES ADICIONALES:
{solicitud.sura_observaciones or 'Sin observaciones adicionales'}

ACCIONES RECOMENDADAS:
• Verifique que los datos del cliente y vehículo sean correctos
• Revise el estado de la solicitud en el sistema
• Contacte al equipo de soporte si el problema persiste

Para ver el tracking de todas las solicitudes SURA:
{solicitud_url}

Saludos,
Sistema de Workflow - Financiera Pacífico

---
Este es un correo automático, por favor no responder a esta dirección.
        """
        
        # Render HTML content using template
        from django.template.loader import render_to_string
        html_content = render_to_string('workflow/emails/sura_error_notification.html', {
            'solicitud': solicitud,
            'cliente_nombre': cliente_nombre,
            'solicitud_url': solicitud_url,
            'mensaje_error': mensaje_error,
        })
        
        # Crear el correo usando EmailMultiAlternatives
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'workflow@fpacifico.com'),
            to=destinatarios,
        )
        
        # Attach HTML version
        email.attach_alternative(html_content, "text/html")
        
        # Enviar el correo con manejo de SSL personalizado
        try:
            email.send()
            print(f"✅ Correo SURA error enviado correctamente para solicitud {solicitud.codigo}")
            print(f"✅ Destinatarios: {', '.join(destinatarios)}")
        except ssl.SSLCertVerificationError as ssl_error:
            print(f"⚠️ Error SSL detectado, intentando con contexto SSL personalizado: {ssl_error}")
            # Crear contexto SSL que no verifica certificados
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Reenviar con contexto SSL personalizado
            from django.core.mail import get_connection
            connection = get_connection()
            connection.ssl_context = ssl_context
            email.connection = connection
            email.send()
            print(f"✅ Correo SURA error enviado correctamente (con SSL personalizado) para solicitud {solicitud.codigo}")
        except Exception as e:
            print(f"❌ Error específico al enviar correo SURA error: {str(e)}")
        
    except Exception as e:
        # Registrar el error pero no romper el flujo
        print(f"❌ Error al enviar correo SURA error para solicitud {solicitud.codigo}: {str(e)}")


@login_required
def test_apc_upload_email(request):
    """
    Vista para probar el envío de correo de APC completado
    Solo para testing - eliminar en producción
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        # Buscar una solicitud con APC habilitado para testing
        solicitud = Solicitud.objects.filter(descargar_apc_makito=True).first()
        
        if not solicitud:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró ninguna solicitud con APC habilitado para testing'
            })
        
        # Simular que se completó el APC
        from django.utils import timezone
        solicitud.apc_status = 'completed'
        solicitud.apc_fecha_completado = timezone.now()
        solicitud.apc_observaciones = 'APC de prueba completado - TEST'
        
        # No guardar en la base de datos, solo simular
        
        print(f"🧪 Testing envío de correo APC completado para solicitud: {solicitud.codigo}")
        print(f"🧪 Usuario creador: {solicitud.creada_por.username} ({solicitud.creada_por.email})")
        
        # Probar el envío del correo
        try:
            enviar_correo_apc_completado(solicitud)
            
            return JsonResponse({
                'success': True,
                'message': f'Test de correo APC completado enviado para solicitud {solicitud.codigo}',
                'details': {
                    'solicitud_codigo': solicitud.codigo,
                    'usuario_destinatario': solicitud.creada_por.username,
                    'email_destinatario': solicitud.creada_por.email,
                    'cliente_nombre': solicitud.cliente_nombre_completo or 'Sin cliente'
                }
            })
            
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'error': f'Error al enviar correo de test: {str(e)}',
                'traceback': traceback.format_exc()
            })
    
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'Error en test: {str(e)}',
            'traceback': traceback.format_exc()
        })


@login_required
def test_apc_iniciado_email(request):
    """
    Vista para probar el envío de correo de APC iniciado (in_progress)
    Solo para testing - eliminar en producción
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        # Buscar una solicitud con APC habilitado para testing
        solicitud = Solicitud.objects.filter(descargar_apc_makito=True).first()
        
        if not solicitud:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró ninguna solicitud con APC habilitado para testing'
            })
        
        # Simular que se inició el proceso APC
        from django.utils import timezone
        solicitud.apc_status = 'in_progress'
        solicitud.apc_fecha_inicio = timezone.now()
        solicitud.apc_observaciones = 'Proceso APC iniciado - TEST'
        
        # No guardar en la base de datos, solo simular
        
        print(f"🧪 Testing envío de correo APC iniciado para solicitud: {solicitud.codigo}")
        print(f"🧪 Usuario creador: {solicitud.creada_por.username} ({solicitud.creada_por.email})")
        
        # Probar el envío del correo
        try:
            enviar_correo_apc_iniciado(solicitud)
            
            return JsonResponse({
                'success': True,
                'message': f'Test de correo APC iniciado enviado para solicitud {solicitud.codigo}',
                'details': {
                    'solicitud_codigo': solicitud.codigo,
                    'usuario_destinatario': solicitud.creada_por.username,
                    'email_destinatario': solicitud.creada_por.email,
                    'cliente_nombre': solicitud.cliente_nombre_completo or 'Sin cliente',
                    'status_simulado': 'in_progress'
                }
            })
            
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'error': f'Error al enviar correo de test: {str(e)}',
                'traceback': traceback.format_exc()
            })
    
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'Error en test: {str(e)}',
            'traceback': traceback.format_exc()
        })


@login_required
def test_sura_completado_email(request):
    """
    Vista para probar el envío de correo de SURA completado
    Solo para testing - eliminar en producción
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        # Buscar una solicitud con SURA habilitado para testing
        solicitud = Solicitud.objects.filter(cotizar_sura_makito=True).first()
        
        if not solicitud:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró ninguna solicitud con SURA habilitado para testing'
            })
        
        # Simular que se completó la cotización SURA
        from django.utils import timezone
        solicitud.sura_status = 'completed'
        solicitud.sura_fecha_completado = timezone.now()
        solicitud.sura_observaciones = 'Cotización SURA completada - TEST'
        
        # No guardar en la base de datos, solo simular
        
        print(f"🧪 Testing envío de correo SURA completado para solicitud: {solicitud.codigo}")
        print(f"🧪 Usuario creador: {solicitud.creada_por.username} ({solicitud.creada_por.email})")
        
        # Probar el envío del correo
        try:
            enviar_correo_sura_completado(solicitud)
            
            return JsonResponse({
                'success': True,
                'message': f'Test de correo SURA completado enviado para solicitud {solicitud.codigo}',
                'details': {
                    'solicitud_codigo': solicitud.codigo,
                    'usuario_destinatario': solicitud.creada_por.username,
                    'email_destinatario': solicitud.creada_por.email,
                    'cliente_nombre': solicitud.cliente_nombre_completo or 'Sin cliente'
                }
            })
            
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'error': f'Error al enviar correo de test: {str(e)}',
                'traceback': traceback.format_exc()
            })
    
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'Error en test: {str(e)}',
            'traceback': traceback.format_exc()
        })


@login_required
def test_sura_iniciado_email(request):
    """
    Vista para probar el envío de correo de SURA iniciado (in_progress)
    Solo para testing - eliminar en producción
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        # Buscar una solicitud con SURA habilitado para testing
        solicitud = Solicitud.objects.filter(cotizar_sura_makito=True).first()
        
        if not solicitud:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró ninguna solicitud con SURA habilitado para testing'
            })
        
        # Simular que se inició el proceso SURA
        from django.utils import timezone
        solicitud.sura_status = 'in_progress'
        solicitud.sura_fecha_inicio = timezone.now()
        solicitud.sura_observaciones = 'Proceso SURA iniciado - TEST'
        
        # No guardar en la base de datos, solo simular
        
        print(f"🧪 Testing envío de correo SURA iniciado para solicitud: {solicitud.codigo}")
        print(f"🧪 Usuario creador: {solicitud.creada_por.username} ({solicitud.creada_por.email})")
        
        # Probar el envío del correo
        try:
            enviar_correo_sura_iniciado(solicitud)
            
            return JsonResponse({
                'success': True,
                'message': f'Test de correo SURA iniciado enviado para solicitud {solicitud.codigo}',
                'details': {
                    'solicitud_codigo': solicitud.codigo,
                    'usuario_destinatario': solicitud.creada_por.username,
                    'email_destinatario': solicitud.creada_por.email,
                    'cliente_nombre': solicitud.cliente_nombre_completo or 'Sin cliente'
                }
            })
            
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'error': f'Error al enviar correo de test: {str(e)}',
                'traceback': traceback.format_exc()
            })
    
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'Error en test: {str(e)}',
            'traceback': traceback.format_exc()
        })


@login_required
def test_sura_error_email(request):
    """
    Vista para probar el envío de correo de SURA error
    Solo para testing - eliminar en producción
    """
    if not request.user.is_superuser:
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    try:
        # Buscar una solicitud con SURA habilitado para testing
        solicitud = Solicitud.objects.filter(cotizar_sura_makito=True).first()
        
        if not solicitud:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró ninguna solicitud con SURA habilitado para testing'
            })
        
        # Simular que hubo un error en el proceso SURA
        from django.utils import timezone
        solicitud.sura_status = 'error'
        solicitud.sura_observaciones = 'Error en cotización SURA - TEST'
        
        # No guardar en la base de datos, solo simular
        
        print(f"🧪 Testing envío de correo SURA error para solicitud: {solicitud.codigo}")
        print(f"🧪 Usuario creador: {solicitud.creada_por.username} ({solicitud.creada_por.email})")
        
        # Probar el envío del correo
        try:
            mensaje_error = "Error de prueba: No se pudo procesar la cotización debido a datos incompletos del vehículo"
            enviar_correo_sura_error(solicitud, mensaje_error)
            
            return JsonResponse({
                'success': True,
                'message': f'Test de correo SURA error enviado para solicitud {solicitud.codigo}',
                'details': {
                    'solicitud_codigo': solicitud.codigo,
                    'usuario_destinatario': solicitud.creada_por.username,
                    'email_destinatario': solicitud.creada_por.email,
                    'cliente_nombre': solicitud.cliente_nombre_completo or 'Sin cliente',
                    'mensaje_error': mensaje_error
                }
            })
            
        except Exception as e:
            import traceback
            return JsonResponse({
                'success': False,
                'error': f'Error al enviar correo de test: {str(e)}',
                'traceback': traceback.format_exc()
            })
    
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'error': f'Error en test: {str(e)}',
            'traceback': traceback.format_exc()
        })


@login_required
@require_http_methods(["GET"])
def api_apc_list(request):
    """
    API para obtener la lista de solicitudes APC con filtros
    """
    try:
        # Parámetros de filtro
        status_filter = request.GET.get('status', '')
        fecha_desde = request.GET.get('fecha_desde', '')
        fecha_hasta = request.GET.get('fecha_hasta', '')
        
        # Query base
        queryset = Solicitud.objects.filter(
            descargar_apc_makito=True
        ).select_related(
            'pipeline', 'creada_por', 'etapa_actual'
        )
        
        # Aplicar filtro de usuario si no es superuser
        if not request.user.is_superuser:
            queryset = queryset.filter(propietario=request.user)
        
        # Aplicar filtros
        if status_filter:
            queryset = queryset.filter(apc_status=status_filter)
        
        if fecha_desde:
            try:
                from datetime import datetime
                fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(apc_fecha_solicitud__date__gte=fecha_desde_obj)
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                from datetime import datetime
                fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(apc_fecha_solicitud__date__lte=fecha_hasta_obj)
            except ValueError:
                pass
        
        # Ordenar por fecha de solicitud más reciente
        queryset = queryset.order_by('-apc_fecha_solicitud')
        
        # Construir respuesta
        data = []
        for solicitud in queryset:
            data.append({
                'codigo': solicitud.codigo,
                'cliente_nombre': solicitud.cliente_nombre_completo or 'Sin cliente',
                'apc_tipo_documento': solicitud.get_apc_tipo_documento_display() if solicitud.apc_tipo_documento else '',
                'apc_no_cedula': solicitud.apc_no_cedula,
                'apc_status': solicitud.apc_status,
                'apc_status_display': solicitud.get_apc_status_display(),
                'pipeline': solicitud.pipeline.nombre,
                'creada_por': solicitud.creada_por.get_full_name() or solicitud.creada_por.username,
                'creada_por_email': solicitud.creada_por.email,
                'propietario': solicitud.propietario.get_full_name() or solicitud.propietario.username if solicitud.propietario else '',
                'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin etapa',
                'fecha_creacion': solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'apc_fecha_solicitud': solicitud.apc_fecha_solicitud.strftime('%d/%m/%Y %H:%M') if solicitud.apc_fecha_solicitud else '',
                'apc_fecha_inicio': solicitud.apc_fecha_inicio.strftime('%d/%m/%Y %H:%M') if solicitud.apc_fecha_inicio else '',
                'apc_fecha_completado': solicitud.apc_fecha_completado.strftime('%d/%m/%Y %H:%M') if solicitud.apc_fecha_completado else '',
                'apc_observaciones': solicitud.apc_observaciones or '',
                'apc_archivo_url': solicitud.apc_archivo.url if solicitud.apc_archivo else None,
                'apc_archivo_disponible': bool(solicitud.apc_archivo),
                'url_detail': f'/workflow/solicitud/{solicitud.id}/'
            })
        
        return JsonResponse({
            'success': True,
            'total': len(data),
            'solicitudes': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener lista APC: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_apc_detail(request, solicitud_codigo):
    """
    API para obtener detalles completos de una solicitud APC específica
    """
    try:
        # Buscar la solicitud por código
        solicitud = Solicitud.objects.filter(
            codigo=solicitud_codigo,
            descargar_apc_makito=True
        ).select_related(
            'pipeline', 'creada_por', 'etapa_actual'
        ).first()
        
        if not solicitud:
            return JsonResponse({
                'success': False,
                'error': f'Solicitud con código {solicitud_codigo} no encontrada'
            }, status=404)
        
        # Verificar permisos si no es superuser
        if not request.user.is_superuser and solicitud.propietario != request.user:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para ver esta solicitud'
            }, status=403)
        
        # Construir respuesta detallada
        data = {
            'codigo': solicitud.codigo,
            'cliente_nombre': solicitud.cliente_nombre_completo or 'Sin cliente',
            'apc_tipo_documento': solicitud.get_apc_tipo_documento_display() if solicitud.apc_tipo_documento else '',
            'apc_no_cedula': solicitud.apc_no_cedula,
            'apc_status': solicitud.apc_status,
            'apc_status_display': solicitud.get_apc_status_display(),
            'pipeline': solicitud.pipeline.nombre,
            'creada_por': solicitud.creada_por.get_full_name() or solicitud.creada_por.username,
            'creada_por_email': solicitud.creada_por.email,
            'propietario': solicitud.propietario.get_full_name() or solicitud.propietario.username if solicitud.propietario else '',
            'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin etapa',
            'fecha_creacion': solicitud.fecha_creacion.isoformat(),
            'apc_fecha_solicitud': solicitud.apc_fecha_solicitud.isoformat() if solicitud.apc_fecha_solicitud else None,
            'apc_fecha_inicio': solicitud.apc_fecha_inicio.isoformat() if solicitud.apc_fecha_inicio else None,
            'apc_fecha_completado': solicitud.apc_fecha_completado.isoformat() if solicitud.apc_fecha_completado else None,
            'apc_observaciones': solicitud.apc_observaciones or '',
            'apc_archivo_url': solicitud.apc_archivo.url if solicitud.apc_archivo else None,
            'apc_archivo_disponible': bool(solicitud.apc_archivo),
            'apc_archivo_nombre': solicitud.apc_archivo.name.split('/')[-1] if solicitud.apc_archivo else None,
        }
        
        return JsonResponse({
            'success': True,
            'solicitud': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener detalles APC: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_sura_list(request):
    """
    API para obtener la lista de solicitudes SURA con filtros
    """
    try:
        # Parámetros de filtro
        status_filter = request.GET.get('status', '')
        fecha_desde = request.GET.get('fecha_desde', '')
        fecha_hasta = request.GET.get('fecha_hasta', '')
        
        # Query base
        queryset = Solicitud.objects.filter(
            cotizar_sura_makito=True
        ).select_related(
            'pipeline', 'creada_por', 'etapa_actual'
        )
        
        # Aplicar filtro de usuario si no es superuser
        if not request.user.is_superuser:
            queryset = queryset.filter(propietario=request.user)
        
        # Aplicar filtros
        if status_filter:
            queryset = queryset.filter(sura_status=status_filter)
        
        if fecha_desde:
            try:
                from datetime import datetime
                fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(sura_fecha_solicitud__date__gte=fecha_desde_obj)
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                from datetime import datetime
                fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(sura_fecha_solicitud__date__lte=fecha_hasta_obj)
            except ValueError:
                pass
        
        # Ordenar por fecha de solicitud más reciente
        queryset = queryset.order_by('-sura_fecha_solicitud')
        
        # Construir respuesta
        data = []
        for solicitud in queryset:
            data.append({
                'codigo': solicitud.codigo,
                'cliente_nombre': solicitud.cliente_nombre_completo or 'Sin cliente',
                'sura_primer_nombre': solicitud.sura_primer_nombre or '',
                'sura_primer_apellido': solicitud.sura_primer_apellido or '',
                'sura_no_documento': solicitud.sura_no_documento or '',
                'sura_status': solicitud.sura_status,
                'sura_status_display': solicitud.get_sura_status_display(),
                'pipeline': solicitud.pipeline.nombre,
                'creada_por': solicitud.creada_por.get_full_name() or solicitud.creada_por.username,
                'creada_por_email': solicitud.creada_por.email,
                'propietario': solicitud.propietario.get_full_name() or solicitud.propietario.username if solicitud.propietario else '',
                'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin etapa',
                'fecha_creacion': solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                'sura_fecha_solicitud': solicitud.sura_fecha_solicitud.strftime('%d/%m/%Y %H:%M') if solicitud.sura_fecha_solicitud else '',
                'sura_fecha_inicio': solicitud.sura_fecha_inicio.strftime('%d/%m/%Y %H:%M') if solicitud.sura_fecha_inicio else '',
                'sura_fecha_completado': solicitud.sura_fecha_completado.strftime('%d/%m/%Y %H:%M') if solicitud.sura_fecha_completado else '',
                'sura_observaciones': solicitud.sura_observaciones or '',
                'sura_archivo_url': solicitud.sura_archivo.url if solicitud.sura_archivo else None,
                'sura_archivo_disponible': bool(solicitud.sura_archivo),
                'url_detail': f'/workflow/solicitud/{solicitud.id}/'
            })
        
        return JsonResponse({
            'success': True,
            'total': len(data),
            'solicitudes': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener lista SURA: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_sura_detail(request, solicitud_codigo):
    """
    API para obtener detalles completos de una solicitud SURA específica
    """
    try:
        # Buscar la solicitud por código
        solicitud = Solicitud.objects.filter(
            codigo=solicitud_codigo,
            cotizar_sura_makito=True
        ).select_related(
            'pipeline', 'creada_por', 'etapa_actual'
        ).first()
        
        if not solicitud:
            return JsonResponse({
                'success': False,
                'error': f'Solicitud con código {solicitud_codigo} no encontrada'
            }, status=404)
        
        # Verificar permisos si no es superuser
        if not request.user.is_superuser and solicitud.propietario != request.user:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para ver esta solicitud'
            }, status=403)
        
        # Construir respuesta detallada
        data = {
            'codigo': solicitud.codigo,
            'cliente_nombre': solicitud.cliente_nombre_completo or 'Sin cliente',
            'sura_primer_nombre': solicitud.sura_primer_nombre or '',
            'sura_primer_apellido': solicitud.sura_primer_apellido or '',
            'sura_no_documento': solicitud.sura_no_documento or '',
            'sura_status': solicitud.sura_status,
            'sura_status_display': solicitud.get_sura_status_display(),
            'pipeline': solicitud.pipeline.nombre,
            'creada_por': solicitud.creada_por.get_full_name() or solicitud.creada_por.username,
            'creada_por_email': solicitud.creada_por.email,
            'propietario': solicitud.propietario.get_full_name() or solicitud.propietario.username if solicitud.propietario else '',
            'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin etapa',
            'fecha_creacion': solicitud.fecha_creacion.isoformat(),
            'sura_fecha_solicitud': solicitud.sura_fecha_solicitud.isoformat() if solicitud.sura_fecha_solicitud else None,
            'sura_fecha_inicio': solicitud.sura_fecha_inicio.isoformat() if solicitud.sura_fecha_inicio else None,
            'sura_fecha_completado': solicitud.sura_fecha_completado.isoformat() if solicitud.sura_fecha_completado else None,
            'sura_observaciones': solicitud.sura_observaciones or '',
            'sura_archivo_url': solicitud.sura_archivo.url if solicitud.sura_archivo else None,
            'sura_archivo_disponible': bool(solicitud.sura_archivo),
            'sura_archivo_nombre': solicitud.sura_archivo.name.split('/')[-1] if solicitud.sura_archivo else None,
        }
        
        return JsonResponse({
            'success': True,
            'solicitud': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener detalles SURA: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_check_apc_status(request, solicitud_id):
    """
    API para verificar el estado APC de una solicitud por ID
    """
    try:
        # Buscar la solicitud por ID
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar si la solicitud tiene APC habilitado
        if not solicitud.descargar_apc_makito:
            return JsonResponse({
                'success': False,
                'error': 'APC no está habilitado para esta solicitud'
            }, status=400)
        
        # Construir respuesta con información del estado APC
        data = {
            'solicitud_id': solicitud.id,
            'codigo': solicitud.codigo,
            'apc_status': solicitud.apc_status,
            'apc_status_display': solicitud.get_apc_status_display(),
            'apc_fecha_solicitud': solicitud.apc_fecha_solicitud.isoformat() if solicitud.apc_fecha_solicitud else None,
            'apc_fecha_inicio': solicitud.apc_fecha_inicio.isoformat() if solicitud.apc_fecha_inicio else None,
            'apc_fecha_completado': solicitud.apc_fecha_completado.isoformat() if solicitud.apc_fecha_completado else None,
            'apc_observaciones': solicitud.apc_observaciones or '',
            'apc_archivo_disponible': bool(solicitud.apc_archivo),
        }
        
        return JsonResponse({
            'success': True,
            'apc_status': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al verificar estado APC: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_check_sura_status(request, solicitud_id):
    """
    API para verificar el estado SURA de una solicitud por ID
    """
    try:
        # Buscar la solicitud por ID
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar si la solicitud tiene SURA habilitado
        if not solicitud.cotizar_sura_makito:
            return JsonResponse({
                'success': False,
                'error': 'SURA no está habilitado para esta solicitud'
            }, status=400)
        
        # Construir respuesta con información del estado SURA
        data = {
            'solicitud_id': solicitud.id,
            'codigo': solicitud.codigo,
            'sura_status': solicitud.sura_status,
            'sura_status_display': solicitud.get_sura_status_display(),
            'sura_fecha_solicitud': solicitud.sura_fecha_solicitud.isoformat() if solicitud.sura_fecha_solicitud else None,
            'sura_fecha_inicio': solicitud.sura_fecha_inicio.isoformat() if solicitud.sura_fecha_inicio else None,
            'sura_fecha_completado': solicitud.sura_fecha_completado.isoformat() if solicitud.sura_fecha_completado else None,
            'sura_observaciones': solicitud.sura_observaciones or '',
            'sura_archivo_disponible': bool(solicitud.sura_archivo),
        }
        
        return JsonResponse({
            'success': True,
            'sura_status': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al verificar estado SURA: {str(e)}'
        }, status=500)


# ==========================================
# APIs PARA CANAL DIGITAL
# ==========================================

@login_required
def api_obtener_pipelines_canal_digital(request):
    """API para obtener pipelines disponibles para el Canal Digital"""
    try:
        from .modelsWorkflow import Pipeline
        
        pipelines = Pipeline.objects.all()
        pipelines_data = []
        
        for pipeline in pipelines:
            pipelines_data.append({
                'id': pipeline.id,
                'nombre': pipeline.nombre,
                'descripcion': pipeline.descripcion or '',
                'etapas': [
                    {
                        'id': etapa.id,
                        'nombre': etapa.nombre,
                        'orden': etapa.orden
                    }
                    for etapa in pipeline.etapas.all().order_by('orden')
                ]
            })
        
        return JsonResponse({
            'success': True,
            'pipelines': pipelines_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def api_obtener_etapas_pipeline(request, pipeline_id):
    """API para obtener etapas de un pipeline específico"""
    try:
        from .modelsWorkflow import Pipeline
        
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        etapas = pipeline.etapas.all().order_by('orden')
        
        etapas_data = []
        for etapa in etapas:
            etapas_data.append({
                'id': etapa.id,
                'nombre': etapa.nombre,
                'orden': etapa.orden,
                'sla_horas': etapa.sla_horas if etapa.sla else None
            })
        
        return JsonResponse({
            'success': True,
            'pipeline': {
                'id': pipeline.id,
                'nombre': pipeline.nombre
            },
            'etapas': etapas_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def api_guardar_configuracion_canal_digital(request):
    """API para guardar la configuración del Canal Digital"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    
    try:
        from .modelsWorkflow import ConfiguracionCanalDigital, Pipeline, Etapa
        import json
        
        data = json.loads(request.body)
        pipeline_id = data.get('pipeline_id')
        etapa_id = data.get('etapa_id')
        
        if not pipeline_id:
            return JsonResponse({'success': False, 'error': 'Pipeline requerido'})
        
        pipeline = get_object_or_404(Pipeline, id=pipeline_id)
        
        # Desactivar configuraciones anteriores
        ConfiguracionCanalDigital.objects.filter(activo=True).update(activo=False)
        
        # Crear nueva configuración
        configuracion = ConfiguracionCanalDigital()
        configuracion.pipeline_por_defecto = pipeline
        
        if etapa_id:
            etapa = get_object_or_404(Etapa, id=etapa_id, pipeline=pipeline)
            configuracion.etapa_por_defecto = etapa
        else:
            # Usar primera etapa del pipeline
            configuracion.etapa_por_defecto = pipeline.etapas.first()
        
        configuracion.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Configuración guardada: {pipeline.nombre} - {configuracion.etapa_por_defecto.nombre}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def api_obtener_configuracion_canal_digital(request):
    """API para obtener la configuración actual del Canal Digital"""
    try:
        from .modelsWorkflow import ConfiguracionCanalDigital
        
        configuracion = ConfiguracionCanalDigital.get_configuracion_activa()
        
        if configuracion:
            return JsonResponse({
                'success': True,
                'configuracion': {
                    'id': configuracion.id,
                    'pipeline_id': configuracion.pipeline_por_defecto.id,
                    'pipeline_nombre': configuracion.pipeline_por_defecto.nombre,
                    'etapa_id': configuracion.etapa_por_defecto.id,
                    'etapa_nombre': configuracion.etapa_por_defecto.nombre
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'configuracion': None
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@csrf_exempt
def api_asignar_propietario_formulario(request):
    """API para asignar propietario a un formulario del canal digital"""
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        })
    
    try:
        import json
        from .models import FormularioWeb
        from django.contrib.auth.models import User, Group
        
        data = json.loads(request.body)
        formulario_id = data.get('formulario_id')
        propietario_id = data.get('propietario_id')
        
        # Validar formulario
        formulario = get_object_or_404(FormularioWeb, id=formulario_id)
        
        # Si propietario_id es None o vacío, desasignar
        if not propietario_id:
            formulario.propietario = None
            propietario_nombre = "Sin asignar"
        else:
            # Validar propietario
            propietario = get_object_or_404(User, id=propietario_id, is_active=True)
            
            # Verificar que el propietario esté en el grupo "Canal Digital"
            try:
                grupo_canal_digital = Group.objects.get(name="Canal Digital")
                if not propietario.groups.filter(id=grupo_canal_digital.id).exists():
                    return JsonResponse({
                        'success': False,
                        'error': f'El usuario {propietario.get_full_name() or propietario.username} no pertenece al grupo "Canal Digital"'
                    })
            except Group.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'El grupo "Canal Digital" no existe. Contacte al administrador.'
                })
            
            formulario.propietario = propietario
            propietario_nombre = propietario.get_full_name() or propietario.username
        
        formulario.save()
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Propietario {"asignado" if propietario_id else "removido"} correctamente',
            'propietario_nombre': propietario_nombre
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


# =====================================================
# APIS PARA AVANZAR SUBESTADOS Y TRANSICIONES
# =====================================================

@login_required
def api_subestados_disponibles(request, solicitud_id):
    """API para obtener los subestados disponibles para una solicitud (secuencial)"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Debug logging
        print(f"DEBUG: Obteniendo subestados para solicitud {solicitud_id}")
        print(f"DEBUG: Solicitud subestado_actual: {solicitud.subestado_actual}")
        print(f"DEBUG: Solicitud etapa_actual: {solicitud.etapa_actual}")
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser or
                request.user.is_staff):
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para ver esta solicitud.'
            })
        
        # Obtener todos los subestados de la etapa actual
        if not solicitud.etapa_actual:
            return JsonResponse({
                'success': False,
                'message': 'La solicitud no tiene etapa actual asignada.'
            })
        
        # Asegurar que la solicitud tenga un subestado_actual asignado
        if not solicitud.subestado_actual:
            primer_subestado = solicitud.etapa_actual.subestados.order_by('orden').first()
            if primer_subestado:
                solicitud.subestado_actual = primer_subestado
                solicitud.save()
                print(f"DEBUG: Auto-asignado primer subestado: {primer_subestado.nombre}")
        
        todos_subestados = solicitud.etapa_actual.subestados.all().order_by('orden')
        subestado_actual_orden = solicitud.subestado_actual.orden if solicitud.subestado_actual else 0
        
        print(f"DEBUG: Subestado actual orden: {subestado_actual_orden}")
        
        subestados_data = []
        for subestado in todos_subestados:
            # Determinar disponibilidad basada en nueva lógica unidireccional
            es_actual = subestado.id == (solicitud.subestado_actual.id if solicitud.subestado_actual else None)
            
            # NUEVA LÓGICA:
            # - Subestados anteriores (completados): siempre disponibles para navegación
            # - Subestado siguiente: disponible para avance
            # - Subestados más lejanos: bloqueados
            es_completado = subestado.orden < subestado_actual_orden  # Navegación libre hacia atrás
            puede_avanzar = subestado.orden == subestado_actual_orden + 1  # Solo el siguiente para avanzar
            esta_bloqueado = subestado.orden > subestado_actual_orden + 1  # Saltos hacia adelante bloqueados
            
            print(f"DEBUG: Subestado {subestado.nombre} - orden: {subestado.orden}, es_actual: {es_actual}, es_completado: {es_completado}, puede_avanzar: {puede_avanzar}, esta_bloqueado: {esta_bloqueado}")
            
            # Determinar el motivo de bloqueo
            razon_bloqueado = None
            if esta_bloqueado:
                razon_bloqueado = f'No puede avanzar más allá del siguiente subestado (orden {subestado_actual_orden + 1})'
            
            subestados_data.append({
                'id': subestado.id,
                'nombre': subestado.nombre,
                'orden': subestado.orden,
                'es_actual': es_actual,
                'es_completado': es_completado,
                'puede_avanzar': puede_avanzar,
                'esta_bloqueado': esta_bloqueado,
                'razon_bloqueado': razon_bloqueado
            })
        
        subestado_actual_id = solicitud.subestado_actual.id if solicitud.subestado_actual else None
        
        print(f"DEBUG: Subestados procesados: {len(subestados_data)}")
        print(f"DEBUG: Subestado actual ID: {subestado_actual_id}")
        
        return JsonResponse({
            'success': True,
            'subestados': subestados_data,
            'subestado_actual_id': subestado_actual_id,
            'validacion_secuencial': True,
            'navegacion_libre_atras': True,  # Nueva propiedad para indicar navegación libre hacia atrás
            'bloqueo_solo_avance': True      # Nueva propiedad para indicar que solo se bloquea avance
        })
        
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener subestados: {str(e)}'
        })


@login_required
def api_transiciones_disponibles(request, solicitud_id):
    """API para obtener las transiciones disponibles para una solicitud"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser or
                request.user.is_staff):
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para ver esta solicitud.'
            })
        
        # Obtener todas las transiciones desde la etapa actual
        if not solicitud.etapa_actual:
            return JsonResponse({
                'success': False,
                'message': 'La solicitud no tiene etapa actual asignada.'
            })
        
        transiciones = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=solicitud.etapa_actual
        )
        
        transiciones_data = []
        for transicion in transiciones:
            transiciones_data.append({
                'id': transicion.id,
                'nombre': transicion.nombre,
                'etapa_origen': transicion.etapa_origen.nombre,
                'etapa_destino': transicion.etapa_destino.nombre,
                'requiere_permiso': transicion.requiere_permiso
            })
        
        return JsonResponse({
            'success': True,
            'transiciones': transiciones_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener transiciones: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def api_avanzar_subestado(request):
    """API para avanzar al siguiente subestado con validación secuencial"""
    import json
    
    try:
        data = json.loads(request.body)
        solicitud_id = data.get('solicitud_id')
        subestado_id = data.get('subestado_id')
        
        print(f"DEBUG: Avanzando subestado - solicitud_id: {solicitud_id}, subestado_id: {subestado_id}")
        
        if not solicitud_id or not subestado_id:
            return JsonResponse({
                'success': False,
                'message': 'Faltan parámetros requeridos.'
            })
        
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        subestado_destino = get_object_or_404(SubEstado, id=subestado_id)
        
        print(f"DEBUG: Solicitud encontrada: {solicitud.codigo}")
        print(f"DEBUG: Subestado destino: {subestado_destino.nombre}")
        print(f"DEBUG: Subestado actual antes del cambio: {solicitud.subestado_actual}")
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser or
                request.user.is_staff):
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para modificar esta solicitud.'
            })
        
        # Verificar que el subestado pertenece a la etapa actual
        if subestado_destino.etapa != solicitud.etapa_actual:
            return JsonResponse({
                'success': False,
                'message': 'El subestado no pertenece a la etapa actual.'
            })
        
        # Asegurar que la solicitud tenga un subestado_actual asignado
        if not solicitud.subestado_actual:
            primer_subestado = solicitud.etapa_actual.subestados.order_by('orden').first()
            if primer_subestado:
                solicitud.subestado_actual = primer_subestado
                solicitud.save()
                print(f"DEBUG: Auto-asignado primer subestado: {primer_subestado.nombre}")
        
        # VALIDACIÓN SECUENCIAL UNIDIRECCIONAL: 
        # - Permitir retroceder a cualquier subestado anterior (completado)
        # - Solo permitir avanzar al siguiente subestado en orden
        subestado_actual_orden = solicitud.subestado_actual.orden if solicitud.subestado_actual else 0
        subestado_destino_orden = subestado_destino.orden
        
        print(f"DEBUG: Orden actual: {subestado_actual_orden}, Orden destino: {subestado_destino_orden}")
        
        # Permitir permanecer en el mismo subestado (refresh)
        if subestado_destino_orden == subestado_actual_orden:
            return JsonResponse({
                'success': False,
                'message': 'Ya te encuentras en este subestado.'
            })
        
        # NAVEGACIÓN HACIA ATRÁS: Permitir retroceder a subestados anteriores (completados)
        elif subestado_destino_orden < subestado_actual_orden:
            print(f"DEBUG: Navegación hacia atrás permitida - de orden {subestado_actual_orden} a orden {subestado_destino_orden}")
            # No hay validación adicional para retrocesos - siempre permitidos
        
        # NAVEGACIÓN HACIA ADELANTE: Solo permitir avanzar al siguiente subestado
        elif subestado_destino_orden > subestado_actual_orden:
            if subestado_destino_orden != subestado_actual_orden + 1:
                return JsonResponse({
                    'success': False,
                    'message': f'No puede avanzar más allá del siguiente subestado. Solo puede avanzar al subestado de orden {subestado_actual_orden + 1}.'
                })
            print(f"DEBUG: Avance secuencial permitido - de orden {subestado_actual_orden} a orden {subestado_destino_orden}")
        
        # Si llegamos aquí, la validación es correcta (avance secuencial o retroceso permitido)
        action_type = "retrocediendo" if subestado_destino_orden < subestado_actual_orden else "avanzando"
        print(f"DEBUG: Validación aprobada. {action_type} de orden {subestado_actual_orden} a {subestado_destino_orden}")
        
        # Actualizar el subestado actual
        solicitud.subestado_actual = subestado_destino
        solicitud.save()
        
        print(f"DEBUG: Subestado actualizado exitosamente a: {subestado_destino.nombre}")
        
        # Actualizar el historial si existe una entrada activa
        historial_actual = HistorialSolicitud.objects.filter(
            solicitud=solicitud,
            fecha_fin__isnull=True
        ).first()
        
        if historial_actual:
            historial_actual.subestado = subestado_destino
            historial_actual.save()
            print(f"DEBUG: Historial actualizado también")
        
        return JsonResponse({
            'success': True,
            'message': f'Navegación exitosa a: {subestado_destino.nombre}',
            'nuevo_subestado': {
                'id': subestado_destino.id,
                'nombre': subestado_destino.nombre,
                'orden': subestado_destino.orden
            },
            'accion': action_type
        })
        
    except Exception as e:
        print(f"DEBUG ERROR en api_avanzar_subestado: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error al avanzar subestado: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def api_ejecutar_transicion(request):
    """API para ejecutar una transición a otra etapa"""
    import json
    
    try:
        data = json.loads(request.body)
        solicitud_id = data.get('solicitud_id')
        transicion_id = data.get('transicion_id')
        motivo = data.get('motivo', '')  # ✅ NUEVO: Obtener motivo de devolución
        
        if not solicitud_id or not transicion_id:
            return JsonResponse({
                'success': False,
                'message': 'Faltan parámetros requeridos.'
            })
        
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        transicion = get_object_or_404(TransicionEtapa, id=transicion_id)
        
        # Verificar permisos (incluye supervisores de grupo)
        if not usuario_puede_modificar_solicitud(request.user, solicitud):
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para modificar esta solicitud.'
            })
        
        # Verificar que la transición es válida
        if transicion.etapa_origen != solicitud.etapa_actual:
            return JsonResponse({
                'success': False,
                'message': 'La transición no es válida para la etapa actual.'
            })
        
        # Verificar permisos de transición si es requerido
        if transicion.requiere_permiso:
            # Aquí podrías agregar lógica adicional de permisos
            pass
        
        # ✅ NUEVO: Registrar devolución en historial si viene desde Back Office
        if (solicitud.etapa_actual and 
            solicitud.etapa_actual.nombre == "Back Office" and
            transicion.etapa_origen.nombre == "Back Office"):
            
            # Importar función de registro
            from .signals_backoffice import registrar_devolucion_manual
            
            # Registrar la devolución en el historial
            registrar_devolucion_manual(
                solicitud=solicitud,
                usuario=request.user,
                motivo=motivo or "Devolución desde Back Office",
                etapa_destino=transicion.etapa_destino
            )
        
        # Cerrar el historial actual
        historial_actual = HistorialSolicitud.objects.filter(
            solicitud=solicitud,
            fecha_fin__isnull=True
        ).first()
        
        if historial_actual:
            historial_actual.fecha_fin = timezone.now()
            historial_actual.save()
        
        # Actualizar la solicitud
        solicitud.etapa_actual = transicion.etapa_destino
        # Resetear subestado al primer subestado de la nueva etapa
        primer_subestado = transicion.etapa_destino.subestados.order_by('orden').first()
        solicitud.subestado_actual = primer_subestado
        
        # ✅ NUEVO: Auto-asignar calificación 'pendiente' cuando llega a Back Office
        if transicion.etapa_destino.nombre == 'Back Office' and not solicitud.calificaciondocumentobackoffice:
            solicitud.calificaciondocumentobackoffice = 'pendiente'
            print(f"🔄 Auto-asignado calificaciondocumentobackoffice='pendiente' para solicitud {solicitud.codigo}")
            
            # ✅ NUEVO: También crear calificaciones individuales de documentos al llegar a Back Office
            usuario_calificador = request.user  # El usuario que está haciendo la transición
            crear_calificaciones_pendientes_backoffice(solicitud, usuario_calificador)
            print(f"✅ Calificaciones de documentos creadas al llegar a Back Office para solicitud {solicitud.codigo}")
        
        solicitud.save()
        
        # Crear nuevo historial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=transicion.etapa_destino,
            subestado=primer_subestado,
            usuario_responsable=request.user,
            fecha_inicio=timezone.now()
        )
        
        # Determinar URL de redirección
        if transicion.etapa_destino.nombre == 'Back Office' and transicion.etapa_destino.es_bandeja_grupal:
            redirect_url = f'/workflow/solicitudes/{solicitud.id}/backoffice/'
        else:
            redirect_url = f'/workflow/solicitudes/{solicitud.id}/detalle/'
        
        return JsonResponse({
            'success': True,
            'message': f'Transición ejecutada: {transicion.nombre}',
            'redirect_url': redirect_url
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al ejecutar transición: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def api_devolver_bandeja_grupal(request):
    """API para devolver una solicitud a la bandeja grupal"""
    import json
    
    try:
        data = json.loads(request.body)
        solicitud_id = data.get('solicitud_id')
        
        if not solicitud_id:
            return JsonResponse({
                'success': False,
                'message': 'ID de solicitud requerido.'
            })
        
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos - solo el usuario asignado o con permisos especiales puede devolver
        if not (solicitud.asignada_a == request.user or 
                request.user.is_superuser or
                request.user.is_staff):
            return JsonResponse({
                'success': False,
                'message': 'Solo puedes devolver solicitudes que están asignadas a ti.'
            })
        
        # Verificar que la solicitud está en una etapa que permite devolución a bandeja grupal
        if not solicitud.etapa_actual or not solicitud.etapa_actual.es_bandeja_grupal:
            return JsonResponse({
                'success': False,
                'message': 'Esta etapa no permite devolución a bandeja grupal.'
            })
        
        # Verificar que la solicitud está actualmente asignada (no en bandeja grupal)
        if not solicitud.asignada_a:
            return JsonResponse({
                'success': False,
                'message': 'La solicitud ya está en bandeja grupal.'
            })
        
        # Crear registro en el historial antes de cambiar la asignación
        comentario_devolucion = f"Solicitud devuelta a bandeja grupal por {request.user.get_full_name() or request.user.username}"
        
        # Actualizar la solicitud - remover asignación para que vuelva a bandeja grupal
        usuario_anterior = solicitud.asignada_a
        solicitud.asignada_a = None  # Esto la devuelve a bandeja grupal
        solicitud.save()
        
        # Crear comentario de sistema
        SolicitudComentario.objects.create(
            solicitud=solicitud,
            usuario=request.user,
            comentario=f"📤 Solicitud devuelta a bandeja grupal. Ahora está disponible para que otros usuarios la tomen y continúen con el subestado: {solicitud.subestado_actual.nombre if solicitud.subestado_actual else 'Sin subestado'}",
            es_sistema=True,
            etapa=solicitud.etapa_actual,
            subestado=solicitud.subestado_actual
        )
        
        # Determinar URL de redirección
        redirect_url = '/workflow/bandeja-grupal/'
        
        return JsonResponse({
            'success': True,
            'message': f'Solicitud devuelta a bandeja grupal exitosamente. Ahora otros usuarios pueden tomarla y continuar con el proceso.',
            'redirect_url': redirect_url,
            'data': {
                'usuario_anterior': usuario_anterior.get_full_name() if usuario_anterior else None,
                'etapa_actual': solicitud.etapa_actual.nombre if solicitud.etapa_actual else None,
                'subestado_actual': solicitud.subestado_actual.nombre if solicitud.subestado_actual else None,
                'fecha_devolucion': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error al devolver solicitud a bandeja grupal: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def api_devolver_solicitud_backoffice(request):
    """
    🚨 NUEVA API: Devolver solicitud desde Back Office a etapa anterior con envío de correo
    """
    import json
    from workflow.models import CalificacionDocumentoBackoffice
    
    try:
        data = json.loads(request.body)
        solicitud_id = data.get('solicitud_id')
        transicion_id = data.get('transicion_id')
        motivo = data.get('motivo', '').strip()
        
        if not solicitud_id or not transicion_id:
            return JsonResponse({
                'success': False,
                'message': 'Faltan parámetros requeridos (solicitud_id, transicion_id).'
            }, status=400)
        
        if not motivo:
            return JsonResponse({
                'success': False,
                'message': 'El motivo de devolución es obligatorio.'
            }, status=400)
        
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        transicion = get_object_or_404(TransicionEtapa, id=transicion_id)
        
        # Verificar que estamos en Back Office
        if not solicitud.etapa_actual or solicitud.etapa_actual.nombre != "Back Office":
            return JsonResponse({
                'success': False,
                'message': 'Esta función solo está disponible desde Back Office.'
            }, status=400)
        
        # Verificar que la transición es válida
        if transicion.pipeline != solicitud.pipeline or transicion.etapa_origen != solicitud.etapa_actual:
            return JsonResponse({
                'success': False,
                'message': 'Transición no válida para esta solicitud.'
            }, status=400)
        
        # 📊 OBTENER DOCUMENTOS PROBLEMÁTICOS DIRECTAMENTE DE LA BD
        documentos_problematicos = []
        
        print(f"🔍 Obteniendo documentos problemáticos para solicitud {solicitud.codigo}")
        
        # 1. ✅ DOCUMENTOS CALIFICADOS COMO "MALO" - CONSULTA DIRECTA
        calificaciones_malas = CalificacionDocumentoBackoffice.objects.filter(
            requisito_solicitud__solicitud_id=solicitud.id,  # Usar ID directo
            estado='malo'
        ).select_related('requisito_solicitud__requisito')
        
        print(f"📊 Documentos MALOS encontrados: {calificaciones_malas.count()}")
        
        for calificacion in calificaciones_malas:
            doc_malo = {
                'nombre': calificacion.requisito_solicitud.requisito.nombre,
                'estado': 'malo'
            }
            documentos_problematicos.append(doc_malo)
            print(f"   ❌ Malo: {doc_malo['nombre']}")
        
        # 2. ✅ DOCUMENTOS PENDIENTES - CONSULTA DIRECTA
        calificaciones_pendientes = CalificacionDocumentoBackoffice.objects.filter(
            requisito_solicitud__solicitud_id=solicitud.id,  # Usar ID directo
            estado='pendiente'
        ).select_related('requisito_solicitud__requisito')
        
        print(f"📊 Documentos PENDIENTES encontrados: {calificaciones_pendientes.count()}")
        
        for calificacion in calificaciones_pendientes:
            doc_pendiente = {
                'nombre': calificacion.requisito_solicitud.requisito.nombre,
                'estado': 'pendiente'
            }
            documentos_problematicos.append(doc_pendiente)
            print(f"   ⚠️ Pendiente: {doc_pendiente['nombre']}")
        
        print(f"📋 TOTAL documentos problemáticos para correo: {len(documentos_problematicos)}")
        
        # Guardar etapa anterior
        etapa_anterior = solicitud.etapa_actual
        
        # Cerrar historial actual
        historial_actual = HistorialSolicitud.objects.filter(
            solicitud=solicitud,
            fecha_fin__isnull=True
        ).first()
        
        if historial_actual:
            historial_actual.fecha_fin = timezone.now()
            historial_actual.save()
        
        # Actualizar la solicitud
        solicitud.etapa_actual = transicion.etapa_destino
        solicitud.subestado_actual = None  # Resetear subestado
        solicitud.asignada_a = None  # Liberar asignación
        
        # Limpiar campo de Back Office al salir
        solicitud.calificaciondocumentobackoffice = None
        
        solicitud.save()
        
        # Crear nuevo historial
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=transicion.etapa_destino,
            usuario_responsable=request.user,
            fecha_inicio=timezone.now()
        )
        
        # Crear comentario de devolución
        SolicitudComentario.objects.create(
            solicitud=solicitud,
            usuario=request.user,
            comentario=f"🚨 DEVOLUCIÓN desde {etapa_anterior.nombre}: {motivo}",
            tipo='sistema'
        )
        
        # 📧 ENVIAR CORREO AL PROPIETARIO
        try:
            enviar_correo_devolucion_backoffice(
                solicitud=solicitud,
                etapa_anterior=etapa_anterior,
                nueva_etapa=transicion.etapa_destino,
                documentos_problematicos=documentos_problematicos,
                motivo=motivo,
                usuario_que_devolvio=request.user,
                request=request
            )
        except Exception as e:
            print(f"⚠️ Error enviando correo de devolución: {e}")
            # No fallar la devolución por error en correo
        
        # Notificar cambio
        notify_solicitud_change(solicitud, 'devolucion_backoffice', request.user)
        
        return JsonResponse({
            'success': True,
            'message': f'Solicitud {solicitud.codigo} devuelta exitosamente a {transicion.etapa_destino.nombre}',
            'redirect_url': '/workflow/bandeja-mixta/',  # ✅ CORREGIDO: Redirigir a vista mixta
            'data': {
                'solicitud_codigo': solicitud.codigo,
                'etapa_anterior': etapa_anterior.nombre,
                'nueva_etapa': transicion.etapa_destino.nombre,
                'documentos_problematicos': len(documentos_problematicos),
                'fecha_devolucion': timezone.now().isoformat()
            }
        })
        
    except Exception as e:
        import traceback
        print(f"❌ Error en devolución desde Back Office: {str(e)}")
        print(f"❌ TRACEBACK: {traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': f'Error al devolver solicitud: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_obtener_calificaciones_por_estado(request, solicitud_id, estado):
    """
    🆕 API para obtener calificaciones de documentos por estado específico
    """
    try:
        print(f"📋 API llamada: solicitud_id={solicitud_id}, estado={estado}")
        
        # Verificar si la solicitud existe
        try:
            solicitud = get_object_or_404(Solicitud, id=solicitud_id)
            print(f"✅ Solicitud encontrada: {solicitud.codigo}")
        except Exception as e:
            print(f"❌ Solicitud no encontrada: {e}")
            return JsonResponse({
                'success': False,
                'message': f'Solicitud no encontrada: {str(e)}'
            }, status=404)
        
        # Verificar permisos básicos
        if not (solicitud.propietario == request.user or 
                solicitud.creada_por == request.user or
                solicitud.asignada_a == request.user or
                request.user.is_staff):
            print(f"❌ Sin permisos para usuario: {request.user.username}")
            return JsonResponse({
                'success': False,
                'message': 'No tienes permisos para ver esta solicitud.'
            }, status=403)
        
        print(f"✅ Permisos verificados para usuario: {request.user.username}")
        
        # Obtener calificaciones por estado - CONSULTA DIRECTA SIMPLE
        from workflow.models import CalificacionDocumentoBackoffice
        print(f"📊 Buscando calificaciones con estado: {estado} para solicitud {solicitud.codigo}")
        
        # Consulta simple y directa
        calificaciones = CalificacionDocumentoBackoffice.objects.filter(
            requisito_solicitud__solicitud_id=solicitud.id,
            estado=estado
        ).select_related('requisito_solicitud__requisito')
        
        # Debugging adicional
        total_calificaciones = CalificacionDocumentoBackoffice.objects.filter(
            requisito_solicitud__solicitud_id=solicitud.id
        ).count()
        
        print(f"📊 Total calificaciones en la solicitud: {total_calificaciones}")
        print(f"📊 Calificaciones con estado '{estado}': {calificaciones.count()}")
        
        # Mostrar todas las calificaciones para debugging
        todas = CalificacionDocumentoBackoffice.objects.filter(
            requisito_solicitud__solicitud_id=solicitud.id
        ).values('estado', 'requisito_solicitud__requisito__nombre')
        
        print(f"📋 TODAS las calificaciones:")
        for cal in todas:
            print(f"   - {cal['requisito_solicitud__requisito__nombre']}: {cal['estado']}")
        
        # ✅ CORREGIDO: Obtener información de obligatoriedad desde RequisitoTransicion (como en api_validar_documentos_backoffice)
        from workflow.modelsWorkflow import TransicionEtapa, RequisitoTransicion
        
        # Obtener transiciones de entrada hacia la etapa actual
        transiciones_entrada = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_destino=solicitud.etapa_actual
        ).prefetch_related('requisitos_obligatorios__requisito')
        
        # Obtener todos los requisitos definidos en RequisitoTransicion de entrada
        requisitos_definidos = {}
        for transicion in transiciones_entrada:
            for req_transicion in transicion.requisitos_obligatorios.all():
                req_id = req_transicion.requisito.id
                if req_id not in requisitos_definidos:
                    requisitos_definidos[req_id] = {
                        'requisito': req_transicion.requisito,
                        'obligatorio': req_transicion.obligatorio,
                        'mensaje_personalizado': req_transicion.mensaje_personalizado,
                        'transicion_origen': transicion.etapa_origen.nombre
                    }
        
        # Preparar datos
        calificaciones_data = []
        for calificacion in calificaciones:
            try:
                # Obtener información de obligatoriedad desde RequisitoTransicion
                req_id = calificacion.requisito_solicitud.requisito.id
                es_obligatorio = requisitos_definidos.get(req_id, {}).get('obligatorio', False)
                
                calificacion_data = {
                    'id': calificacion.id,
                    'estado': calificacion.estado,
                    'requisito_solicitud': {
                        'id': calificacion.requisito_solicitud.id,
                        'requisito': {
                            'id': calificacion.requisito_solicitud.requisito.id,
                            'nombre': calificacion.requisito_solicitud.requisito.nombre,
                            'obligatorio': es_obligatorio,  # ✅ Ahora obtenido correctamente
                        }
                    },
                    'observaciones': getattr(calificacion, 'observaciones', ''),  # Proteger contra campos faltantes
                    'fecha_calificacion': calificacion.fecha_calificacion.isoformat() if calificacion.fecha_calificacion else None,
                }
                calificaciones_data.append(calificacion_data)
                print(f"✅ Procesada calificación: {calificacion.id}")
            except Exception as e:
                print(f"❌ Error procesando calificación {calificacion.id}: {str(e)}")
                import traceback
                print(f"❌ TRACEBACK: {traceback.format_exc()}")
                continue
        
        resultado = {
            'success': True,
            'estado_filtrado': estado,
            'total': len(calificaciones_data),
            'calificaciones': calificaciones_data
        }
        
        print(f"✅ Devolviendo {len(calificaciones_data)} calificaciones")
        return JsonResponse(resultado)
        
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"❌ Error en api_obtener_calificaciones_por_estado: {str(e)}")
        print(f"❌ TRACEBACK: {error_traceback}")
        return JsonResponse({
            'success': False,
            'message': f'Error al obtener calificaciones: {str(e)}',
            'debug_traceback': error_traceback if settings.DEBUG else None
        }, status=500)





# ==========================================
# VISTAS PARA FORMULARIO GENERAL  
# ==========================================

@login_required
def buscar_entrevistas_api(request):
    """
    API para buscar entrevistas de clientes
    """
    try:
        if request.method != 'GET':
            return JsonResponse({'error': 'Método no permitido'}, status=405)
        
        # Obtener parámetros de búsqueda
        busqueda = request.GET.get('q', '').strip()
        
        # Construir query base
        query = ClienteEntrevista.objects.all().order_by('-fecha_entrevista')
        
        # Aplicar filtros si hay búsqueda
        if busqueda:
            query = query.filter(
                Q(primer_nombre__icontains=busqueda) | 
                Q(primer_apellido__icontains=busqueda) |
                Q(tomo_cedula__icontains=busqueda) |
                Q(partida_cedula__icontains=busqueda) |
                Q(telefono__icontains=busqueda)
            )
        
        # Limitar resultados
        entrevistas = query[:50]
        
        # Preparar datos para respuesta
        entrevistas_data = []
        for entrevista in entrevistas:
            # Construir cédula completa
            cedula_completa = ""
            if entrevista.provincia_cedula and entrevista.tipo_letra and entrevista.tomo_cedula and entrevista.partida_cedula:
                cedula_completa = f"{entrevista.provincia_cedula}-{entrevista.tipo_letra}-{entrevista.tomo_cedula}-{entrevista.partida_cedula}"
            
            entrevistas_data.append({
                'id': entrevista.id,
                'nombre': entrevista.primer_nombre or '',
                'apellido': entrevista.primer_apellido or '',
                'cedula': cedula_completa,
                'celular': entrevista.telefono or '',
                'fecha_creacion': entrevista.fecha_entrevista.strftime('%d/%m/%Y') if entrevista.fecha_entrevista else '',
                'producto_interesado': entrevista.tipo_producto or ''
            })
        
        return JsonResponse({
            'success': True,
            'entrevistas': entrevistas_data,
            'total': len(entrevistas_data)
        })
        
    except Exception as e:
        print(f"❌ Error en buscar_entrevistas_api: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)


@login_required
def asociar_formulario_general(request, solicitud_id):
    """
    Asocia una entrevista de cliente al campo formulario_general de una solicitud
    """
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'Método no permitido'}, status=405)
        
        # Verificar que la solicitud existe y el usuario tiene permisos
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Obtener datos del request
        import json
        data = json.loads(request.body)
        entrevista_id = data.get('entrevista_id')
        
        if not entrevista_id:
            return JsonResponse({'error': 'ID de entrevista requerido'}, status=400)
        
        # Verificar que la entrevista existe
        entrevista = get_object_or_404(ClienteEntrevista, id=entrevista_id)
        
        # Asociar la entrevista a la solicitud
        solicitud.entrevista_cliente = entrevista
        solicitud.save()
        
        # Registrar en historial si es necesario
        HistorialSolicitud.objects.create(
            solicitud=solicitud,
            etapa=solicitud.etapa_actual,
            subestado=solicitud.subestado_actual,
            usuario_responsable=request.user,
            fecha_inicio=timezone.now()
        )
        
        # Preparar datos de respuesta
        entrevista_data = {
            'id': entrevista.id,
            'nombre': entrevista.primer_nombre or '',
            'apellido': entrevista.primer_apellido or '',
            'cedula': f"{entrevista.provincia_cedula or ''}-{entrevista.tipo_letra or ''}-{entrevista.tomo_cedula or ''}-{entrevista.partida_cedula or ''}",
            'celular': entrevista.telefono or '',
            'fecha_creacion': entrevista.fecha_entrevista.strftime('%d/%m/%Y') if entrevista.fecha_entrevista else '',
            'producto_interesado': entrevista.tipo_producto or ''
        }
        
        return JsonResponse({
            'success': True,
            'message': 'Entrevista asociada correctamente',
            'entrevista': entrevista_data
        })
        
    except Exception as e:
        print(f"❌ Error en asociar_formulario_general: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)


@login_required 
def obtener_formulario_general_asociado(request, solicitud_id):
    """
    Obtiene la entrevista asociada al formulario general de una solicitud
    """
    try:
        if request.method != 'GET':
            return JsonResponse({'error': 'Método no permitido'}, status=405)
        
        # Verificar que la solicitud existe
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        if solicitud.entrevista_cliente:
            entrevista = solicitud.entrevista_cliente
            entrevista_data = {
                'id': entrevista.id,
                'nombre': entrevista.nombre or '',
                'apellido': entrevista.apellido or '',
                'cedula': entrevista.cedulaCliente or '',
                'celular': entrevista.celular or '',
                'fecha_creacion': entrevista.fecha_creacion.strftime('%d/%m/%Y') if entrevista.fecha_creacion else '',
                'producto_interesado': entrevista.producto_interesado or ''
            }
            
            return JsonResponse({
                'success': True,
                'entrevista': entrevista_data
            })
        else:
            return JsonResponse({
                'success': True,
                'entrevista': None
            })
        
    except Exception as e:
        print(f"❌ Error en obtener_formulario_general_asociado: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        }, status=500)


# ==========================================
# VISTAS PARA ASOCIACIÓN DE ENTREVISTAS
# ==========================================

@login_required
def buscar_entrevistas(request):
    """API para buscar entrevistas de clientes"""
    if request.method == 'GET':
        query = request.GET.get('q', '').strip()
        cedula = request.GET.get('cedula', '').strip()
        
        try:
            from .models import ClienteEntrevista
            
            print(f"🔍 buscar_entrevistas iniciado - cedula: '{cedula}', query: '{query}'")
            
            # Base queryset
            queryset = ClienteEntrevista.objects.all()
            print(f"📊 Total entrevistas en BD: {queryset.count()}")
            
            # Si tenemos una cédula específica para filtrar
            if cedula:
                # ✅ IMPORTAR Q AL INICIO para evitar UnboundLocalError
                from django.db.models import Q
                
                # Intentar dividir la cédula en sus componentes
                cedula_parts = cedula.split('-')
                print(f"📋 Cédula dividida: {cedula_parts} (total partes: {len(cedula_parts)})")
                
                # Extraer solo números para búsqueda flexible
                numeros_cedula = ''.join(filter(str.isdigit, cedula))
                
                if len(cedula_parts) == 4:  # Formato completo: provincia-letra-tomo-partida
                    provincia, letra, tomo, partida = cedula_parts
                    print(f"📋 Cédula completa - provincia: {provincia}, letra: {letra}, tomo: {tomo}, partida: {partida}")
                    
                    # Intentar diferentes combinaciones de búsqueda
                    # 1. Búsqueda exacta por todos los componentes
                    # 2. Búsqueda por tomo y partida (los más identificativos)
                    print(f"🔍 Aplicando filtro para cédula completa...")
                    queryset = queryset.filter(
                        Q(provincia_cedula=provincia, tipo_letra=letra, tomo_cedula=tomo, partida_cedula=partida) |
                        Q(tomo_cedula=tomo, partida_cedula=partida)
                    )
                    print(f"📊 Resultados después del filtro: {queryset.count()}")
                    
                elif len(cedula_parts) == 3:  # Formato 8-906-1692: provincia-tomo-partida
                    provincia, tomo, partida = cedula_parts
                    print(f"📋 Cédula 3 partes - provincia: {provincia}, tomo: {tomo}, partida: {partida}")
                    
                    print(f"🔍 Aplicando filtro para formato 3 partes...")
                    queryset = queryset.filter(
                        Q(provincia_cedula=provincia, tomo_cedula=tomo, partida_cedula=partida) |
                        Q(tomo_cedula=tomo, partida_cedula=partida)  # Fallback sin provincia
                    )
                    print(f"📊 Resultados después del filtro 3 partes: {queryset.count()}")
                    
                elif len(cedula_parts) >= 2:  # Formato parcial: solo tomo-partida
                    # Si tenemos al menos tomo y partida, filtramos por ellos
                    tomo = cedula_parts[-2]
                    partida = cedula_parts[-1]
                    print(f"📋 Cédula parcial - tomo: {tomo}, partida: {partida}, partes totales: {len(cedula_parts)}")
                    
                    print(f"🔍 Aplicando filtro para tomo y partida...")
                    queryset = queryset.filter(
                        Q(tomo_cedula=tomo, partida_cedula=partida) |
                        Q(tomo_cedula__endswith=tomo, partida_cedula=partida)
                    )
                    print(f"📊 Resultados después del filtro parcial: {queryset.count()}")
                        
            # Aplicar filtro de búsqueda si hay un query
            if query and len(query) >= 2:
                queryset = queryset.filter(
                    Q(primer_nombre__icontains=query) |
                    Q(primer_apellido__icontains=query) |
                    Q(email__icontains=query)
                )
            elif not cedula:  # Si no hay cédula ni query, retornamos vacío
                return JsonResponse({
                    'success': True,
                    'entrevistas': []
                })
                
            # Limitar resultados y ordenar
            print(f"🔍 Obteniendo entrevistas finales...")
            entrevistas = queryset.order_by('-fecha_entrevista')[:20]
            print(f"📊 Entrevistas finales a procesar: {len(entrevistas)}")
            
            # Serializar resultados
            resultados = []
            print(f"🔄 Comenzando serialización de resultados...")
            for i, entrevista in enumerate(entrevistas):
                try:
                    print(f"📋 Procesando entrevista {i+1}/{len(entrevistas)} - ID: {entrevista.id}")
                    
                    # Construir cédula completa
                    cedula_completa = ""
                    if entrevista.provincia_cedula and entrevista.tipo_letra and entrevista.tomo_cedula and entrevista.partida_cedula:
                        cedula_completa = f"{entrevista.provincia_cedula}-{entrevista.tipo_letra}-{entrevista.tomo_cedula}-{entrevista.partida_cedula}"
                    else:
                        cedula_completa = f"{entrevista.tomo_cedula or ''}-{entrevista.partida_cedula or ''}"
                    
                    print(f"   📄 Cédula construida: {cedula_completa}")
                    
                    # Verificar cada campo que puede causar problemas
                    salario_valor = 0
                    try:
                        salario_valor = float(entrevista.salario) if entrevista.salario else 0
                    except (ValueError, TypeError) as e:
                        print(f"   ⚠️ Error convirtiendo salario: {e}")
                        salario_valor = 0
                    
                    # Verificar fechas
                    fecha_str = ''
                    try:
                        fecha_str = entrevista.fecha_entrevista.strftime('%d/%m/%Y %H:%M') if entrevista.fecha_entrevista else ''
                    except Exception as e:
                        print(f"   ⚠️ Error formateando fecha: {e}")
                        fecha_str = ''
                    
                    entrevista_data = {
                        'id': entrevista.id,
                        'nombre_completo': f"{entrevista.primer_nombre or ''} {entrevista.primer_apellido or ''}".strip(),
                        'nombre': entrevista.primer_nombre or '',
                        'apellido': entrevista.primer_apellido or '',
                        'cedula': cedula_completa,
                        'celular': entrevista.telefono or 'Sin celular',
                        'email': entrevista.email or 'Sin email',
                        'telefono': entrevista.telefono or 'Sin teléfono',
                        'fecha_entrevista': fecha_str,
                        'fecha_creacion': fecha_str,
                        'tipo_producto': entrevista.tipo_producto or 'Sin especificar',
                        'producto_interesado': entrevista.tipo_producto or 'Sin especificar',
                        'salario': salario_valor,
                        'empresa': entrevista.trabajo_lugar or 'Sin empresa',
                        'completada': bool(entrevista.completada_por_admin) if hasattr(entrevista, 'completada_por_admin') else False
                    }
                    
                    resultados.append(entrevista_data)
                    print(f"   ✅ Entrevista {entrevista.id} procesada exitosamente")
                    
                except Exception as e:
                    print(f"   ❌ Error procesando entrevista {entrevista.id}: {e}")
                    continue  # Continuar con la siguiente entrevista
            
            print(f"✅ Serialización completada - Devolviendo {len(resultados)} entrevistas")
            return JsonResponse({
                'success': True,
                'entrevistas': resultados
            })
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"❌ Error en buscar_entrevistas: {e}")
            print(f"❌ TRACEBACK completo: {error_traceback}")
            print(f"❌ Cédula buscada: {cedula}")
            print(f"❌ Query: {query}")
            
            return JsonResponse({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}',
                'debug_info': error_traceback if hasattr(request, 'user') and request.user.is_staff else None
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    }, status=405)


@login_required
@csrf_exempt
def asociar_entrevista(request):
    """API para asociar/desasociar una entrevista con una solicitud"""
    print(f"🔍 asociar_entrevista iniciado - Método: {request.method}")
    print(f"🔍 User: {request.user}")
    print(f"🔍 Headers: {dict(request.headers)}")
    
    if request.method == 'POST':
        try:
            print(f"🔍 Request body raw: {request.body}")
            import json
            data = json.loads(request.body)
            print(f"🔍 Data parsed: {data}")
            
            solicitud_id = data.get('solicitud_id')
            entrevista_id = data.get('entrevista_id')
            accion = data.get('accion')  # 'asociar' o 'desasociar'
            # Flag 'forzar' removido - ya no es necesario porque se permiten múltiples asociaciones
            
            if not solicitud_id or not accion:
                return JsonResponse({
                    'success': False,
                    'error': 'Datos requeridos faltantes'
                }, status=400)
            
            # Obtener la solicitud
            solicitud = get_object_or_404(Solicitud, id=solicitud_id)
            
            # Verificar permisos (el usuario debe tener acceso a la solicitud)
            if not (solicitud.creada_por == request.user or 
                    solicitud.asignada_a == request.user or 
                    request.user.is_superuser or 
                    request.user.is_staff):
                return JsonResponse({
                    'success': False,
                    'error': 'No tienes permisos para modificar esta solicitud'
                }, status=403)
            
            if accion == 'asociar':
                if not entrevista_id:
                    return JsonResponse({
                        'success': False,
                        'error': 'ID de entrevista requerido para asociar'
                    }, status=400)
                
                # Obtener la entrevista
                from .models import ClienteEntrevista
                entrevista = get_object_or_404(ClienteEntrevista, id=entrevista_id)
                
                print(f"🔍 Verificando asociación de entrevista {entrevista_id} con solicitud {solicitud_id}")
                
                # Verificar si la entrevista ya está asociada a esta misma solicitud
                if solicitud.entrevista_cliente and solicitud.entrevista_cliente.id == entrevista.id:
                    return JsonResponse({
                        'success': False,
                        'error': 'Esta entrevista ya está asociada a esta solicitud',
                        'ya_asociada': True
                    }, status=400)
                
                # ✅ PERMITIR MÚLTIPLES ASOCIACIONES: Una entrevista puede estar asociada a múltiples solicitudes
                # Se removió la verificación de exclusividad
                
                # Asociar la entrevista
                print(f"✅ Asociando entrevista {entrevista_id} a solicitud {solicitud_id}")
                solicitud.entrevista_cliente = entrevista
                solicitud.save()
                print(f"✅ Entrevista asociada exitosamente")
                
                return JsonResponse({
                    'success': True,
                    'mensaje': f'Entrevista de {entrevista.primer_nombre} {entrevista.primer_apellido} asociada exitosamente (múltiples asociaciones permitidas)',
                    'entrevista': {
                        'id': entrevista.id,
                        'nombre_completo': f"{entrevista.primer_nombre or ''} {entrevista.primer_apellido or ''}".strip(),
                        'cedula': f"{entrevista.provincia_cedula or ''}-{entrevista.tipo_letra or ''}-{entrevista.tomo_cedula or ''}-{entrevista.partida_cedula or ''}",
                        'celular': entrevista.telefono or 'Sin celular',
                        'fecha_creacion': entrevista.fecha_entrevista.strftime('%d/%m/%Y %H:%M') if entrevista.fecha_entrevista else ''
                    }
                })
                
            elif accion == 'desasociar':
                # Desasociar la entrevista
                entrevista_anterior = solicitud.entrevista_cliente
                solicitud.entrevista_cliente = None
                solicitud.save()
                
                nombre_entrevista = 'la entrevista'
                if entrevista_anterior:
                    nombre_entrevista = f"{entrevista_anterior.primer_nombre or ''} {entrevista_anterior.primer_apellido or ''}".strip()
                    if not nombre_entrevista:
                        nombre_entrevista = 'la entrevista'
                
                return JsonResponse({
                    'success': True,
                    'mensaje': f'Entrevista de {nombre_entrevista} desasociada exitosamente'
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Acción no válida'
                }, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido'
            }, status=400)
        except Exception as e:
            print(f"❌ Error en asociar_entrevista: {e}")
            return JsonResponse({
                'success': False,
                'error': 'Error interno del servidor'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido'
    }, status=405)


# ==========================================
# APIS DE GESTIÓN DE USUARIOS DEL CANAL DIGITAL
# API PARA CAMBIO DE SUBESTADOS EN BACK OFFICE
# ==========================================

@login_required
@csrf_exempt
def api_agregar_usuario_canal_digital(request):
    """API para agregar un usuario al grupo Canal Digital"""
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'Permisos insuficientes'
        }, status=403)
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        }, status=405)
    
    try:
        import json
        from django.contrib.auth.models import User, Group
        
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': 'ID de usuario requerido'
            })
        
        # Obtener usuario
        usuario = get_object_or_404(User, id=user_id, is_active=True)
        
        # Obtener o crear grupo "Canal Digital"
        grupo_canal_digital, created = Group.objects.get_or_create(name="Canal Digital")
        
        # Verificar si ya está en el grupo
        if usuario.groups.filter(name="Canal Digital").exists():
            return JsonResponse({
                'success': False,
                'error': f'El usuario {usuario.get_full_name() or usuario.username} ya pertenece al grupo "Canal Digital"'
            })
        
        # Agregar al grupo
        usuario.groups.add(grupo_canal_digital)
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Usuario {usuario.get_full_name() or usuario.username} agregado al grupo "Canal Digital" exitosamente',
            'usuario': {
                'id': usuario.id,
                'username': usuario.username,
                'full_name': usuario.get_full_name(),
                'email': usuario.email
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
@csrf_exempt
def api_remover_usuario_canal_digital(request):
    """API para remover un usuario del grupo Canal Digital"""
    if not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'Permisos insuficientes'
        }, status=403)
    
    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': 'Método no permitido'
        }, status=405)
    
    try:
        import json
        from django.contrib.auth.models import User, Group
        
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            return JsonResponse({
                'success': False,
                'error': 'ID de usuario requerido'
            })
        
        # Obtener usuario
        usuario = get_object_or_404(User, id=user_id, is_active=True)
        
        # Obtener grupo "Canal Digital"
        try:
            grupo_canal_digital = Group.objects.get(name="Canal Digital")
        except Group.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'El grupo "Canal Digital" no existe'
            })
        
        # Verificar si está en el grupo
        if not usuario.groups.filter(name="Canal Digital").exists():
            return JsonResponse({
                'success': False,
                'error': f'El usuario {usuario.get_full_name() or usuario.username} no pertenece al grupo "Canal Digital"'
            })
        
        # Remover del grupo
        usuario.groups.remove(grupo_canal_digital)
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Usuario {usuario.get_full_name() or usuario.username} removido del grupo "Canal Digital" exitosamente',
            'usuario': {
                'id': usuario.id,
                'username': usuario.username,
                'full_name': usuario.get_full_name(),
                'email': usuario.email
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# ==========================================
# API PARA SOLICITUDES PROCESADAS
# ==========================================

@login_required
def api_solicitudes_procesadas(request):
    """API para obtener solicitudes procesadas por el usuario actual"""
    try:
        # Obtener parámetros de filtro y paginación
        filtro = request.GET.get('filtro', 'todas')
        pagina = int(request.GET.get('pagina', 1))
        por_pagina = 10
        
        # Construir query base según el tipo de usuario
        if request.user.is_staff or request.user.is_superuser:
            # Supervisores y superusuarios pueden ver TODAS las solicitudes procesadas
            base_query = Solicitud.objects.exclude(
                # Excluir solicitudes activas (que aún están en progreso)
                etapa_actual__nombre__in=['En Proceso', 'Pendiente', 'En Revisión']
            ).distinct()
        else:
            # Usuarios regulares - solo solicitudes donde participaron
            base_query = Solicitud.objects.filter(
                Q(creada_por=request.user) |
                Q(historial__usuario=request.user) |
                Q(asignada_a=request.user)
            ).exclude(
                # Excluir solicitudes activas (que aún están en progreso)
                etapa_actual__nombre__in=['En Proceso', 'Pendiente', 'En Revisión']
            ).distinct()
        
        # Aplicar filtros específicos
        if filtro == 'ultima_semana':
            fecha_limite = timezone.now() - timedelta(days=7)
            base_query = base_query.filter(fecha_ultima_actualizacion__gte=fecha_limite)
        elif filtro == 'ultimo_mes':
            fecha_limite = timezone.now() - timedelta(days=30)
            base_query = base_query.filter(fecha_ultima_actualizacion__gte=fecha_limite)
        elif filtro == 'completadas':
            base_query = base_query.filter(
                etapa_actual__nombre__in=['Completada', 'Aprobada', 'Finalizada']
            )
        elif filtro == 'rechazadas':
            base_query = base_query.filter(
                etapa_actual__nombre__in=['Rechazada', 'Denegada', 'Cancelada']
            )
        
        # Ordenar por fecha más reciente
        base_query = base_query.order_by('-fecha_ultima_actualizacion')
        
        # Paginación
        total_solicitudes = base_query.count()
        total_paginas = (total_solicitudes + por_pagina - 1) // por_pagina
        inicio = (pagina - 1) * por_pagina
        fin = inicio + por_pagina
        
        solicitudes_paginadas = base_query[inicio:fin]
        
        # Serializar datos
        solicitudes_data = []
        for solicitud in solicitudes_paginadas:
            # Determinar el estado final basado en la etapa actual
            estado_final = 'completada'  # Por defecto
            if solicitud.etapa_actual:
                etapa_nombre = solicitud.etapa_actual.nombre.lower()
                if any(word in etapa_nombre for word in ['rechaz', 'deneg', 'cancel']):
                    estado_final = 'rechazada'
                elif any(word in etapa_nombre for word in ['cancel', 'anula']):
                    estado_final = 'cancelada'
            
            # Verificar si el usuario puede ver los detalles
            if request.user.is_staff or request.user.is_superuser:
                # Supervisores y superusuarios pueden ver todos los detalles
                puede_ver_detalle = True
            else:
                # Usuarios regulares - solo si participaron en la solicitud
                puede_ver_detalle = (
                    solicitud.creada_por == request.user or
                    solicitud.asignada_a == request.user or
                    HistorialSolicitud.objects.filter(
                        solicitud=solicitud, 
                        usuario=request.user
                    ).exists()
                )
            
            # Obtener el nombre del cliente
            cliente_nombre = 'Cliente no especificado'
            if solicitud.cliente:
                cliente_nombre = f"{solicitud.cliente.primer_nombre} {solicitud.cliente.primer_apellido}"
            elif solicitud.cliente_nombre:
                cliente_nombre = solicitud.cliente_nombre
            
            # Obtener información del usuario que procesó la solicitud (último historial)
            ultimo_historial = HistorialSolicitud.objects.filter(
                solicitud=solicitud
            ).order_by('-fecha_inicio').first()
            
            procesado_por = 'Sistema'
            if ultimo_historial and ultimo_historial.usuario:
                procesado_por = ultimo_historial.usuario.get_full_name() or ultimo_historial.usuario.username
            elif solicitud.asignada_a:
                procesado_por = solicitud.asignada_a.get_full_name() or solicitud.asignada_a.username
            elif solicitud.creada_por:
                procesado_por = solicitud.creada_por.get_full_name() or solicitud.creada_por.username
            
            solicitud_data = {
                'id': solicitud.id,
                'codigo': solicitud.codigo,
                'cliente_nombre': cliente_nombre,
                'etapa_final': solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin etapa',
                'fecha_procesada': solicitud.fecha_ultima_actualizacion.isoformat(),
                'estado_final': estado_final,
                'puede_ver_detalle': puede_ver_detalle,
                'pipeline': solicitud.pipeline.nombre if solicitud.pipeline else 'Sin pipeline',
                'procesado_por': procesado_por,
                'creado_por': solicitud.creada_por.get_full_name() or solicitud.creada_por.username if solicitud.creada_por else 'Desconocido',
                'es_supervisor_view': request.user.is_staff or request.user.is_superuser,
            }
            
            solicitudes_data.append(solicitud_data)
        
        return JsonResponse({
            'success': True,
            'solicitudes': solicitudes_data,
            'total_solicitudes': total_solicitudes,
            'total_paginas': total_paginas,
            'pagina_actual': pagina,
            'por_pagina': por_pagina,
            'filtro_aplicado': filtro,
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def api_cambiar_subestado_backoffice(request, solicitud_id):
    """API para cambiar el subestado actual en Back Office"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if not (solicitud.creada_por == request.user or 
                solicitud.asignada_a == request.user or 
                request.user.is_superuser or
                request.user.is_staff):
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para modificar esta solicitud'
            }, status=403)
        
        # Verificar que estamos en Back Office
        if not (solicitud.etapa_actual and 
                solicitud.etapa_actual.nombre == "Back Office" and 
                solicitud.etapa_actual.es_bandeja_grupal):
            return JsonResponse({
                'success': False,
                'error': 'Esta solicitud no está en la etapa de Back Office'
            }, status=400)
        
        data = json.loads(request.body)
        nuevo_subestado_nombre = data.get('subestado')
        
        if not nuevo_subestado_nombre:
            return JsonResponse({
                'success': False,
                'error': 'Nombre de subestado requerido'
            }, status=400)
        
        # Buscar el subestado
        try:
            nuevo_subestado = solicitud.etapa_actual.subestados.get(nombre=nuevo_subestado_nombre)
        except:
            return JsonResponse({
                'success': False,
                'error': f'Subestado "{nuevo_subestado_nombre}" no encontrado'
            }, status=404)
        
        # Cambiar subestado
        solicitud.subestado_actual = nuevo_subestado
        solicitud.save()
        
        # Notificar cambio
        notify_solicitud_change(solicitud, 'subestado_cambiado', request.user)
        
        return JsonResponse({
            'success': True,
            'mensaje': f'Cambiado a subestado: {nuevo_subestado.nombre}',
            'subestado': {
                'id': nuevo_subestado.id,
                'nombre': nuevo_subestado.nombre,
                'orden': nuevo_subestado.orden
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        print(f"❌ Error en api_cambiar_subestado_backoffice: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


# ==========================================
# BACK OFFICE SUBESTADO VIEWS
# ==========================================

@login_required
def backoffice_checklist(request, solicitud_id):
    """Vista específica para el subestado Checklist del Back Office"""
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que estamos en Back Office
    if not (solicitud.etapa_actual and solicitud.etapa_actual.nombre == "Back Office"):
        messages.error(request, 'Esta solicitud no está en la etapa de Back Office.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Asegurar que el subestado actual sea Checklist
    try:
        checklist_subestado = SubEstado.objects.get(etapa=solicitud.etapa_actual, nombre='Checklist')
        solicitud.subestado_actual = checklist_subestado
        solicitud.save()
    except SubEstado.DoesNotExist:
        messages.error(request, 'El subestado Checklist no existe.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Reutilizar la lógica existente de detalle_solicitud
    return detalle_solicitud(request, solicitud_id)


@login_required  
def backoffice_captura(request, solicitud_id):
    """Vista específica para el subestado Captura del Back Office"""
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que estamos en Back Office
    if not (solicitud.etapa_actual and solicitud.etapa_actual.nombre == "Back Office"):
        messages.error(request, 'Esta solicitud no está en la etapa de Back Office.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Asegurar que el subestado actual sea Captura
    try:
        captura_subestado = SubEstado.objects.get(etapa=solicitud.etapa_actual, nombre='Captura')
        solicitud.subestado_actual = captura_subestado
        solicitud.save()
    except SubEstado.DoesNotExist:
        messages.error(request, 'El subestado Captura no existe.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Usar la misma lógica que detalle_solicitud pero con template específico
    request.GET = request.GET.copy()
    request.GET['subestado'] = 'Captura'
    return detalle_solicitud(request, solicitud_id)


@login_required
def backoffice_firma(request, solicitud_id):
    """Vista específica para el subestado Firma del Back Office"""
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que estamos en Back Office
    if not (solicitud.etapa_actual and solicitud.etapa_actual.nombre == "Back Office"):
        messages.error(request, 'Esta solicitud no está en la etapa de Back Office.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Asegurar que el subestado actual sea Firma
    try:
        firma_subestado = SubEstado.objects.get(etapa=solicitud.etapa_actual, nombre='Firma')
        solicitud.subestado_actual = firma_subestado
        solicitud.save()
    except SubEstado.DoesNotExist:
        messages.error(request, 'El subestado Firma no existe.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Usar la misma lógica que detalle_solicitud pero con template específico
    request.GET = request.GET.copy()
    request.GET['subestado'] = 'Firma'
    return detalle_solicitud(request, solicitud_id)


@login_required
def backoffice_orden(request, solicitud_id):
    """Vista específica para el subestado Orden del expediente del Back Office"""
    from .modelsWorkflow import OrdenExpediente, PlantillaOrdenExpediente
    from collections import defaultdict
    
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que estamos en Back Office
    if not (solicitud.etapa_actual and solicitud.etapa_actual.nombre == "Back Office"):
        messages.error(request, 'Esta solicitud no está en la etapa de Back Office.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Asegurar que el subestado actual sea Orden del expediente
    try:
        orden_subestado = SubEstado.objects.get(etapa=solicitud.etapa_actual, nombre='Orden del expediente')
        solicitud.subestado_actual = orden_subestado
        solicitud.save()
    except SubEstado.DoesNotExist:
        messages.error(request, 'El subestado Orden del expediente no existe.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Función auxiliar para ordenar documentos por sección
    def ordenar_documentos_por_seccion(documentos_qs, pipeline):
        # Crear un diccionario de orden de secciones desde las plantillas
        orden_secciones = {}
        plantillas_orden_seccion = PlantillaOrdenExpediente.objects.filter(
            pipeline=pipeline,
            activo=True
        ).values('seccion', 'orden_seccion').distinct().order_by('orden_seccion')
        
        for plantilla in plantillas_orden_seccion:
            if plantilla['seccion'] not in orden_secciones:
                orden_secciones[plantilla['seccion']] = plantilla['orden_seccion']
        
        # Ordenar documentos usando el orden de sección
        return sorted(
            documentos_qs, 
            key=lambda doc: (orden_secciones.get(doc.seccion, 999), doc.orden)
        )

    # Obtener o crear documentos de orden de expediente para esta solicitud
    documentos_orden_qs = OrdenExpediente.objects.filter(
        solicitud=solicitud, 
        activo=True
    ).select_related('calificado_por')
    
    # Si no hay documentos, crear desde plantillas del pipeline
    if not documentos_orden_qs.exists():
        plantillas = PlantillaOrdenExpediente.objects.filter(
            pipeline=solicitud.pipeline,
            activo=True
        ).order_by('orden_seccion', 'seccion', 'orden')
        
        documentos_creados = []
        for plantilla in plantillas:
            documento = OrdenExpediente.objects.create(
                solicitud=solicitud,
                seccion=plantilla.seccion,
                nombre_documento=plantilla.nombre_documento,
                orden=plantilla.orden,
                obligatorio=plantilla.obligatorio
            )
            documentos_creados.append(documento)
        
        if documentos_creados:
            messages.info(request, f'Se crearon {len(documentos_creados)} documentos desde las plantillas del pipeline.')
    
    # Aplicar ordenamiento personalizado a todos los documentos (nuevos o existentes)
    documentos_orden = ordenar_documentos_por_seccion(documentos_orden_qs, solicitud.pipeline)
    
    # Agrupar documentos por sección
    documentos_por_seccion = defaultdict(list)
    for documento in documentos_orden:
        documentos_por_seccion[documento.seccion].append(documento)
    
    # Estadísticas
    total_documentos = len(documentos_orden)
    documentos_presentes = len([doc for doc in documentos_orden if doc.tiene_documento])
    documentos_faltantes = len([doc for doc in documentos_orden if not doc.tiene_documento and doc.obligatorio])
    documentos_opcionales_faltantes = len([doc for doc in documentos_orden if not doc.tiene_documento and not doc.obligatorio])
    
    # Calcular porcentaje de completitud
    porcentaje_completitud = 0
    if total_documentos > 0:
        porcentaje_completitud = round((documentos_presentes / total_documentos) * 100)
    
    # Transiciones negativas - no necesarias para esta vista específica
    transiciones_negativas = []
    
    context = {
        'solicitud': solicitud,
        'documentos_por_seccion': dict(documentos_por_seccion),
        'total_documentos': total_documentos,
        'documentos_presentes': documentos_presentes,
        'documentos_faltantes': documentos_faltantes,
        'documentos_opcionales_faltantes': documentos_opcionales_faltantes,
        'porcentaje_completitud': porcentaje_completitud,
        'transiciones_negativas': transiciones_negativas,
        'tiene_transiciones_negativas': len(transiciones_negativas) > 0,
        'puede_modificar': True,  # El usuario de backoffice puede modificar
    }
    
    return render(request, 'workflow/detalle_solicitud_orden.html', context)


@login_required
def backoffice_tramite(request, solicitud_id):
    """Vista específica para el subestado Trámite del Back Office"""
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que estamos en Back Office
    if not (solicitud.etapa_actual and solicitud.etapa_actual.nombre == "Back Office"):
        messages.error(request, 'Esta solicitud no está en la etapa de Back Office.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Asegurar que el subestado actual sea Trámite
    try:
        tramite_subestado = SubEstado.objects.get(etapa=solicitud.etapa_actual, nombre='Trámite')
        solicitud.subestado_actual = tramite_subestado
        solicitud.save()
    except SubEstado.DoesNotExist:
        messages.error(request, 'El subestado Trámite no existe.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Usar la misma lógica que detalle_solicitud pero con template específico
    request.GET = request.GET.copy()
    request.GET['subestado'] = 'Trámite'
    return detalle_solicitud(request, solicitud_id)


@login_required
def backoffice_subsanacion(request, solicitud_id):
    """Vista específica para el subestado Subsanación de pendientes Trámite del Back Office"""
    solicitud = get_object_or_404(Solicitud, id=solicitud_id)
    
    # Verificar que estamos en Back Office
    if not (solicitud.etapa_actual and solicitud.etapa_actual.nombre == "Back Office"):
        messages.error(request, 'Esta solicitud no está en la etapa de Back Office.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Asegurar que el subestado actual sea Subsanación de pendientes Trámite
    try:
        subsanacion_subestado = SubEstado.objects.get(etapa=solicitud.etapa_actual, nombre='Subsanación de pendientes Trámite')
        solicitud.subestado_actual = subsanacion_subestado
        solicitud.save()
    except SubEstado.DoesNotExist:
        messages.error(request, 'El subestado Subsanación de pendientes Trámite no existe.')
        return redirect('detalle_solicitud', solicitud_id=solicitud_id)
    
    # Usar la misma lógica que detalle_solicitud pero con template específico
    request.GET = request.GET.copy()
    request.GET['subestado'] = 'Subsanación de pendientes Trámite'
    return detalle_solicitud(request, solicitud_id)


def crear_calificaciones_pendientes_backoffice(solicitud, usuario_asignado):
    """
    🚨 BULLETPROOF: Crear calificaciones automáticas FORZANDO la creación en BD
    """
    from .models import CalificacionDocumentoBackoffice, RequisitoTransicion, RequisitoSolicitud
    from django.db import transaction
    
    print(f"🚨 INICIANDO crear_calificaciones_pendientes_backoffice para solicitud {solicitud.codigo}")
    print(f"🚨 Usuario asignado: {usuario_asignado.username}")
    print(f"🚨 Etapa actual: {solicitud.etapa_actual.nombre}")
    
    try:
        with transaction.atomic():  # FORZAR transacción
            calificaciones_creadas = 0
            
            # ✅ MÉTODO DIRECTO: Obtener TODOS los RequisitoSolicitud de la solicitud
            todos_requisitos = RequisitoSolicitud.objects.filter(solicitud=solicitud)
            print(f"🚨 ENCONTRADOS {todos_requisitos.count()} RequisitoSolicitud para procesar")
            
            for req_sol in todos_requisitos:
                try:
                    # Verificar que no exista ya una calificación
                    calificacion_existente = CalificacionDocumentoBackoffice.objects.filter(
                        requisito_solicitud=req_sol
                    ).first()
                    
                    if not calificacion_existente:
                        print(f"🚨 CREANDO calificación para: {req_sol.requisito.nombre}")
                        
                        # CREAR CALIFICACIÓN FORZADA
                        nueva_calificacion = CalificacionDocumentoBackoffice.objects.create(
                            requisito_solicitud=req_sol,
                            calificado_por=usuario_asignado,
                            estado='pendiente'
                        )
                        
                        # VERIFICAR QUE SE CREÓ
                        if nueva_calificacion.id:
                            calificaciones_creadas += 1
                            print(f"✅ CALIFICACIÓN CREADA CON ID: {nueva_calificacion.id} para {req_sol.requisito.nombre}")
                        else:
                            print(f"❌ FALLÓ crear calificación para {req_sol.requisito.nombre}")
                    
                    else:
                        print(f"ℹ️  Ya existe calificación para: {req_sol.requisito.nombre} (Estado: {calificacion_existente.estado})")
                        
                except Exception as e_inner:
                    print(f"❌ Error individual creando para {req_sol.requisito.nombre}: {str(e_inner)}")
                    continue
            
            print(f"🎯 RESULTADO FINAL: {calificaciones_creadas} calificaciones creadas para solicitud {solicitud.codigo}")
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO creando calificaciones pendientes: {str(e)}")
        import traceback
        print(f"❌ TRACEBACK COMPLETO: {traceback.format_exc()}")
        # No lanzar excepción para no interrumpir el flujo de asignación


def verificar_documentos_pendientes_backoffice(solicitud):
    """
    Verificar si hay documentos pendientes (opcionales sin archivo) en Back Office
    """
    from .models import CalificacionDocumentoBackoffice, RequisitoTransicion, RequisitoSolicitud
    
    documentos_pendientes = []
    
    try:
        # Obtener calificaciones pendientes
        calificaciones_pendientes = CalificacionDocumentoBackoffice.objects.filter(
            requisito_solicitud__solicitud=solicitud,
            estado='pendiente'
        ).select_related('requisito_solicitud__requisito')
        
        for calificacion in calificaciones_pendientes:
            documentos_pendientes.append({
                'id': calificacion.requisito_solicitud.id,
                'nombre': calificacion.requisito_solicitud.requisito.nombre,
                'calificacion_id': calificacion.id
            })
        
        return documentos_pendientes
        
    except Exception as e:
        print(f"❌ Error verificando documentos pendientes: {str(e)}")
        return []


@login_required
@require_http_methods(["GET"])
def api_obtener_siguiente_subestado(request, solicitud_id):
    """
    API para obtener el siguiente subestado disponible para una solicitud en Back Office
    """
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar que estamos en Back Office
        if not solicitud.etapa_actual or 'back office' not in solicitud.etapa_actual.nombre.lower():
            return JsonResponse({
                'success': False,
                'error': 'La solicitud no está en Back Office'
            }, status=400)
        
        # Obtener el subestado actual
        subestado_actual = solicitud.subestado_actual
        if not subestado_actual:
            return JsonResponse({
                'success': False,
                'error': 'No se encontró el subestado actual'
            }, status=400)
        
        # Obtener todos los subestados de Back Office ordenados
        subestados_backoffice = solicitud.etapa_actual.subestados.all().order_by('orden')
        
        # Encontrar el siguiente subestado
        siguiente_subestado = None
        for subestado in subestados_backoffice:
            if subestado.orden > subestado_actual.orden:
                siguiente_subestado = subestado
                break
        
        # Si no hay siguiente subestado, significa que terminamos Back Office
        if siguiente_subestado:
            return JsonResponse({
                'success': True,
                'siguiente_subestado': {
                    'id': siguiente_subestado.id,
                    'nombre': siguiente_subestado.nombre,
                    'orden': siguiente_subestado.orden
                }
            })
        else:
            # Obtener siguiente etapa disponible
            transiciones_salida = solicitud.etapa_actual.transiciones_salida.all()
            if transiciones_salida.exists():
                siguiente_etapa = transiciones_salida.first().etapa_destino
                return JsonResponse({
                    'success': True,
                    'siguiente_subestado': None,
                    'siguiente_etapa': {
                        'id': siguiente_etapa.id,
                        'nombre': siguiente_etapa.nombre
                    }
                })
            else:
                return JsonResponse({
                    'success': True,
                    'siguiente_subestado': None,
                    'siguiente_etapa': None
                })
        
    except Exception as e:
        print(f"❌ Error obteniendo siguiente subestado: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_validar_documentos_backoffice(request, solicitud_id):
    """
    Validar que todos los documentos obligatorios estén calificados como 'bueno'
    antes de permitir avanzar al siguiente subestado.
    """
    from .models import CalificacionDocumentoBackoffice
    
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar que el usuario tenga permisos
        if not (request.user.is_superuser or request.user.is_staff or solicitud.asignada_a == request.user):
            return JsonResponse({
                'success': False, 
                'error': 'No tienes permisos para validar esta solicitud'
            }, status=403)
        
        # ✅ CORREGIDO: Obtener solo los requisitos definidos en RequisitoTransicion para Back Office
        # Los documentos para Back Office están definidos en las transiciones DE ENTRADA hacia Back Office
        # (no en las de salida, que son para la siguiente etapa)
        transiciones_entrada = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_destino=solicitud.etapa_actual
        ).prefetch_related('requisitos_obligatorios__requisito')
        
        # Obtener todos los requisitos definidos en RequisitoTransicion de entrada
        requisitos_definidos = {}
        for transicion in transiciones_entrada:
            for req_transicion in transicion.requisitos_obligatorios.all():
                req_id = req_transicion.requisito.id
                if req_id not in requisitos_definidos:
                    requisitos_definidos[req_id] = {
                        'requisito': req_transicion.requisito,
                        'obligatorio': req_transicion.obligatorio,
                        'mensaje_personalizado': req_transicion.mensaje_personalizado,
                        'transicion_origen': transicion.etapa_origen.nombre
                    }
        
        # Solo procesar RequisitoSolicitud que estén definidos en RequisitoTransicion de entrada
        requisitos_solicitud = RequisitoSolicitud.objects.filter(
            solicitud=solicitud,
            requisito_id__in=requisitos_definidos.keys()  # 🎯 CLAVE: Solo los definidos en RequisitoTransicion
        ).select_related('requisito')
        
        documentos_problematicos = []
        documentos_pendientes = []
        documentos_buenos = 0
        documentos_malos = 0
        
        # 🔍 DEBUG SIMPLIFICADO: Solo información esencial
        print(f"📋 Validando solicitud {solicitud_id}: {len(requisitos_definidos)} requisitos definidos")
        
        # Validar documentos - Solo documentos OBLIGATORIOS calificados como "malo" bloquean el avance
        for req_sol in requisitos_solicitud:
            # Buscar la calificación más reciente
            calificacion = CalificacionDocumentoBackoffice.objects.filter(
                requisito_solicitud=req_sol
            ).order_by('-fecha_calificacion').first()
            
            # Obtener información de obligatoriedad desde RequisitoTransicion
            req_id = req_sol.requisito.id
            es_obligatorio = requisitos_definidos.get(req_id, {}).get('obligatorio', False)
            
            if calificacion:
                estado = calificacion.estado
                
                # ✅ VERIFICAR DOCUMENTOS "PENDIENTE" - Solo obligatorios bloquean
                if estado == 'pendiente':
                    if es_obligatorio:
                        # Documento OBLIGATORIO pendiente → BLOQUEA
                        documentos_problematicos.append({
                            'nombre': req_sol.requisito.nombre,
                            'problema': 'obligatorio_pendiente',
                            'estado_actual': estado,
                            'es_obligatorio': True
                        })
                    else:
                        # Documento OPCIONAL pendiente → NO bloquea
                        documentos_pendientes.append({
                            'nombre': req_sol.requisito.nombre,
                            'estado': 'pendiente',
                            'es_obligatorio': es_obligatorio
                        })
                    continue
                
                # Contar por estado (solo bueno/malo, pendiente se ignora)
                if estado == 'bueno':
                    documentos_buenos += 1
                elif estado == 'malo':
                    documentos_malos += 1
                    # ✅ LÓGICA CORRECTA: Solo documentos OBLIGATORIOS "malo" bloquean
                    if es_obligatorio:
                        documentos_problematicos.append({
                            'nombre': req_sol.requisito.nombre,
                            'problema': 'calificado_como_malo',
                            'estado_actual': estado,
                            'es_obligatorio': True
                        })
                    # Los documentos opcionales "malo" NO bloquean el avance
            else:
                # Sin calificación = pendiente automático (permite avanzar)
                documentos_pendientes.append({
                    'nombre': req_sol.requisito.nombre,
                    'estado': 'sin_calificacion_pendiente',
                    'es_obligatorio': es_obligatorio
                })
                
                # Crear calificación automática como "pendiente"
                try:
                    CalificacionDocumentoBackoffice.objects.get_or_create(
                        requisito_solicitud=req_sol,
                        defaults={
                            'calificado_por': request.user,
                            'estado': 'pendiente'
                        }
                    )
                except Exception:
                    pass  # Ignorar errores de creación automática
        
        # ✅ NUEVO: Incluir documentos definidos en RequisitoTransicion que NO están en RequisitoSolicitud
        # Estos son documentos requeridos que el usuario aún no ha subido
        for req_id, req_info in requisitos_definidos.items():
            # Si no existe un RequisitoSolicitud para este requisito
            if not requisitos_solicitud.filter(requisito_id=req_id).exists():
                documentos_pendientes.append({
                    'nombre': req_info['requisito'].nombre,
                    'estado': 'faltante',
                    'obligatorio': req_info['obligatorio'],
                    'mensaje_personalizado': req_info['mensaje_personalizado']
                })
        
        # ✅ LÓGICA CORREGIDA: Solo bloquear por documentos OBLIGATORIOS sin calificar
        documentos_obligatorios_sin_calificar = []
        
        # Verificar documentos obligatorios que no han sido calificados
        for req_id, req_info in requisitos_definidos.items():
            es_obligatorio = req_info['obligatorio']
            if es_obligatorio:
                # Buscar si existe calificación para este documento obligatorio
                req_sol_existe = requisitos_solicitud.filter(requisito_id=req_id).first()
                if not req_sol_existe:
                    # Documento obligatorio que no ha sido subido/calificado
                    documentos_obligatorios_sin_calificar.append({
                        'nombre': req_info['requisito'].nombre,
                        'problema': 'sin_subir',
                        'es_obligatorio': True
                    })
                else:
                    # Verificar si tiene calificación
                    calificacion = CalificacionDocumentoBackoffice.objects.filter(
                        requisito_solicitud=req_sol_existe
                    ).order_by('-fecha_calificacion').first()
                    
                    if not calificacion:
                        # Documento subido pero sin calificar
                        documentos_obligatorios_sin_calificar.append({
                            'nombre': req_info['requisito'].nombre,
                            'problema': 'sin_calificar',
                            'es_obligatorio': True
                        })
        
        # 🎯 REGLAS DE BLOQUEO: 
        # 1. Documentos obligatorios sin calificar → BLOQUEAN
        # 2. Documentos obligatorios "malo" → BLOQUEAN  
        # 3. Documentos "pendiente" → NO bloquean
        # 4. Documentos opcionales "malo" → NO bloquean
        
        total_bloqueantes = len(documentos_obligatorios_sin_calificar) + len(documentos_problematicos)
        print(f"🎯 Resultado: {len(documentos_obligatorios_sin_calificar)} sin calificar + {len(documentos_problematicos)} obligatorios 'malo' = {total_bloqueantes} bloqueantes")
        
        if total_bloqueantes == 0:
            # Mensaje personalizado basado en la situación
            mensaje_partes = []
            if documentos_buenos > 0:
                mensaje_partes.append(f"{documentos_buenos} documento(s) bueno(s)")
            if documentos_malos > 0:
                mensaje_partes.append(f"{documentos_malos} documento(s) malo(s) - NO bloquean")
            if len(documentos_pendientes) > 0:
                mensaje_partes.append(f"{len(documentos_pendientes)} documento(s) pendiente(s) - NO bloquean")
            
            if mensaje_partes:
                detalle = ", ".join(mensaje_partes)
                mensaje = f'✅ Puede avanzar. Estado: {detalle}. (Documentos "pendiente" y opcionales "malo" NO bloquean)'
            else:
                mensaje = '✅ Puede avanzar. No hay documentos obligatorios que bloqueen el avance.'
            
            return JsonResponse({
                'success': True,
                'puede_avanzar': True,
                'mensaje': mensaje,
                'documentos_pendientes': documentos_pendientes,
                'total_documentos': len(requisitos_definidos),  # ✅ Total según RequisitoTransicion
                'documentos_buenos': documentos_buenos,
                'documentos_malos': documentos_malos,
                'documentos_pendientes_count': len(documentos_pendientes)
            })
        else:
            # ❌ HAY DOCUMENTOS BLOQUEANTES - BLOQUEAR AVANCE
            mensajes_detalle = []
            
            # Agregar documentos sin calificar
            for doc in documentos_obligatorios_sin_calificar:
                if doc['problema'] == 'sin_subir':
                    mensajes_detalle.append(f"• {doc['nombre']}: Documento OBLIGATORIO no subido")
                elif doc['problema'] == 'sin_calificar':
                    mensajes_detalle.append(f"• {doc['nombre']}: Documento OBLIGATORIO sin calificar")
            
            # Agregar documentos obligatorios "malo"
            for doc in documentos_problematicos:
                if doc['problema'] == 'calificado_como_malo':
                    mensajes_detalle.append(f"• {doc['nombre']}: Documento OBLIGATORIO calificado como 'Malo'")
                elif doc['problema'] == 'obligatorio_pendiente':
                    mensajes_detalle.append(f"• {doc['nombre']}: Documento OBLIGATORIO pendiente - requiere calificación")
            
            # Combinar todos los documentos problemáticos para la respuesta
            todos_problematicos = documentos_obligatorios_sin_calificar + documentos_problematicos
            
            return JsonResponse({
                'success': True,
                'puede_avanzar': False,
                'documentos_problematicos': todos_problematicos,
                'documentos_pendientes': documentos_pendientes,
                'mensaje': f'No puede avanzar: {total_bloqueantes} documento(s) OBLIGATORIO(S) requieren atención',
                'detalle': mensajes_detalle,
                'total_documentos': len(requisitos_definidos),
                'documentos_buenos': documentos_buenos,
                'documentos_malos': documentos_malos,
                'documentos_pendientes_count': len(documentos_pendientes)
            })

            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_avanzar_subestado_backoffice(request, solicitud_id):
    """
    API para avanzar al siguiente subestado en Back Office con opción de asignación
    """
    try:
        import json
        from django.contrib.auth.models import User
        
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        data = json.loads(request.body)
        
        opcion = data.get('opcion')  # 'yo' o 'otro'
        usuario_id = data.get('usuario_id')
        siguiente_subestado_id = data.get('siguiente_subestado_id')
        
        # Validaciones
        if opcion not in ['yo', 'otro', 'bandeja']:
            return JsonResponse({
                'success': False,
                'error': 'Opción inválida. Debe ser "yo", "otro" o "bandeja"'
            }, status=400)
        
        if opcion == 'otro' and not usuario_id:
            return JsonResponse({
                'success': False,
                'error': 'Debe especificar un usuario para asignar'
            }, status=400)
        
        # Verificar que estamos en Back Office
        if not solicitud.etapa_actual or 'back office' not in solicitud.etapa_actual.nombre.lower():
            return JsonResponse({
                'success': False,
                'error': 'La solicitud no está en Back Office'
            }, status=400)
        
        # Determinar el usuario asignado
        if opcion == 'yo':
            usuario_asignado = request.user
        elif opcion == 'otro':
            usuario_asignado = get_object_or_404(User, id=usuario_id)
        else:  # opcion == 'bandeja'
            usuario_asignado = None  # Sin asignar, queda en bandeja grupal
        
        # Si hay siguiente subestado, avanzar a él
        if siguiente_subestado_id:
            siguiente_subestado = get_object_or_404(SubEstado, id=siguiente_subestado_id)
            
            # Actualizar la solicitud
            solicitud.subestado_actual = siguiente_subestado
            solicitud.asignada_a = usuario_asignado
            solicitud.save()
            
            # ✅ CORREGIDO: Crear calificaciones pendientes SIEMPRE, para todas las opciones
            # Determinar el usuario que va a calificar
            usuario_calificador = usuario_asignado if usuario_asignado else request.user
            crear_calificaciones_pendientes_backoffice(solicitud, usuario_calificador)
            print(f"✅ Calificaciones pendientes creadas para solicitud {solicitud.codigo} con usuario {usuario_calificador.username}")
            
            # Generar URL de redirección
            if opcion == 'yo':
                # Normalizar nombre del subestado para la URL
                def normalizar_subestado_url(nombre):
                    """Normaliza el nombre del subestado para crear URLs válidas"""
                    # Mapeo específico para los subestados de Back Office
                    mapeo_subestados = {
                        'checklist': 'checklist',
                        'captura': 'captura', 
                        'firma': 'firma',
                        'orden del expediente': 'orden',
                        'trámite': 'tramite',  # Sin acento
                        'subsanación de pendientes trámite': 'subsanacion'  # Sin acento y simplificado
                    }
                    
                    nombre_lower = nombre.lower().strip()
                    return mapeo_subestados.get(nombre_lower, nombre_lower.replace(' ', '-'))
                
                subestado_url = normalizar_subestado_url(siguiente_subestado.nombre)
                redirect_url = f"/solicitudes/{solicitud.id}/backoffice/{subestado_url}/"
            else:  # opcion == 'otro' o 'bandeja'
                redirect_url = "/workflow/bandeja-mixta/"
            
            # Notificar cambio
            notify_solicitud_change(solicitud, 'subestado_changed', request.user)
            
            # Generar mensaje según la opción
            if opcion == 'yo':
                mensaje = f'Solicitud avanzada a {siguiente_subestado.nombre}. Continuarás trabajando en este subestado.'
            elif opcion == 'otro':
                mensaje = f'Solicitud avanzada a {siguiente_subestado.nombre} y asignada a {usuario_asignado.get_full_name() or usuario_asignado.username}.'
            else:  # opcion == 'bandeja'
                mensaje = f'Solicitud avanzada a {siguiente_subestado.nombre} y devuelta a la bandeja grupal para que cualquier usuario pueda tomarla.'
            
            return JsonResponse({
                'success': True,
                'mensaje': mensaje,
                'redirect_url': redirect_url
            })
        
        else:
            # No hay siguiente subestado, avanzar a la siguiente etapa
            transiciones_salida = solicitud.etapa_actual.transiciones_salida.all()
            
            if not transiciones_salida.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'No hay transiciones disponibles desde esta etapa'
                }, status=400)
            
            # Tomar la primera transición disponible (puede mejorarse con lógica más específica)
            transicion = transiciones_salida.first()
            siguiente_etapa = transicion.etapa_destino
            
            # Actualizar la solicitud
            solicitud.etapa_actual = siguiente_etapa
            solicitud.subestado_actual = None  # Se asignará en la nueva etapa
            solicitud.asignada_a = usuario_asignado
            solicitud.save()
            
            # Generar URL de redirección
            if opcion == 'yo':
                redirect_url = f"/solicitudes/{solicitud.id}/"
            else:  # opcion == 'otro' o 'bandeja'
                redirect_url = "/workflow/bandeja-mixta/"
            
            # Notificar cambio
            notify_solicitud_change(solicitud, 'etapa_changed', request.user)
            
            # Generar mensaje según la opción
            if opcion == 'yo':
                mensaje = f'Solicitud avanzada a la etapa {siguiente_etapa.nombre}. Continuarás trabajando en esta etapa.'
            elif opcion == 'otro':
                mensaje = f'Solicitud avanzada a la etapa {siguiente_etapa.nombre} y asignada a {usuario_asignado.get_full_name() or usuario_asignado.username}.'
            else:  # opcion == 'bandeja'
                mensaje = f'Solicitud avanzada a la etapa {siguiente_etapa.nombre} y devuelta a la bandeja grupal para que cualquier usuario pueda tomarla.'
            
            return JsonResponse({
                'success': True,
                'mensaje': mensaje,
                'redirect_url': redirect_url
            })
        
    except Exception as e:
        print(f"❌ Error avanzando subestado: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_obtener_transiciones_negativas(request, solicitud_id):
    """API para obtener transiciones negativas (hacia atrás) disponibles para una solicitud"""
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        etapa_actual = solicitud.etapa_actual
        
        # Buscar transiciones desde la etapa actual hacia etapas con orden menor (transiciones negativas)
        transiciones_negativas = TransicionEtapa.objects.filter(
            pipeline=solicitud.pipeline,
            etapa_origen=etapa_actual,
            etapa_destino__orden__lt=etapa_actual.orden  # Orden menor = hacia atrás
        ).select_related('etapa_destino').order_by('-etapa_destino__orden')  # Ordenar por etapa destino descendente
        
        transiciones_data = []
        for transicion in transiciones_negativas:
            transiciones_data.append({
                'id': transicion.id,
                'nombre': transicion.nombre,
                'etapa_destino': {
                    'id': transicion.etapa_destino.id,
                    'nombre': transicion.etapa_destino.nombre,
                    'orden': transicion.etapa_destino.orden
                },
                'requiere_permiso': transicion.requiere_permiso
            })
        
        return JsonResponse({
            'success': True,
            'transiciones_negativas': transiciones_data,
            'tiene_transiciones_negativas': len(transiciones_data) > 0
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        })

# ==========================================
# PDF RESULTADO CONSULTA API
# ==========================================

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_pdf_resultado_consulta(request, solicitud_id):
    """
    API para generar PDF con el resultado de la consulta de análisis usando xhtml2pdf
    """
    try:
        # Check if xhtml2pdf is available
        if not XHTML2PDF_AVAILABLE:
            return JsonResponse({
                "success": False,
                "error": "xhtml2pdf library is not available. Please install it with: pip install xhtml2pdf"
            }, status=500)
        
        # Obtener solicitud
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Parsear datos del request
        data = json.loads(request.body) if request.body else {}
        
        # Import required modules
        from django.template.loader import render_to_string
        from django.utils import timezone
        
        # Obtener calificaciones existentes de la base de datos
        calificaciones = CalificacionCampo.objects.filter(solicitud=solicitud)
        
        # Obtener comentarios de analista
        comentarios_analista = SolicitudComentario.objects.filter(
            solicitud=solicitud,
            tipo="analista_credito"
        ).order_by("-fecha_creacion")
        
        # Obtener el comentario más reciente del analista
        # Priorizar CalificacionCampo con campo 'comentario_analista_credito'
        analyst_comment = ""
        
        # Primero, buscar en CalificacionCampo
        calificacion_analista = CalificacionCampo.objects.filter(
            solicitud=solicitud,
            campo='comentario_analista_credito'
        ).exclude(comentario__isnull=True).exclude(comentario='').first()
        
        if calificacion_analista and calificacion_analista.comentario:
            analyst_comment = calificacion_analista.comentario
        elif comentarios_analista.exists():
            # Fallback a SolicitudComentario si no hay CalificacionCampo
            first_comment = comentarios_analista.first()
            if first_comment:
                analyst_comment = first_comment.comentario
        
        # Obtener resultado de análisis
        # Priorizar solicitud.resultado_consulta sobre subestado_actual.nombre
        resultado_analisis = ""
        if solicitud.resultado_consulta:
            resultado_analisis = solicitud.resultado_consulta
        elif solicitud.subestado_actual:
            resultado_analisis = solicitud.subestado_actual.nombre
        
        # Obtener field values desde los datos del request
        field_values = data.get('field_values', {})
        
        # Crear lista enriquecida de calificaciones con valores
        calificaciones_with_values = []
        for cal in calificaciones:
            field_value = field_values.get(cal.campo, '')
            cal_dict = {
                'campo': cal.campo,
                'campo_legible': getattr(cal, 'campo_legible', None),
                'estado': cal.estado,
                'comentario': cal.comentario,
                'field_value': field_value,
            }
            calificaciones_with_values.append(cal_dict)
        
        # Preparar contexto para el template
        context = {
            'solicitud': solicitud,
            'calificaciones': calificaciones_with_values,
            'comentarios_analista': comentarios_analista,
            'analyst_comment': analyst_comment,
            'resultado_analisis': resultado_analisis,
            'field_values': field_values,  # Keep for backward compatibility
            'fecha_generacion': timezone.now(),
        }
        
        # Renderizar HTML usando el template optimizado
        html_string = render_to_string('workflow/pdf_resultado_consulta_simple.html', context)
        
        # Generar PDF con xhtml2pdf
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.pisaDocument(io.StringIO(html_string), pdf_buffer)
        
        if pisa_status.err:
            return JsonResponse({
                "success": False,
                "error": "Error al generar PDF con xhtml2pdf"
            }, status=500)
        
        # Obtener contenido del PDF
        pdf_content = pdf_buffer.getvalue()
        pdf_buffer.close()
        
        if not pdf_content:
            return JsonResponse({
                "success": False,
                "error": "PDF generado está vacío"
            }, status=500)
        
        # Preparar respuesta
        response = HttpResponse(pdf_content, content_type="application/pdf")
        filename = f"Resultado_Consulta_{solicitud.codigo}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        
        return response
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Solicitud no encontrada"
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Datos JSON inválidos"
        }, status=400)
    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        import traceback
        traceback.print_exc()  # This will help debug the issue
        return JsonResponse({
            "success": False,
            "error": f"Error interno: {str(e)}"
        }, status=500)


def generar_pdf_resultado_consulta(pdf_data):
    """
    Genera el PDF con el resultado de la consulta de análisis
    """
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    from django.conf import settings
    import os
    
    buffer = io.BytesIO()
    
    # Crear documento PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    document_title_style = ParagraphStyle(
        "DocumentTitle",
        parent=styles["Heading1"],
        fontSize=14,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.darkgreen
    )
    
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Heading2"],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkgreen
    )
    
    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    # Elementos del documento
    elements = []
    
    # Logo de la empresa
    try:
        # Buscar el logo en diferentes ubicaciones posibles
        logo_paths = [
            os.path.join(settings.STATICFILES_DIRS[0], 'logoColor.png') if settings.STATICFILES_DIRS else None,
            os.path.join(settings.STATIC_ROOT, 'logoColor.png') if settings.STATIC_ROOT else None,
            os.path.join(settings.BASE_DIR, 'staticfiles', 'logoColor.png'),
            os.path.join(settings.BASE_DIR, 'static', 'images', 'logoColor.png'),
            os.path.join(settings.BASE_DIR, 'staticfiles', 'images', 'logoColor.png'),
        ]
        
        logo_path = None
        for path in logo_paths:
            if path and os.path.exists(path):
                logo_path = path
                break
        
        if logo_path:
            # Crear imagen del logo
            logo = Image(logo_path, width=2*inch, height=1*inch)
            logo.hAlign = 'CENTER'
            elements.append(logo)
            elements.append(Spacer(1, 20))
        else:
            # Si no se encuentra el logo, agregar el nombre de la empresa
            company_name = Paragraph("Financiera Pacífico", title_style)
            elements.append(company_name)
            elements.append(Spacer(1, 20))
            
    except Exception as e:
        # Fallback en caso de error con el logo
        company_name = Paragraph("Financiera Pacífico", title_style)
        elements.append(company_name)
        elements.append(Spacer(1, 20))
    
    # Título principal
    solicitud = pdf_data["solicitud"]
    title = Paragraph(f"Resultado de Consulta - Análisis de Solicitud {solicitud.codigo}", document_title_style)
    elements.append(title)
    elements.append(Spacer(1, 20))
    
    # Información general de la solicitud
    elements.append(Paragraph("Resumen Completo de la Solicitud", subtitle_style))
    
    # Crear tabla con información básica
    solicitud_info = [
        ["Código de Solicitud:", solicitud.codigo or "-"],
        ["Pipeline:", solicitud.pipeline.nombre if solicitud.pipeline else "-"],
        ["Etapa Actual:", solicitud.etapa_actual.nombre if solicitud.etapa_actual else "-"],
        ["Cliente:", (solicitud.cliente.nombreCliente or '') if solicitud.cliente else "-"],
        ["Cédula/Documento:", solicitud.cliente.cedulaCliente if solicitud.cliente else "-"],
        ["Fecha de Creación:", solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M') if solicitud.fecha_creacion else "-"],
        ["Asignado a:", f"{solicitud.asignada_a.first_name} {solicitud.asignada_a.last_name}" if solicitud.asignada_a else "Sin asignar"],
        ["Prioridad:", solicitud.prioridad or "-"],
    ]
    
    # Agregar información de cotización si existe
    if solicitud.cotizacion:
        solicitud_info.extend([
            ["Monto Préstamo:", f"B/. {solicitud.cotizacion.montoPrestamo:,.2f}" if solicitud.cotizacion.montoPrestamo else "-"],
            ["Plazo:", f"{solicitud.cotizacion.plazoPago} meses" if solicitud.cotizacion.plazoPago else "-"],
            ["Tasa:", f"{solicitud.cotizacion.tasaInteres}%" if solicitud.cotizacion.tasaInteres else "-"],
        ])
    
    info_table = Table(solicitud_info, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Motivo de la consulta
    if solicitud.motivo_consulta:
        elements.append(Paragraph("Motivo de la Consulta", subtitle_style))
        motivo_text = Paragraph(solicitud.motivo_consulta, normal_style)
        elements.append(motivo_text)
        elements.append(Spacer(1, 15))
    
    # Comentarios de campos (calificaciones)
    calificaciones = pdf_data["calificaciones"]
    if calificaciones:
        elements.append(Paragraph("Comentarios de Campos (Auto-generados)", subtitle_style))
        
        for cal in calificaciones:
            campo_name = obtener_nombre_campo_legible(cal.campo, solicitud)
            estado_text = "✓ Bueno" if cal.estado == "bueno" else "✗ Malo"
            estado_color = colors.green if cal.estado == "bueno" else colors.red
            
            # Crear párrafo con el campo y estado
            campo_paragraph = Paragraph(
                f"<b>{campo_name}:</b> <font color=\"{estado_color.hexval()}\">{estado_text}</font>",
                normal_style
            )
            elements.append(campo_paragraph)
            
            # Agregar comentario si existe
            if cal.comentario:
                comentario_paragraph = Paragraph(
                    f"&nbsp;&nbsp;&nbsp;&nbsp;<i>Comentario: {cal.comentario}</i>",
                    normal_style
                )
                elements.append(comentario_paragraph)
        
        elements.append(Spacer(1, 15))
    
    # Análisis General del Analista
    elementos_analisis = []
    
    # Comentario del analista desde el formulario
    if pdf_data.get("analyst_comment"):
        elementos_analisis.append(("Análisis Actual:", pdf_data["analyst_comment"]))
    
    # Comentarios históricos del analista
    comentarios_analista = pdf_data["comentarios_analista"]
    if comentarios_analista:
        for i, comentario in enumerate(comentarios_analista[:3]):  # Últimos 3 comentarios
            fecha_str = comentario.fecha_creacion.strftime('%d/%m/%Y %H:%M')
            usuario_str = f"{comentario.usuario.first_name} {comentario.usuario.last_name}"
            elementos_analisis.append((
                f"Comentario {i+1} ({fecha_str} - {usuario_str}):",
                comentario.contenido
            ))
    
    if elementos_analisis:
        elements.append(Paragraph("Análisis General", subtitle_style))
        
        for titulo, contenido in elementos_analisis:
            elements.append(Paragraph(f"<b>{titulo}</b>", normal_style))
            elements.append(Paragraph(contenido, normal_style))
            elements.append(Spacer(1, 8))
    
    # Información del generador del reporte
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Información del Reporte", subtitle_style))
    
    usuario_generador = pdf_data["usuario_generador"]
    fecha_generacion = pdf_data["fecha_generacion"]
    
    info_reporte = [
        ["Generado por:", f"{usuario_generador.first_name} {usuario_generador.last_name} ({usuario_generador.username})"],
        ["Fecha de Generación:", fecha_generacion.strftime('%d/%m/%Y %H:%M:%S')],
        ["Sistema:", "PACIFICO - Sistema de Workflow"]
    ]
    
    reporte_table = Table(info_reporte, colWidths=[2*inch, 3*inch])
    reporte_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    
    elements.append(reporte_table)
    
    # Construir PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer


# ==========================================
# PDF RESULTADO COMITÉ API
# ==========================================

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def api_pdf_resultado_comite(request, solicitud_id):
    """
    API para generar PDF con el resultado del comité de análisis usando xhtml2pdf
    """
    try:
        # Check if xhtml2pdf is available
        if not XHTML2PDF_AVAILABLE:
            return JsonResponse({
                "success": False,
                "error": "xhtml2pdf library is not available. Please install it with: pip install xhtml2pdf"
            }, status=500)
        
        # Obtener solicitud
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Parsear datos del request
        data = json.loads(request.body) if request.body else {}
        
        # Import required modules
        from django.template.loader import render_to_string
        from django.utils import timezone
        
        # Obtener calificaciones existentes de la base de datos
        calificaciones = CalificacionCampo.objects.filter(solicitud=solicitud)
        
        # Obtener comentarios de analista
        comentarios_analista = SolicitudComentario.objects.filter(
            solicitud=solicitud,
            tipo="analista_credito"
        ).order_by("-fecha_creacion")
        
        # Obtener el comentario más reciente del analista
        # Priorizar CalificacionCampo con campo 'comentario_analista_credito'
        analyst_comment = ""
        
        # Primero, buscar en CalificacionCampo
        calificacion_analista = CalificacionCampo.objects.filter(
            solicitud=solicitud,
            campo='comentario_analista_credito'
        ).exclude(comentario__isnull=True).exclude(comentario='').first()
        
        if calificacion_analista and calificacion_analista.comentario:
            analyst_comment = calificacion_analista.comentario
        elif comentarios_analista.exists():
            # Fallback a SolicitudComentario si no hay CalificacionCampo
            first_comment = comentarios_analista.first()
            if first_comment:
                analyst_comment = first_comment.comentario
        
        # Obtener resultado de análisis
        # Priorizar solicitud.resultado_consulta sobre subestado_actual.nombre
        resultado_analisis = ""
        if solicitud.resultado_consulta:
            resultado_analisis = solicitud.resultado_consulta
        elif solicitud.subestado_actual:
            resultado_analisis = solicitud.subestado_actual.nombre
        
        # Obtener participaciones del comité
        from .modelsWorkflow import ParticipacionComite, NivelComite
        participaciones_comite = ParticipacionComite.objects.filter(
            solicitud=solicitud
        ).select_related('usuario', 'nivel').order_by('nivel__orden', 'fecha_modificacion')
        
        # Obtener field values desde los datos del request
        field_values = data.get('field_values', {})
        
        # Crear lista enriquecida de calificaciones con valores
        calificaciones_with_values = []
        for cal in calificaciones:
            field_value = field_values.get(cal.campo, '')
            cal_dict = {
                'campo': cal.campo,
                'campo_legible': getattr(cal, 'campo_legible', None),
                'estado': cal.estado,
                'comentario': cal.comentario,
                'field_value': field_value,
            }
            calificaciones_with_values.append(cal_dict)
        
        # Preparar contexto para el template
        context = {
            'solicitud': solicitud,
            'calificaciones': calificaciones_with_values,
            'comentarios_analista': comentarios_analista,
            'participaciones_comite': participaciones_comite,
            'analyst_comment': analyst_comment,
            'resultado_analisis': resultado_analisis,
            'field_values': field_values,  # Keep for backward compatibility
            'committee_comment': data.get('committee_comment', ''),
            'compliance_ratings': data.get('compliance_ratings', []),
            'usuario_generador': request.user,
            'fecha_generacion': timezone.now(),
        }
        
        # Renderizar HTML usando el template simple (evita problemas con fuentes externas)
        html_string = render_to_string('workflow/pdf_resultado_consulta_simple.html', context)
        
        # Generar PDF con xhtml2pdf
        pdf_buffer = io.BytesIO()
        pisa_status = pisa.pisaDocument(io.StringIO(html_string), pdf_buffer)
        
        if pisa_status.err:
            return JsonResponse({
                "success": False,
                "error": "Error al generar PDF con xhtml2pdf"
            }, status=500)
        
        # Obtener contenido del PDF
        pdf_content = pdf_buffer.getvalue()
        pdf_buffer.close()
        
        if not pdf_content:
            return JsonResponse({
                "success": False,
                "error": "PDF generado está vacío"
            }, status=500)
        
        # Preparar respuesta
        response = HttpResponse(pdf_content, content_type="application/pdf")
        filename = f"Resultado_Comite_{solicitud.codigo}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response["Content-Disposition"] = f"attachment; filename=\"{filename}\""
        
        return response
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            "success": False,
            "error": "Solicitud no encontrada"
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            "success": False,
            "error": "Datos JSON inválidos"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": f"Error interno: {str(e)}"
        }, status=500)


# ==========================================================
# APIS PARA PENDIENTES ANTES DE FIRMA
# ==========================================================

@login_required
@require_http_methods(["GET"])
def api_buscar_pendientes_catalogo(request):
    """
    API para buscar pendientes en el catálogo
    """
    try:
        query = request.GET.get('q', '').strip()
        
        # Filtrar pendientes activos
        pendientes = CatalogoPendienteAntesFirma.objects.filter(activo=True)
        
        # Si hay término de búsqueda, filtrar
        if query:
            pendientes = pendientes.filter(
                Q(nombre__icontains=query) |
                Q(descripcion__icontains=query)
            )
        
        # Ordenar por orden y nombre
        pendientes = pendientes.order_by('orden', 'nombre')[:20]  # Limitar a 20 resultados
        
        pendientes_data = []
        for pendiente in pendientes:
            pendientes_data.append({
                'id': pendiente.id,
                'nombre': pendiente.nombre,
                'descripcion': pendiente.descripcion,
                'orden': pendiente.orden
            })
        
        return JsonResponse({
            'success': True,
            'pendientes': pendientes_data,
            'total': len(pendientes_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al buscar pendientes: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def api_obtener_pendientes_solicitud(request, solicitud_id):
    """
    API para obtener los pendientes de una solicitud específica
    """
    try:
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        pendientes = PendienteSolicitud.objects.filter(
            solicitud=solicitud
        ).select_related(
            'pendiente', 'agregado_por', 'completado_por', 'ultima_modificacion_por'
        ).order_by('-fecha_agregado')
        
        pendientes_data = []
        for pendiente in pendientes:
            pendientes_data.append({
                'id': pendiente.id,
                'pendiente': {
                    'id': pendiente.pendiente.id,
                    'nombre': pendiente.pendiente.nombre,
                    'descripcion': pendiente.pendiente.descripcion
                },
                'estado': pendiente.estado,
                'estado_display': pendiente.get_estado_display(),
                'agregado_por': {
                    'id': pendiente.agregado_por.id,
                    'username': pendiente.agregado_por.username,
                    'nombre_completo': f"{pendiente.agregado_por.first_name} {pendiente.agregado_por.last_name}".strip() or pendiente.agregado_por.username
                },
                'fecha_agregado': pendiente.fecha_agregado.isoformat(),
                'fecha_agregado_display': pendiente.fecha_agregado.strftime('%d/%m/%Y %H:%M'),
                'completado_por': {
                    'id': pendiente.completado_por.id,
                    'username': pendiente.completado_por.username,
                    'nombre_completo': f"{pendiente.completado_por.first_name} {pendiente.completado_por.last_name}".strip() or pendiente.completado_por.username
                } if pendiente.completado_por else None,
                'fecha_completado': pendiente.fecha_completado.isoformat() if pendiente.fecha_completado else None,
                'fecha_completado_display': pendiente.fecha_completado.strftime('%d/%m/%Y %H:%M') if pendiente.fecha_completado else None,
                'etapa_agregado': pendiente.etapa_agregado,
                'subestado_agregado': pendiente.subestado_agregado,
                'notas': pendiente.notas,
                'esta_completado': pendiente.esta_completado
            })
        
        return JsonResponse({
            'success': True,
            'pendientes': pendientes_data,
            'total': len(pendientes_data),
            'solicitud_codigo': solicitud.codigo
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener pendientes: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_agregar_pendiente_solicitud(request, solicitud_id):
    """
    API para agregar uno o varios pendientes a una solicitud
    """
    try:
        import json
        data = json.loads(request.body)
        
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        pendientes_ids = data.get('pendientes_ids', [])
        
        if not pendientes_ids:
            return JsonResponse({
                'success': False,
                'error': 'Debe seleccionar al menos un pendiente'
            }, status=400)
        
        # Verificar que los pendientes existan y estén activos
        pendientes = CatalogoPendienteAntesFirma.objects.filter(
            id__in=pendientes_ids, 
            activo=True
        )
        
        if len(pendientes) != len(pendientes_ids):
            return JsonResponse({
                'success': False,
                'error': 'Algunos pendientes seleccionados no existen o no están activos'
            }, status=400)
        
        agregados = []
        duplicados = []
        
        for pendiente in pendientes:
            # Verificar si ya existe esta combinación
            if PendienteSolicitud.objects.filter(
                solicitud=solicitud, 
                pendiente=pendiente
            ).exists():
                duplicados.append(pendiente.nombre)
                continue
            
            # Crear el nuevo pendiente de solicitud
            pendiente_solicitud = PendienteSolicitud.objects.create(
                solicitud=solicitud,
                pendiente=pendiente,
                agregado_por=request.user,
                etapa_agregado=solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'Sin etapa',
                subestado_agregado=solicitud.subestado_actual.nombre if solicitud.subestado_actual else 'Sin subestado',
                ultima_modificacion_por=request.user
            )
            
            agregados.append({
                'id': pendiente_solicitud.id,
                'nombre': pendiente.nombre
            })
        
        mensaje = f"Se agregaron {len(agregados)} pendiente(s) correctamente."
        if duplicados:
            mensaje += f" Se omitieron {len(duplicados)} pendiente(s) ya existente(s): {', '.join(duplicados)}"
        
        return JsonResponse({
            'success': True,
            'message': mensaje,
            'agregados': agregados,
            'duplicados': duplicados
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Error en el formato de datos enviados'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al agregar pendientes: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_cambiar_estado_pendiente(request, pendiente_solicitud_id):
    """
    API para cambiar el estado de un pendiente de solicitud
    """
    try:
        import json
        data = json.loads(request.body)
        
        pendiente_solicitud = get_object_or_404(PendienteSolicitud, id=pendiente_solicitud_id)
        nuevo_estado = data.get('estado')
        notas = data.get('notas', '')
        
        # Validar el nuevo estado
        estados_validos = dict(PendienteSolicitud.ESTADO_CHOICES).keys()
        if nuevo_estado not in estados_validos:
            return JsonResponse({
                'success': False,
                'error': f'Estado inválido. Estados válidos: {list(estados_validos)}'
            }, status=400)
        
        # Actualizar el pendiente
        pendiente_solicitud.estado = nuevo_estado
        pendiente_solicitud.ultima_modificacion_por = request.user
        
        if notas:
            pendiente_solicitud.notas = notas
        
        # Si se marca como listo, establecer completado_por
        if nuevo_estado == 'listo':
            pendiente_solicitud.completado_por = request.user
        else:
            # Si cambia de listo a otro estado, limpiar datos de completado
            pendiente_solicitud.completado_por = None
            pendiente_solicitud.fecha_completado = None
        
        pendiente_solicitud.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Estado cambiado a "{pendiente_solicitud.get_estado_display()}" correctamente',
            'nuevo_estado': nuevo_estado,
            'nuevo_estado_display': pendiente_solicitud.get_estado_display(),
            'fecha_completado': pendiente_solicitud.fecha_completado.isoformat() if pendiente_solicitud.fecha_completado else None,
            'completado_por': {
                'username': pendiente_solicitud.completado_por.username,
                'nombre_completo': f"{pendiente_solicitud.completado_por.first_name} {pendiente_solicitud.completado_por.last_name}".strip() or pendiente_solicitud.completado_por.username
            } if pendiente_solicitud.completado_por else None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Error en el formato de datos enviados'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al cambiar estado: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_eliminar_pendiente_solicitud(request, pendiente_solicitud_id):
    """
    API para eliminar un pendiente de una solicitud
    """
    try:
        pendiente_solicitud = get_object_or_404(PendienteSolicitud, id=pendiente_solicitud_id)
        
        # Guardar información antes de eliminar
        pendiente_nombre = pendiente_solicitud.pendiente.nombre
        solicitud_codigo = pendiente_solicitud.solicitud.codigo
        
        # Eliminar el pendiente
        pendiente_solicitud.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Pendiente "{pendiente_nombre}" eliminado correctamente de la solicitud {solicitud_codigo}'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al eliminar pendiente: {str(e)}'
        }, status=500)


# ==========================================================
# VISTA PARA AGENDA DE FIRMA
# ==========================================================

@login_required
def agenda_firma_view(request):
    """
    Vista principal para la Agenda de Firma
    """
    try:
        # Por ahora, simplemente renderizamos un template básico
        # Más funcionalidad se agregará según las especificaciones
        
        context = {
            'titulo_pagina': 'Agenda de Firma',
            'usuario': request.user,
        }
        
        return render(request, 'workflow/agenda_firma.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar la agenda de firma: {str(e)}')
        return redirect('workflow:dashboard')


# ==========================================================
# APIs PARA AGENDA DE FIRMA
# ==========================================================

@login_required
def api_listar_citas_calendario(request):
    """
    API para obtener las citas del calendario en formato FullCalendar
    """
    try:
        # Obtener parámetros de fecha del calendario
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        
        # Filtrar citas por rango de fechas si se proporcionan
        citas = AgendaFirma.objects.select_related('solicitud', 'creado_por').all()
        if start_date and end_date:
            citas = citas.filter(
                fecha_hora__gte=start_date,
                fecha_hora__lte=end_date
            )
        
        # Convertir a formato FullCalendar
        eventos = []
        for cita in citas:
            try:
                # Validar que la cita tenga todos los datos necesarios
                if not cita.solicitud or not cita.creado_por:
                    continue
                
                eventos.append({
                    'id': cita.id,
                    'title': f'{cita.cliente_nombre} - {cita.solicitud.codigo}',
                    'start': cita.fecha_hora.isoformat(),
                    'end': (cita.fecha_hora + timedelta(hours=1)).isoformat(),  # 1 hora de duración
                    'backgroundColor': '#28a745',  # Verde para resaltar
                    'borderColor': '#1e7e34',
                    'textColor': '#ffffff',
                    'extendedProps': {
                        'solicitud_codigo': cita.solicitud.codigo or 'N/A',
                        'cliente_nombre': cita.cliente_nombre,
                        'cliente_cedula': cita.cliente_cedula,
                        'lugar_firma': cita.lugar_firma_display,
                        'comentarios': cita.comentarios or '',
                        'creado_por': cita.creado_por.username,
                        'tiene_pendientes': cita.tiene_pendientes
                    }
                })
            except Exception as item_error:
                # Si hay error con una cita específica, continuar con las demás
                print(f"Error procesando cita {cita.id}: {str(item_error)}")
                continue
        
        # FullCalendar siempre espera un array, nunca un objeto
        return JsonResponse(eventos, safe=False)
        
    except Exception as e:
        print(f"Error en api_listar_citas_calendario: {str(e)}")
        # IMPORTANTE: Siempre devolver array vacío, nunca un objeto con error
        # FullCalendar no puede manejar objetos de error
        return JsonResponse([], safe=False)


@login_required
def api_buscar_solicitudes_agenda(request):
    """
    API para buscar solicitudes en el autocomplete del modal
    """
    try:
        termino = request.GET.get('q', '').strip()
        if len(termino) < 2:
            return JsonResponse({'solicitudes': []})
        
        # Construir consulta más segura
        q_filters = Q(codigo__icontains=termino)
        
        # Agregar filtros solo si los campos existen y no son None
        try:
            q_filters |= Q(cliente__nombreCliente__icontains=termino)
            q_filters |= Q(cliente__cedulaCliente__icontains=termino)
        except:
            pass  # Ignorar si el campo no existe o hay error
            
        try:
            q_filters |= Q(cotizacion__nombreCliente__icontains=termino)
            q_filters |= Q(cotizacion__cedulaCliente__icontains=termino)
        except:
            pass  # Ignorar si el campo no existe o hay error
        
        # Ejecutar consulta con select_related para optimizar
        solicitudes = Solicitud.objects.select_related(
            'cliente', 'cotizacion', 'etapa_actual'
        ).filter(q_filters).distinct()[:10]
        
        resultados = []
        for solicitud in solicitudes:
            try:
                # Obtener información del cliente de forma segura
                cliente_nombre = "N/A"
                cliente_cedula = "N/A"
                
                # Priorizar información del cliente directo
                if solicitud.cliente:
                    if hasattr(solicitud.cliente, 'nombreCliente') and solicitud.cliente.nombreCliente:
                        cliente_nombre = solicitud.cliente.nombreCliente
                    if hasattr(solicitud.cliente, 'cedulaCliente') and solicitud.cliente.cedulaCliente:
                        cliente_cedula = solicitud.cliente.cedulaCliente
                # Fallback a cotización si no hay cliente directo
                elif solicitud.cotizacion:
                    if hasattr(solicitud.cotizacion, 'nombreCliente') and solicitud.cotizacion.nombreCliente:
                        cliente_nombre = solicitud.cotizacion.nombreCliente
                    if hasattr(solicitud.cotizacion, 'cedulaCliente') and solicitud.cotizacion.cedulaCliente:
                        cliente_cedula = solicitud.cotizacion.cedulaCliente
                
                # Obtener etapa actual de forma segura
                etapa_actual = "N/A"
                if solicitud.etapa_actual and hasattr(solicitud.etapa_actual, 'nombre'):
                    etapa_actual = solicitud.etapa_actual.nombre
                
                resultados.append({
                    'id': solicitud.id,
                    'codigo': solicitud.codigo or "N/A",
                    'cliente_nombre': cliente_nombre,
                    'cliente_cedula': cliente_cedula,
                    'etapa_actual': etapa_actual,
                    'display_text': f'{solicitud.codigo or "N/A"} - {cliente_nombre} ({cliente_cedula})'
                })
                
            except Exception as item_error:
                # Si hay error con una solicitud específica, continuar con las demás
                print(f"Error procesando solicitud {solicitud.id}: {str(item_error)}")
                continue
        
        return JsonResponse({'solicitudes': resultados})
        
    except Exception as e:
        print(f"Error en api_buscar_solicitudes_agenda: {str(e)}")
        # Siempre devolver la estructura esperada, incluso en caso de error
        return JsonResponse({
            'solicitudes': [],
            'error_message': f'Error al buscar solicitudes: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def api_crear_cita_firma(request):
    """
    API para crear una nueva cita de firma
    """
    try:
        data = json.loads(request.body)
        print(f"📅 Creando cita de firma - Datos recibidos: {data}")
        
        # Validar campos requeridos
        solicitud_id = data.get('solicitud_id')
        fecha_hora_str = data.get('fecha_hora')
        lugar_firma = data.get('lugar_firma')
        comentarios = data.get('comentarios', '')
        
        if not all([solicitud_id, fecha_hora_str, lugar_firma]):
            return JsonResponse({
                'success': False,
                'error': 'Todos los campos son obligatorios'
            }, status=400)
        
        # Validar solicitud
        try:
            solicitud = Solicitud.objects.get(id=solicitud_id)
        except Solicitud.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Solicitud no encontrada'
            }, status=404)
        
        # Parsear fecha y hora
        try:
            fecha_hora = datetime.fromisoformat(fecha_hora_str.replace('Z', '+00:00'))
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Formato de fecha inválido'
            }, status=400)
        
        # Crear la cita
        cita = AgendaFirma.objects.create(
            solicitud=solicitud,
            fecha_hora=fecha_hora,
            lugar_firma=lugar_firma,
            comentarios=comentarios,
            creado_por=request.user
        )
        print(f"✅ Cita creada exitosamente - ID: {cita.id}, Solicitud: {solicitud.id}")
        
        return JsonResponse({
            'success': True,
            'message': 'Cita creada exitosamente',
            'cita': {
                'id': cita.id,
                'title': f'{cita.cliente_nombre} - {cita.solicitud.codigo}',
                'start': cita.fecha_hora.isoformat(),
                'end': (cita.fecha_hora + timedelta(hours=1)).isoformat(),
                'backgroundColor': '#28a745',
                'borderColor': '#1e7e34',
                'textColor': '#ffffff'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al crear cita: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_editar_cita_firma(request, cita_id):
    """
    API para editar una cita de firma existente
    """
    try:
        # Solo admins pueden editar
        if not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para editar citas'
            }, status=403)
        
        data = json.loads(request.body)
        
        try:
            cita = AgendaFirma.objects.get(id=cita_id)
        except AgendaFirma.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Cita no encontrada'
            }, status=404)
        
        # Actualizar campos si se proporcionan
        if 'fecha_hora' in data:
            try:
                cita.fecha_hora = datetime.fromisoformat(data['fecha_hora'].replace('Z', '+00:00'))
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de fecha inválido'
                }, status=400)
        
        if 'lugar_firma' in data:
            cita.lugar_firma = data['lugar_firma']
        
        if 'comentarios' in data:
            cita.comentarios = data['comentarios']
        
        # Actualizar auditoría
        cita.modificado_por = request.user
        cita.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Cita actualizada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al editar cita: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def api_eliminar_cita_firma(request, cita_id):
    """
    API para eliminar una cita de firma
    """
    try:
        # Solo admins pueden eliminar
        if not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'error': 'No tienes permisos para eliminar citas'
            }, status=403)
        
        try:
            cita = AgendaFirma.objects.get(id=cita_id)
            cita_info = f'{cita.solicitud.codigo} - {cita.cliente_nombre}'
            cita.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Cita {cita_info} eliminada exitosamente'
            })
            
        except AgendaFirma.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Cita no encontrada'
            }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al eliminar cita: {str(e)}'
        }, status=500)


@login_required
def api_obtener_cita_firma(request, cita_id):
    """
    API para obtener detalles de una cita específica
    """
    try:
        cita = get_object_or_404(AgendaFirma, id=cita_id)
        
        return JsonResponse({
            'success': True,
            'cita': {
                'id': cita.id,
                'solicitud': {
                    'id': cita.solicitud.id,
                    'codigo': cita.solicitud.codigo,
                    'cliente_nombre': cita.cliente_nombre,
                    'cliente_cedula': cita.cliente_cedula
                },
                'fecha_hora': cita.fecha_hora.isoformat(),
                'lugar_firma': cita.lugar_firma,
                'lugar_firma_display': cita.lugar_firma_display,
                'comentarios': cita.comentarios,
                'creado_por': cita.creado_por.username,
                'fecha_creacion': cita.fecha_creacion.isoformat(),
                'tiene_pendientes': cita.tiene_pendientes
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener cita: {str(e)}'
        }, status=500)


@login_required
def api_obtener_citas_solicitud(request, solicitud_id):
    """
    API para obtener todas las citas de AgendaFirma de una solicitud específica
    """
    try:
        # Verificar que la solicitud existe
        solicitud = Solicitud.objects.get(id=solicitud_id)
        
        # Obtener todas las citas de esta solicitud
        citas = AgendaFirma.objects.filter(
            solicitud=solicitud
        ).select_related('creado_por', 'modificado_por').order_by('-fecha_hora')
        
        # Convertir a formato JSON
        citas_data = []
        for cita in citas:
            citas_data.append({
                'id': cita.id,
                'fecha_hora': cita.fecha_hora.isoformat(),
                'fecha_formateada': cita.fecha_formateada,
                'lugar_firma': cita.lugar_firma,
                'lugar_firma_display': cita.lugar_firma_display,
                'comentarios': cita.comentarios,
                'creado_por': {
                    'username': cita.creado_por.username,
                    'nombre_completo': f"{cita.creado_por.first_name} {cita.creado_por.last_name}".strip() or cita.creado_por.username
                },
                'fecha_creacion': cita.fecha_creacion.isoformat(),
                'modificado_por': {
                    'username': cita.modificado_por.username if cita.modificado_por else None,
                    'nombre_completo': f"{cita.modificado_por.first_name} {cita.modificado_por.last_name}".strip() if cita.modificado_por else None
                } if cita.modificado_por else None,
                'fecha_modificacion': cita.fecha_modificacion.isoformat() if cita.fecha_modificacion else None,
                'tiene_pendientes': cita.tiene_pendientes,
                'solicitud_codigo': cita.solicitud_codigo,
                'cliente_nombre': cita.cliente_nombre,
                'cliente_cedula': cita.cliente_cedula
            })
        
        return JsonResponse({
            'success': True,
            'citas': citas_data,
            'total': len(citas_data),
            'solicitud': {
                'id': solicitud.id,
                'codigo': solicitud.codigo
            }
        })
        
    except Solicitud.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Solicitud no encontrada'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al obtener las citas: {str(e)}'
        }, status=500)


# ==========================================================
# VISTA PARA PENDIENTES Y ERRORES  
# ==========================================================

@login_required
def pendientes_errores_view(request):
    """
    Vista principal para el módulo de Pendientes y errores
    Muestra tres tablas: pendientes, errores y pendientes antes de firma
    """
    from django.core.paginator import Paginator
    from .models import CalificacionDocumentoBackoffice, RequisitoSolicitud
    from .modelsWorkflow import PendienteSolicitud
    
    try:
        # Obtener datos para tabla de pendientes (documentos pendientes)
        pendientes_query = CalificacionDocumentoBackoffice.objects.filter(
            estado='pendiente',
            requisito_solicitud__solicitud__isnull=False
        ).select_related(
            'requisito_solicitud',
            'requisito_solicitud__solicitud',
            'requisito_solicitud__requisito',
            'calificado_por'
        ).order_by('-fecha_calificacion')

        # Obtener datos para tabla de errores (documentos marcados como malo)
        errores_query = CalificacionDocumentoBackoffice.objects.filter(
            estado='malo',
            requisito_solicitud__solicitud__isnull=False
        ).select_related(
            'requisito_solicitud',
            'requisito_solicitud__solicitud', 
            'requisito_solicitud__requisito',
            'calificado_por',
            'subsanado_por'
        ).order_by('-fecha_calificacion')

        # Obtener datos para tabla de pendientes antes de firma
        pendientes_firma_query = PendienteSolicitud.objects.filter(
            estado__in=['por_hacer', 'haciendo']
        ).select_related(
            'solicitud',
            'pendiente',
            'agregado_por',
            'completado_por'
        ).order_by('-fecha_agregado')

        # Paginación para pendientes
        pendientes_paginator = Paginator(pendientes_query, 10)
        pendientes_page = request.GET.get('pendientes_page', 1)
        pendientes = pendientes_paginator.get_page(pendientes_page)

        # Paginación para errores  
        errores_paginator = Paginator(errores_query, 10)
        errores_page = request.GET.get('errores_page', 1)
        errores = errores_paginator.get_page(errores_page)

        # Paginación para pendientes antes de firma
        pendientes_firma_paginator = Paginator(pendientes_firma_query, 10)
        pendientes_firma_page = request.GET.get('pendientes_firma_page', 1)
        pendientes_firma = pendientes_firma_paginator.get_page(pendientes_firma_page)

        context = {
            'titulo_pagina': 'Pendientes y errores',
            'usuario': request.user,
            'pendientes': pendientes,
            'errores': errores,
            'pendientes_firma': pendientes_firma,
            'total_pendientes': pendientes_query.count(),
            'total_errores': errores_query.count(),
            'total_pendientes_firma': pendientes_firma_query.count(),
        }
        
        return render(request, 'workflow/pendientes_errores.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar pendientes y errores: {str(e)}')
        return redirect('workflow:dashboard')


# ==========================================================
# VISTAS AJAX PARA ORDEN DE EXPEDIENTE
# ==========================================================

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def actualizar_documento_orden(request):
    """Vista AJAX para actualizar el estado de un documento en el orden de expediente"""
    from .modelsWorkflow import OrdenExpediente
    import json
    
    try:
        data = json.loads(request.body)
        documento_id = data.get('documento_id')
        tiene_documento = data.get('tiene_documento', False)
        
        print(f"📝 Actualizando documento ID: {documento_id}, Estado: {tiene_documento}")
        
        documento = get_object_or_404(OrdenExpediente, id=documento_id)
        
        # Verificar permisos (usuario debe tener acceso a la solicitud)
        if not documento.solicitud.asignada_a == request.user:
            # Verificar si es bandeja grupal y el usuario tiene permisos
            if not (documento.solicitud.etapa_actual and 
                   documento.solicitud.etapa_actual.es_bandeja_grupal):
                return JsonResponse({'success': False, 'error': 'Sin permisos'}, status=403)
        
        # Actualizar documento - CRÍTICO: Guardar ambos cambios
        documento.tiene_documento = tiene_documento
        documento.calificado_por = request.user
        documento.fecha_calificacion = timezone.now()
        documento.save()  # Guardar TODOS los cambios
        
        print(f"✅ Documento guardado: ID {documento_id}, tiene_documento={documento.tiene_documento}")
        
        return JsonResponse({
            'success': True,
            'documento_id': documento_id,
            'tiene_documento': documento.tiene_documento,
            'estado_display': documento.estado_display,
            'css_class': documento.css_class,
            'message': f'Documento {"marcado como presente" if tiene_documento else "marcado como faltante"}'
        })
        
    except Exception as e:
        print(f"❌ Error al actualizar documento: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def actualizar_orden_documentos(request):
    """Vista AJAX para actualizar el orden de los documentos mediante drag & drop"""
    from .modelsWorkflow import OrdenExpediente
    import json
    
    try:
        data = json.loads(request.body)
        documentos_orden = data.get('documentos_orden', [])
        
        if not documentos_orden:
            return JsonResponse({'success': False, 'error': 'No se recibieron datos'})
        
        # Actualizar orden de cada documento
        for idx, documento_data in enumerate(documentos_orden):
            documento_id = documento_data.get('id')
            nuevo_orden = idx + 1
            
            documento = get_object_or_404(OrdenExpediente, id=documento_id)
            
            # Verificar permisos
            if not documento.solicitud.asignada_a == request.user:
                if not (documento.solicitud.etapa_actual and 
                       documento.solicitud.etapa_actual.es_bandeja_grupal):
                    return JsonResponse({'success': False, 'error': 'Sin permisos'}, status=403)
            
            documento.orden = nuevo_orden
            documento.marcar_calificado(request.user)
        
        return JsonResponse({'success': True, 'message': 'Orden actualizado correctamente'})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def agregar_comentario_documento(request):
    """Vista AJAX para agregar comentario a un documento"""
    from .modelsWorkflow import OrdenExpediente
    import json
    
    try:
        data = json.loads(request.body)
        documento_id = data.get('documento_id')
        comentario = data.get('comentario', '').strip()
        
        documento = get_object_or_404(OrdenExpediente, id=documento_id)
        
        # Verificar permisos
        if not documento.solicitud.asignada_a == request.user:
            if not (documento.solicitud.etapa_actual and 
                   documento.solicitud.etapa_actual.es_bandeja_grupal):
                return JsonResponse({'success': False, 'error': 'Sin permisos'}, status=403)
        
        # Actualizar comentario
        documento.comentarios = comentario
        documento.marcar_calificado(request.user)
        
        return JsonResponse({
            'success': True,
            'documento_id': documento_id,
            'comentario': documento.comentarios,
            'calificado_por': documento.calificado_por.get_full_name() if documento.calificado_por else None,
            'fecha_calificacion': documento.fecha_calificacion.strftime('%d/%m/%Y %H:%M') if documento.fecha_calificacion else None
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
@csrf_exempt
def obtener_comentario_documento(request, documento_id):
    """Vista AJAX para obtener el comentario de un documento"""
    from .modelsWorkflow import OrdenExpediente
    
    try:
        documento = get_object_or_404(OrdenExpediente, id=documento_id)
        
        # Verificar permisos de lectura
        if not documento.solicitud.asignada_a == request.user:
            if not (documento.solicitud.etapa_actual and 
                   documento.solicitud.etapa_actual.es_bandeja_grupal):
                return JsonResponse({'success': False, 'error': 'Sin permisos'}, status=403)
        
        return JsonResponse({
            'success': True,
            'documento_id': documento_id,
            'nombre_documento': documento.nombre_documento,
            'comentario': documento.comentarios or '',
            'calificado_por': documento.calificado_por.get_full_name() if documento.calificado_por else None,
            'fecha_calificacion': documento.fecha_calificacion.strftime('%d/%m/%Y %H:%M') if documento.fecha_calificacion else None
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def marcar_todos_documentos(request):
    """Vista AJAX para marcar o desmarcar todos los documentos de una vez"""
    from .modelsWorkflow import OrdenExpediente
    import json
    
    try:
        data = json.loads(request.body)
        solicitud_id = data.get('solicitud_id')
        marcar_todos = data.get('marcar_todos', True)
        
        solicitud = get_object_or_404(Solicitud, id=solicitud_id)
        
        # Verificar permisos
        if not solicitud.asignada_a == request.user:
            if not (solicitud.etapa_actual and 
                   solicitud.etapa_actual.es_bandeja_grupal):
                return JsonResponse({'success': False, 'error': 'Sin permisos'}, status=403)
        
        # Actualizar todos los documentos
        documentos = OrdenExpediente.objects.filter(solicitud=solicitud, activo=True)
        count = 0
        for documento in documentos:
            documento.tiene_documento = marcar_todos
            documento.marcar_calificado(request.user)
            count += 1
        
        return JsonResponse({
            'success': True, 
            'message': f'{"Marcados" if marcar_todos else "Desmarcados"} {count} documentos',
            'documentos_actualizados': count
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

