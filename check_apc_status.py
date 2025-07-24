#!/usr/bin/env python
"""
Script para verificar el estado actual de la solicitud FLU-101
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:\\Users\\arodriguez\\Documents\\GitHub\\PACIFICO')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.models import Solicitud

def check_solicitud_status():
    """
    Verificar el estado actual de la solicitud
    """
    print("🔍 Verificando estado actual de solicitudes APC")
    print("=" * 50)
    
    # Buscar la solicitud FLU-101
    try:
        solicitud = Solicitud.objects.get(codigo='FLU-101')
        print(f"✅ Solicitud encontrada: {solicitud.codigo}")
    except Solicitud.DoesNotExist:
        print("❌ Solicitud FLU-101 no encontrada")
        print("Buscando otras solicitudes con APC habilitado...")
        solicitudes = Solicitud.objects.filter(descargar_apc_makito=True)[:5]
        for s in solicitudes:
            print(f"   - {s.codigo} (APC: {s.apc_status})")
        return
    
    print(f"📊 Estado actual de {solicitud.codigo}:")
    print(f"   APC habilitado: {solicitud.descargar_apc_makito}")
    print(f"   APC Status: {solicitud.apc_status}")
    print(f"   APC Fecha solicitud: {solicitud.apc_fecha_solicitud}")
    print(f"   APC Fecha inicio: {solicitud.apc_fecha_inicio}")
    print(f"   APC Fecha completado: {solicitud.apc_fecha_completado}")
    print(f"   APC Observaciones: {solicitud.apc_observaciones}")
    print(f"   APC Tipo documento: {solicitud.apc_tipo_documento}")
    print(f"   APC No cédula: {solicitud.apc_no_cedula}")
    
    print(f"\n👤 Usuario creador:")
    print(f"   Username: {solicitud.creada_por.username}")
    print(f"   Email: {solicitud.creada_por.email}")
    print(f"   Nombre: {solicitud.creada_por.get_full_name()}")
    
    if solicitud.asignada_a:
        print(f"\n👤 Usuario asignado:")
        print(f"   Username: {solicitud.asignada_a.username}")
        print(f"   Email: {solicitud.asignada_a.email}")
        print(f"   Nombre: {solicitud.asignada_a.get_full_name()}")
    else:
        print(f"\n👤 Usuario asignado: Sin asignar")
    
    # Verificar la condición que determina si se envía el correo
    print(f"\n🔍 Análisis de condiciones para envío de correo:")
    print(f"   Condición 1 - Status será 'in_progress': True (por parámetro API)")
    print(f"   Condición 2 - No tiene apc_fecha_inicio: {solicitud.apc_fecha_inicio is None}")
    print(f"   Resultado: {'✅ SE ENVIARÁ' if solicitud.apc_fecha_inicio is None else '❌ NO SE ENVIARÁ'}")
    
    if solicitud.apc_fecha_inicio:
        print(f"   ⚠️ PROBLEMA: Ya tiene apc_fecha_inicio establecida: {solicitud.apc_fecha_inicio}")
        print(f"   ⚠️ Para que se envíe el correo, debe ser None/null")
        
        # Sugerir solución
        print(f"\n💡 SOLUCIÓN:")
        print(f"   Para forzar el envío del correo, resetear apc_fecha_inicio a None:")
        print(f"   1. Entrar al Django Admin")
        print(f"   2. Encontrar solicitud {solicitud.codigo}")
        print(f"   3. Cambiar 'Apc fecha inicio' a vacío")
        print(f"   4. Guardar")
        print(f"   5. Volver a hacer la llamada API")
        
        print(f"\n🔧 O ejecutar en Django shell:")
        print(f"   from workflow.models import Solicitud")
        print(f"   s = Solicitud.objects.get(codigo='{solicitud.codigo}')")
        print(f"   s.apc_fecha_inicio = None")
        print(f"   s.save()")
    
    print(f"\n📧 Emails que recibirían notificación:")
    usuarios_notificar = [solicitud.creada_por]
    if solicitud.asignada_a and solicitud.asignada_a != solicitud.creada_por:
        usuarios_notificar.append(solicitud.asignada_a)
    
    for usuario in usuarios_notificar:
        if usuario.email:
            print(f"   ✅ {usuario.username}: {usuario.email}")
        else:
            print(f"   ❌ {usuario.username}: Sin email configurado")

if __name__ == '__main__':
    check_solicitud_status()
