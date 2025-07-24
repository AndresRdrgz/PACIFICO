#!/usr/bin/env python
"""
Script de diagnóstico para debuggear el envío de correo APC iniciado
"""

import os
import sys
import django
import json

# Configurar Django
sys.path.append('c:\\Users\\arodriguez\\Documents\\GitHub\\PACIFICO')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.models import Solicitud
from workflow.views_workflow import enviar_correo_apc_iniciado
from django.utils import timezone

def simulate_api_call():
    """
    Simula exactamente la llamada API que está fallando
    """
    print("🔍 Diagnóstico: APC Email 'in_progress' no se envía")
    print("=" * 60)
    
    # Buscar la solicitud FLU-101
    try:
        solicitud = Solicitud.objects.get(codigo='FLU-101', descargar_apc_makito=True)
        print(f"✅ Solicitud encontrada: {solicitud.codigo}")
        print(f"   Cliente: {solicitud.cliente_nombre or 'Sin cliente'}")
        print(f"   Creada por: {solicitud.creada_por.username} ({solicitud.creada_por.email})")
        print(f"   Asignada a: {solicitud.asignada_a.username if solicitud.asignada_a else 'Sin asignar'}")
        print(f"   APC Status actual: {solicitud.apc_status}")
        print(f"   APC Fecha inicio: {solicitud.apc_fecha_inicio}")
        
    except Solicitud.DoesNotExist:
        print("❌ Solicitud FLU-101 no encontrada o no tiene APC habilitado")
        # Buscar cualquier solicitud con APC habilitado
        solicitud = Solicitud.objects.filter(descargar_apc_makito=True).first()
        if not solicitud:
            print("❌ No hay solicitudes con APC habilitado en el sistema")
            return
        print(f"✅ Usando solicitud alternativa: {solicitud.codigo}")
    
    # Simular el proceso de actualización de estado
    print("\n🔄 Simulando actualización de estado...")
    
    # Datos de la API call
    nuevo_status = 'in_progress'
    observaciones = 'Iniciando procesamiento del APC'
    
    print(f"   Nuevo status: {nuevo_status}")
    print(f"   Observaciones: {observaciones}")
    
    # Verificar condiciones para envío de correo
    print("\n🔍 Verificando condiciones para envío de correo...")
    
    # Guardar valores originales
    original_status = solicitud.apc_status
    original_fecha_inicio = solicitud.apc_fecha_inicio
    original_observaciones = solicitud.apc_observaciones
    
    try:
        # Simular la lógica de la API
        solicitud.apc_status = nuevo_status
        solicitud.apc_observaciones = observaciones
        
        now = timezone.now()
        fields_to_update = ['apc_status', 'apc_observaciones']
        
        # Esta es la condición clave que determina si se envía el correo
        should_send_email = nuevo_status == 'in_progress' and not solicitud.apc_fecha_inicio
        
        print(f"   Status será: {nuevo_status}")
        print(f"   apc_fecha_inicio actual: {solicitud.apc_fecha_inicio}")
        print(f"   Condición 1 (status == 'in_progress'): {nuevo_status == 'in_progress'}")
        print(f"   Condición 2 (not apc_fecha_inicio): {not solicitud.apc_fecha_inicio}")
        print(f"   ¿Debería enviar correo?: {should_send_email}")
        
        if should_send_email:
            solicitud.apc_fecha_inicio = now
            fields_to_update.append('apc_fecha_inicio')
            print(f"   ✅ Se establecería apc_fecha_inicio: {now}")
            print(f"   ✅ 'apc_fecha_inicio' se agregaría a fields_to_update")
            
            # Verificar que la función de envío de correo existe
            print("\n📧 Verificando función de envío de correo...")
            try:
                print("   ✅ Función enviar_correo_apc_iniciado importada correctamente")
                
                # Verificar datos del usuario
                print(f"\n👤 Datos del usuario que creó la solicitud:")
                print(f"   Username: {solicitud.creada_por.username}")
                print(f"   Email: {solicitud.creada_por.email}")
                print(f"   Nombre completo: {solicitud.creada_por.get_full_name()}")
                
                if solicitud.asignada_a and solicitud.asignada_a != solicitud.creada_por:
                    print(f"\n👤 Usuario asignado (adicional):")
                    print(f"   Username: {solicitud.asignada_a.username}")
                    print(f"   Email: {solicitud.asignada_a.email}")
                
                # Verificar emails válidos
                usuarios_notificar = [solicitud.creada_por]
                if solicitud.asignada_a and solicitud.asignada_a != solicitud.creada_por:
                    usuarios_notificar.append(solicitud.asignada_a)
                
                destinatarios = []
                for usuario in usuarios_notificar:
                    if usuario.email:
                        destinatarios.append(usuario.email)
                
                print(f"\n📮 Destinatarios de correo:")
                print(f"   Emails válidos: {destinatarios}")
                print(f"   ¿Hay destinatarios?: {len(destinatarios) > 0}")
                
                if destinatarios:
                    print("\n🧪 Intentando enviar correo de prueba...")
                    
                    # Probar el envío del correo
                    enviar_correo_apc_iniciado(solicitud)
                    print("   ✅ Correo enviado exitosamente!")
                    
                else:
                    print("   ❌ No hay destinatarios válidos para enviar correo")
                
            except Exception as e:
                print(f"   ❌ Error al probar envío de correo: {str(e)}")
                import traceback
                print(f"   Traceback: {traceback.format_exc()}")
        
        else:
            print("   ❌ Las condiciones no se cumplen para enviar correo")
            if nuevo_status != 'in_progress':
                print(f"      - Status no es 'in_progress': {nuevo_status}")
            if solicitud.apc_fecha_inicio:
                print(f"      - Ya tiene apc_fecha_inicio: {solicitud.apc_fecha_inicio}")
    
    finally:
        # Restaurar valores originales (no guardar en BD)
        solicitud.apc_status = original_status
        solicitud.apc_fecha_inicio = original_fecha_inicio
        solicitud.apc_observaciones = original_observaciones
        print(f"\n🔄 Valores originales restaurados (no se guardó en BD)")
    
    print("\n🎯 Análisis completado!")

if __name__ == '__main__':
    simulate_api_call()
