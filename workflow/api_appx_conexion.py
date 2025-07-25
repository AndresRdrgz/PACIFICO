"""
API para integración con sistema APPX Core - Financiera Pacífico
Maneja el envío de entrevistas de clientes al sistema central
"""
import requests
import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import ClienteEntrevista

# Configurar logging
logger = logging.getLogger(__name__)

# Configuración del endpoint APPX
APPX_ENDPOINT = "http://192.168.1.7:3000/api/recibecotbase"
APPX_TIMEOUT = 30  # segundos

# Endpoint de prueba para desarrollo (cuando APPX no esté disponible)
APPX_TEST_MODE = True  # Cambiar a False en producción

def formatear_datos_entrevista_para_appx(entrevista):
    """
    Agrupa y formatea los datos de la entrevista por secciones para envío a APPX
    """
    try:
        # SECCIÓN 1: DATOS PERSONALES
        datos_personales = {
            "primer_nombre": entrevista.primer_nombre or "",
            "segundo_nombre": entrevista.segundo_nombre or "",
            "primer_apellido": entrevista.primer_apellido or "",
            "segundo_apellido": entrevista.segundo_apellido or "",
            "apellido_casada": entrevista.apellido_casada or "",
            "cedula_completa": f"{entrevista.provincia_cedula or ''}-{entrevista.tipo_letra or ''}-{entrevista.tomo_cedula or ''}-{entrevista.partida_cedula or ''}",
            "provincia_cedula": entrevista.provincia_cedula or "",
            "tipo_letra": entrevista.tipo_letra or "",
            "tomo_cedula": entrevista.tomo_cedula or "",
            "partida_cedula": entrevista.partida_cedula or "",
            "fecha_nacimiento": entrevista.fecha_nacimiento.strftime('%Y-%m-%d') if entrevista.fecha_nacimiento else "",
            "sexo": entrevista.sexo or "",
            "estado_civil": entrevista.estado_civil or "",
            "nacionalidad": entrevista.nacionalidad or "",
            "lugar_nacimiento": entrevista.lugar_nacimiento or "",
            "nivel_academico": entrevista.nivel_academico or "",
            "titulo": entrevista.titulo or "",
            "no_dependientes": entrevista.no_dependientes or 0,
            "peso": str(entrevista.peso) if entrevista.peso else "",
            "estatura": str(entrevista.estatura) if entrevista.estatura else "",
            "jubilado": entrevista.jubilado or False
        }
        
        # SECCIÓN 2: DATOS DE CONTACTO
        datos_contacto = {
            "telefono": entrevista.telefono or "",
            "email": entrevista.email or "",
            "direccion_completa": entrevista.direccion_completa or "",
            "barrio": entrevista.barrio or "",
            "calle": entrevista.calle or "",
            "casa_apto": entrevista.casa_apto or ""
        }
        
        # SECCIÓN 3: DATOS DEL CÓNYUGE
        datos_conyuge = {
            "conyuge_nombre": entrevista.conyuge_nombre or "",
            "conyuge_cedula": entrevista.conyuge_cedula or "",
            "conyuge_lugar_trabajo": entrevista.conyuge_lugar_trabajo or "",
            "conyuge_cargo": entrevista.conyuge_cargo or "",
            "conyuge_ingreso": str(entrevista.conyuge_ingreso) if entrevista.conyuge_ingreso else "",
            "conyuge_telefono": entrevista.conyuge_telefono or ""
        }
        
        # SECCIÓN 4: DATOS LABORALES
        datos_laborales = {
            "trabajo_direccion": entrevista.trabajo_direccion or "",
            "trabajo_lugar": entrevista.trabajo_lugar or "",
            "trabajo_cargo": entrevista.trabajo_cargo or "",
            "salario": str(entrevista.salario) if entrevista.salario else "",
            "tipo_trabajo": entrevista.tipo_trabajo or "",
            "frecuencia_pago": entrevista.frecuencia_pago or "",
            "tel_trabajo": entrevista.tel_trabajo or "",
            "tel_ext": entrevista.tel_ext or "",
            "origen_fondos": entrevista.origen_fondos or "",
            "fecha_inicio_trabajo": entrevista.fecha_inicio_trabajo.strftime('%Y-%m-%d') if entrevista.fecha_inicio_trabajo else ""
        }
        
        # SECCIÓN 5: OTROS INGRESOS
        otros_ingresos = {
            "tipo_ingreso_1": entrevista.tipo_ingreso_1 or "",
            "descripcion_ingreso_1": entrevista.descripcion_ingreso_1 or "",
            "monto_ingreso_1": str(entrevista.monto_ingreso_1) if entrevista.monto_ingreso_1 else "",
            "tipo_ingreso_2": entrevista.tipo_ingreso_2 or "",
            "descripcion_ingreso_2": entrevista.descripcion_ingreso_2 or "",
            "monto_ingreso_2": str(entrevista.monto_ingreso_2) if entrevista.monto_ingreso_2 else "",
            "tipo_ingreso_3": entrevista.tipo_ingreso_3 or "",
            "descripcion_ingreso_3": entrevista.descripcion_ingreso_3 or "",
            "monto_ingreso_3": str(entrevista.monto_ingreso_3) if entrevista.monto_ingreso_3 else ""
        }
        
        # SECCIÓN 6: DATOS PEP
        datos_pep = {
            "es_pep": entrevista.es_pep or False,
            "pep_ingreso": str(entrevista.pep_ingreso) if entrevista.pep_ingreso else "",
            "pep_inicio": entrevista.pep_inicio.strftime('%Y-%m-%d') if entrevista.pep_inicio else "",
            "pep_cargo_actual": entrevista.pep_cargo_actual or "",
            "pep_fin": entrevista.pep_fin.strftime('%Y-%m-%d') if entrevista.pep_fin else "",
            "pep_cargo_anterior": entrevista.pep_cargo_anterior or "",
            "pep_fin_anterior": entrevista.pep_fin_anterior.strftime('%Y-%m-%d') if entrevista.pep_fin_anterior else "",
            "es_familiar_pep": entrevista.es_familiar_pep or False,
            "parentesco_pep": entrevista.parentesco_pep or "",
            "nombre_pep": entrevista.nombre_pep or "",
            "cargo_pep": entrevista.cargo_pep or "",
            "institucion_pep": entrevista.institucion_pep or "",
            "pep_fam_inicio": entrevista.pep_fam_inicio.strftime('%Y-%m-%d') if entrevista.pep_fam_inicio else "",
            "pep_fam_fin": entrevista.pep_fam_fin.strftime('%Y-%m-%d') if entrevista.pep_fam_fin else ""
        }
        
        # SECCIÓN 7: DATOS BANCARIOS
        datos_bancarios = {
            "banco": entrevista.banco or "",
            "tipo_cuenta": entrevista.tipo_cuenta or "",
            "numero_cuenta": entrevista.numero_cuenta or ""
        }
        
        # SECCIÓN 8: AUTORIZACIONES
        autorizaciones = {
            "autoriza_apc": entrevista.autoriza_apc or False,
            "acepta_datos": entrevista.acepta_datos or False,
            "es_beneficiario_final": entrevista.es_beneficiario_final or False
        }
        
        # SECCIÓN 9: PRODUCTO Y SISTEMA
        datos_producto = {
            "tipo_producto": entrevista.tipo_producto or "",
            "oficial": entrevista.oficial or "",
            "empresa": entrevista.empresa or "",
            "fecha_entrevista": entrevista.fecha_entrevista.strftime('%Y-%m-%d %H:%M:%S') if entrevista.fecha_entrevista else "",
            "completada_por_admin": entrevista.completada_por_admin or False,
            "fecha_completada_admin": entrevista.fecha_completada_admin.strftime('%Y-%m-%d %H:%M:%S') if entrevista.fecha_completada_admin else ""
        }
        
        # SECCIÓN 10: REFERENCIAS PERSONALES
        referencias_personales = []
        for ref in entrevista.referencias_personales.all():
            referencias_personales.append({
                "nombre": ref.nombre or "",
                "telefono": ref.telefono or "",
                "relacion": ref.relacion or "",
                "tiempo_conocerse": ref.tiempo_conocerse or "",
                "direccion": ref.direccion or ""
            })
        
        # SECCIÓN 11: REFERENCIAS COMERCIALES
        referencias_comerciales = []
        for ref in entrevista.referencias_comerciales.all():
            referencias_comerciales.append({
                "nombre_empresa": ref.nombre_empresa or "",
                "telefono": ref.telefono or "",
                "contacto": ref.contacto or "",
                "tipo_relacion": ref.tipo_relacion or "",
                "tiempo_relacion": ref.tiempo_relacion or ""
            })
        
        # SECCIÓN 12: OTROS INGRESOS (FORMSET)
        otros_ingresos_formset = []
        for ingreso in entrevista.otros_ingresos.all():
            otros_ingresos_formset.append({
                "tipo": ingreso.tipo or "",
                "descripcion": ingreso.descripcion or "",
                "monto": str(ingreso.monto) if ingreso.monto else ""
            })
        
        # Estructura final agrupada por secciones
        datos_agrupados = {
            "entrevista_id": entrevista.id,
            "datos_personales": datos_personales,
            "datos_contacto": datos_contacto,
            "datos_conyuge": datos_conyuge,
            "datos_laborales": datos_laborales,
            "otros_ingresos": otros_ingresos,
            "datos_pep": datos_pep,
            "datos_bancarios": datos_bancarios,
            "autorizaciones": autorizaciones,
            "datos_producto": datos_producto,
            "referencias_personales": referencias_personales,
            "referencias_comerciales": referencias_comerciales,
            "otros_ingresos_formset": otros_ingresos_formset,
            "metadatos": {
                "fecha_envio": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "version": "1.0",
                "origen": "PACIFICO_WEB"
            }
        }
        
        logger.info(f"Datos formateados exitosamente para entrevista {entrevista.id}")
        return datos_agrupados
        
    except Exception as e:
        logger.error(f"Error al formatear datos de entrevista {entrevista.id}: {str(e)}")
        raise


@csrf_exempt
@require_http_methods(["POST"])
def enviar_entrevista_a_appx(request, entrevista_id):
    """
    API para enviar una entrevista específica al sistema APPX Core
    """
    try:
        # Obtener la entrevista
        entrevista = get_object_or_404(ClienteEntrevista, id=entrevista_id)
        
        logger.info(f"Iniciando envío de entrevista {entrevista_id} a APPX Core")
        
        # Formatear datos
        datos_formateados = formatear_datos_entrevista_para_appx(entrevista)
        
        # Preparar headers para el request
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'PACIFICO-WEB/1.0'
        }
        
        # Enviar request POST al endpoint APPX
        logger.info(f"Enviando datos a {APPX_ENDPOINT}")
        
        # Si estamos en modo de prueba, simular respuesta exitosa
        if APPX_TEST_MODE:
            logger.info(f"MODO PRUEBA: Simulando envío exitoso para entrevista {entrevista_id}")
            return JsonResponse({
                'success': True,
                'message': f'[MODO PRUEBA] Entrevista de {entrevista.primer_nombre} {entrevista.primer_apellido} preparada para envío a APPX Core',
                'entrevista_id': entrevista_id,
                'datos_preparados': {
                    'total_secciones': 12,
                    'campos_enviados': len(str(datos_formateados)),
                    'endpoint_destino': APPX_ENDPOINT
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'modo': 'PRUEBA - APPX no conectado'
            })
        
        response = requests.post(
            APPX_ENDPOINT,
            json=datos_formateados,
            headers=headers,
            timeout=APPX_TIMEOUT
        )
        
        # Verificar respuesta
        if response.status_code == 200:
            logger.info(f"Entrevista {entrevista_id} enviada exitosamente a APPX Core")
            return JsonResponse({
                'success': True,
                'message': f'Entrevista de {entrevista.primer_nombre} {entrevista.primer_apellido} enviada exitosamente al sistema APPX Core',
                'entrevista_id': entrevista_id,
                'response_data': response.json() if response.content else None,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            logger.error(f"Error en respuesta de APPX: {response.status_code} - {response.text}")
            return JsonResponse({
                'success': False,
                'message': f'Error del sistema APPX: {response.status_code}',
                'error_details': response.text,
                'entrevista_id': entrevista_id
            }, status=400)
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout al enviar entrevista {entrevista_id} a APPX")
        return JsonResponse({
            'success': False,
            'message': 'Timeout: El sistema APPX no respondió en el tiempo esperado',
            'entrevista_id': entrevista_id
        }, status=408)
        
    except requests.exceptions.ConnectionError:
        logger.error(f"Error de conexión al enviar entrevista {entrevista_id} a APPX")
        return JsonResponse({
            'success': False,
            'message': 'Error de conexión: No se pudo conectar con el sistema APPX Core',
            'entrevista_id': entrevista_id
        }, status=503)
        
    except Exception as e:
        logger.error(f"Error inesperado al enviar entrevista {entrevista_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f'Error interno: {str(e)}',
            'entrevista_id': entrevista_id
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def verificar_conexion_appx(request):
    """
    Endpoint para verificar la conectividad con el sistema APPX Core
    """
    try:
        # Datos de prueba mínimos
        datos_prueba = {
            "test": True,
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "origen": "PACIFICO_WEB_TEST"
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'PACIFICO-WEB/1.0'
        }
        
        response = requests.post(
            APPX_ENDPOINT,
            json=datos_prueba,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return JsonResponse({
                'success': True,
                'message': 'Conexión con APPX Core exitosa',
                'response_time': 'OK',
                'endpoint': APPX_ENDPOINT
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'APPX Core respondió con error: {response.status_code}',
                'endpoint': APPX_ENDPOINT
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error de conexión con APPX Core: {str(e)}',
            'endpoint': APPX_ENDPOINT
        }, status=503)
