from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone
import json

from .modelsWorkflow import (
    Pipeline, PlantillaOrdenExpediente, CatalogoPendienteAntesFirma
)


def is_superuser(user):
    """Verificar que el usuario sea superusuario"""
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def admin_backoffice_view(request):
    """Vista principal del módulo de administración de Back Office"""
    return render(request, 'workflow/admin_backoffice.html')


# ==========================================================
# APIs PARA PIPELINES
# ==========================================================

@login_required
@user_passes_test(is_superuser)
@require_http_methods(["GET"])
def api_pipelines(request):
    """API para obtener todos los pipelines"""
    try:
        # Verificar que el modelo Pipeline existe
        from .modelsWorkflow import Pipeline
        
        pipelines = Pipeline.objects.all().order_by('nombre')
        
        pipelines_data = []
        for pipeline in pipelines:
            pipelines_data.append({
                'id': pipeline.id,
                'nombre': pipeline.nombre,
                'descripcion': getattr(pipeline, 'descripcion', '') or ''
            })
        
        return JsonResponse(pipelines_data, safe=False)
        
    except ImportError as e:
        return JsonResponse({
            'error': f'Error de importación: {str(e)}'
        }, status=500)
    except Exception as e:
        import traceback
        return JsonResponse({
            'error': f'Error al obtener pipelines: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)


# ==========================================================
# APIs PARA PLANTILLAS DE ORDEN DE EXPEDIENTE
# ==========================================================

@login_required
@user_passes_test(is_superuser)
@require_http_methods(["GET", "POST"])
@csrf_exempt
def api_plantillas_crud(request):
    """API CRUD para plantillas de orden de expediente"""
    if request.method == 'GET':
        return api_plantillas_list(request)
    elif request.method == 'POST':
        return api_plantillas_create(request)


def api_plantillas_list(request):
    """API para obtener todas las plantillas de orden de expediente"""
    try:
        plantillas = PlantillaOrdenExpediente.objects.select_related(
            'pipeline', 'creado_por'
        ).order_by('pipeline__nombre', 'orden_seccion', 'seccion', 'orden')
        
        plantillas_data = []
        for plantilla in plantillas:
            plantillas_data.append({
                'id': plantilla.id,
                'pipeline': plantilla.pipeline.id,
                'pipeline_nombre': plantilla.pipeline.nombre,
                'seccion': plantilla.seccion,
                'orden_seccion': plantilla.orden_seccion,
                'nombre_documento': plantilla.nombre_documento,
                'orden': plantilla.orden,
                'obligatorio': plantilla.obligatorio,
                'descripcion': plantilla.descripcion or '',
                'activo': plantilla.activo,
                'creado_por': plantilla.creado_por.get_full_name() if plantilla.creado_por else '',
                'creado_en': plantilla.creado_en.isoformat(),
                'actualizado_en': plantilla.actualizado_en.isoformat()
            })
        
        return JsonResponse(plantillas_data, safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener plantillas: {str(e)}'
        }, status=500)


def api_plantillas_create(request):
    """API para crear una nueva plantilla de orden de expediente"""
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        required_fields = ['pipeline', 'seccion', 'orden_seccion', 'nombre_documento', 'orden']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'error': f'El campo {field} es requerido'
                }, status=400)
        
        # Obtener pipeline
        try:
            pipeline = Pipeline.objects.get(id=data['pipeline'])
        except Pipeline.DoesNotExist:
            return JsonResponse({
                'error': 'Pipeline no encontrado'
            }, status=404)
        
        # Verificar si ya existe una plantilla con el mismo pipeline, sección y orden
        if PlantillaOrdenExpediente.objects.filter(
            pipeline=pipeline,
            seccion=data['seccion'],
            orden=data['orden']
        ).exists():
            return JsonResponse({
                'error': 'Ya existe una plantilla con este pipeline, sección y orden'
            }, status=400)
        
        # Crear plantilla
        plantilla = PlantillaOrdenExpediente.objects.create(
            pipeline=pipeline,
            seccion=data['seccion'],
            orden_seccion=int(data['orden_seccion']),
            nombre_documento=data['nombre_documento'],
            orden=int(data['orden']),
            obligatorio=data.get('obligatorio', True),
            descripcion=data.get('descripcion', ''),
            activo=data.get('activo', True),
            creado_por=request.user
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Plantilla creada exitosamente',
            'id': plantilla.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error al crear plantilla: {str(e)}'
        }, status=500)


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["PUT", "DELETE"])
@csrf_exempt
def api_plantillas_crud_detail(request, plantilla_id):
    """API CRUD para operaciones detalladas de plantillas"""
    if request.method == 'PUT':
        return api_plantillas_update(request, plantilla_id)
    elif request.method == 'DELETE':
        return api_plantillas_delete(request, plantilla_id)


def api_plantillas_update(request, plantilla_id):
    """API para actualizar una plantilla de orden de expediente"""
    try:
        plantilla = get_object_or_404(PlantillaOrdenExpediente, id=plantilla_id)
        data = json.loads(request.body)
        
        # Validar datos requeridos
        required_fields = ['pipeline', 'seccion', 'orden_seccion', 'nombre_documento', 'orden']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'error': f'El campo {field} es requerido'
                }, status=400)
        
        # Obtener pipeline
        try:
            pipeline = Pipeline.objects.get(id=data['pipeline'])
        except Pipeline.DoesNotExist:
            return JsonResponse({
                'error': 'Pipeline no encontrado'
            }, status=404)
        
        # Verificar si ya existe otra plantilla con el mismo pipeline, sección y orden
        existing = PlantillaOrdenExpediente.objects.filter(
            pipeline=pipeline,
            seccion=data['seccion'],
            orden=data['orden']
        ).exclude(id=plantilla_id)
        
        if existing.exists():
            return JsonResponse({
                'error': 'Ya existe otra plantilla con este pipeline, sección y orden'
            }, status=400)
        
        # Actualizar plantilla
        plantilla.pipeline = pipeline
        plantilla.seccion = data['seccion']
        plantilla.orden_seccion = int(data['orden_seccion'])
        plantilla.nombre_documento = data['nombre_documento']
        plantilla.orden = int(data['orden'])
        plantilla.obligatorio = data.get('obligatorio', True)
        plantilla.descripcion = data.get('descripcion', '')
        plantilla.activo = data.get('activo', True)
        plantilla.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Plantilla actualizada exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error al actualizar plantilla: {str(e)}'
        }, status=500)


def api_plantillas_delete(request, plantilla_id):
    """API para eliminar una plantilla de orden de expediente"""
    try:
        plantilla = get_object_or_404(PlantillaOrdenExpediente, id=plantilla_id)
        
        # En lugar de eliminar, marcar como inactivo por seguridad
        plantilla.activo = False
        plantilla.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Plantilla eliminada exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al eliminar plantilla: {str(e)}'
        }, status=500)


# ==========================================================
# APIs PARA CATÁLOGO PENDIENTES ANTES FIRMA
# ==========================================================

@login_required
@user_passes_test(is_superuser)
@require_http_methods(["GET", "POST"])
@csrf_exempt
def api_catalogos_crud(request):
    """API CRUD para catálogo de pendientes"""
    if request.method == 'GET':
        return api_catalogos_list(request)
    elif request.method == 'POST':
        return api_catalogos_create(request)


def api_catalogos_list(request):
    """API para obtener todos los pendientes del catálogo"""
    try:
        catalogos = CatalogoPendienteAntesFirma.objects.order_by('orden', 'nombre')
        
        catalogos_data = []
        for catalogo in catalogos:
            catalogos_data.append({
                'id': catalogo.id,
                'nombre': catalogo.nombre,
                'descripcion': catalogo.descripcion or '',
                'orden': catalogo.orden,
                'activo': catalogo.activo,
                'fecha_creacion': catalogo.fecha_creacion.isoformat(),
                'fecha_actualizacion': catalogo.fecha_actualizacion.isoformat()
            })
        
        return JsonResponse(catalogos_data, safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al obtener catálogos: {str(e)}'
        }, status=500)


def api_catalogos_create(request):
    """API para crear un nuevo pendiente en el catálogo"""
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        if not data.get('nombre'):
            return JsonResponse({
                'error': 'El nombre es requerido'
            }, status=400)
        
        # Verificar si ya existe un pendiente con el mismo nombre
        if CatalogoPendienteAntesFirma.objects.filter(nombre=data['nombre']).exists():
            return JsonResponse({
                'error': 'Ya existe un pendiente con este nombre'
            }, status=400)
        
        # Crear catálogo
        catalogo = CatalogoPendienteAntesFirma.objects.create(
            nombre=data['nombre'],
            descripcion=data.get('descripcion', ''),
            orden=int(data.get('orden', 0)),
            activo=data.get('activo', True)
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Pendiente creado exitosamente',
            'id': catalogo.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error al crear pendiente: {str(e)}'
        }, status=500)


@login_required
@user_passes_test(is_superuser)
@require_http_methods(["PUT", "DELETE"])
@csrf_exempt
def api_catalogos_crud_detail(request, catalogo_id):
    """API CRUD para operaciones detalladas de catálogos"""
    if request.method == 'PUT':
        return api_catalogos_update(request, catalogo_id)
    elif request.method == 'DELETE':
        return api_catalogos_delete(request, catalogo_id)


def api_catalogos_update(request, catalogo_id):
    """API para actualizar un pendiente del catálogo"""
    try:
        catalogo = get_object_or_404(CatalogoPendienteAntesFirma, id=catalogo_id)
        data = json.loads(request.body)
        
        # Validar datos requeridos
        if not data.get('nombre'):
            return JsonResponse({
                'error': 'El nombre es requerido'
            }, status=400)
        
        # Verificar si ya existe otro pendiente con el mismo nombre
        existing = CatalogoPendienteAntesFirma.objects.filter(
            nombre=data['nombre']
        ).exclude(id=catalogo_id)
        
        if existing.exists():
            return JsonResponse({
                'error': 'Ya existe otro pendiente con este nombre'
            }, status=400)
        
        # Actualizar catálogo
        catalogo.nombre = data['nombre']
        catalogo.descripcion = data.get('descripcion', '')
        catalogo.orden = int(data.get('orden', 0))
        catalogo.activo = data.get('activo', True)
        catalogo.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Pendiente actualizado exitosamente'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Datos JSON inválidos'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Error al actualizar pendiente: {str(e)}'
        }, status=500)


def api_catalogos_delete(request, catalogo_id):
    """API para eliminar un pendiente del catálogo"""
    try:
        catalogo = get_object_or_404(CatalogoPendienteAntesFirma, id=catalogo_id)
        
        # En lugar de eliminar, marcar como inactivo por seguridad
        catalogo.activo = False
        catalogo.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Pendiente eliminado exitosamente'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error al eliminar pendiente: {str(e)}'
        }, status=500)