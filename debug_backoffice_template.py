#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.models import Pipeline, Etapa, SubEstado, Solicitud
from django.contrib.auth.models import User

def debug_solicitud_actual():
    """
    Debug para verificar qué está pasando con la detección del template
    """
    print("=== DEBUG: Verificando detección de template Back Office ===")
    
    # Listar todas las solicitudes que podrían estar siendo vistas
    print("\n📋 TODAS LAS SOLICITUDES EN EL SISTEMA:")
    solicitudes = Solicitud.objects.all().order_by('-id')[:10]  # Últimas 10
    
    for sol in solicitudes:
        etapa_nombre = sol.etapa_actual.nombre if sol.etapa_actual else "Sin etapa"
        es_bandeja = sol.etapa_actual.es_bandeja_grupal if sol.etapa_actual else False
        
        print(f"  ID {sol.id}: {sol.codigo} | Etapa: {etapa_nombre} | Bandeja: {es_bandeja}")
        
        # Verificar condiciones para template especial
        if sol.etapa_actual:
            usara_especial = (sol.etapa_actual.nombre == "Back Office" and sol.etapa_actual.es_bandeja_grupal)
            print(f"    ✓ Usará template especial: {usara_especial}")
            if usara_especial:
                print(f"    🎯 URL: /workflow/detalle-solicitud/{sol.id}/")
        print()
    
    # Verificar específicamente etapas llamadas "Back Office"
    print("\n🏢 ETAPAS LLAMADAS 'Back Office':")
    etapas_bo = Etapa.objects.filter(nombre__icontains="back office")
    
    for etapa in etapas_bo:
        print(f"  ✓ {etapa.nombre} (Pipeline: {etapa.pipeline.nombre})")
        print(f"    - Es bandeja grupal: {etapa.es_bandeja_grupal}")
        print(f"    - Orden: {etapa.orden}")
        
        # Buscar solicitudes en esta etapa
        solicitudes_en_etapa = Solicitud.objects.filter(etapa_actual=etapa)
        print(f"    - Solicitudes en esta etapa: {solicitudes_en_etapa.count()}")
        
        for sol in solicitudes_en_etapa:
            print(f"      • {sol.codigo} (ID: {sol.id}) - URL: /workflow/detalle-solicitud/{sol.id}/")
        print()
    
    # Verificar si existe nuestra solicitud de prueba
    print("\n🧪 SOLICITUD DE PRUEBA ESPECÍFICA:")
    try:
        solicitud_prueba = Solicitud.objects.get(codigo='TEST-BO-COMPLETO-001')
        print(f"  ✓ Encontrada: {solicitud_prueba.codigo} (ID: {solicitud_prueba.id})")
        print(f"  - Etapa: {solicitud_prueba.etapa_actual.nombre}")
        print(f"  - Es bandeja grupal: {solicitud_prueba.etapa_actual.es_bandeja_grupal}")
        print(f"  - Pipeline: {solicitud_prueba.pipeline.nombre}")
        
        # Verificar condiciones exactas
        condicion1 = solicitud_prueba.etapa_actual.nombre == "Back Office"
        condicion2 = solicitud_prueba.etapa_actual.es_bandeja_grupal
        
        print(f"\n🔍 VERIFICACIÓN DE CONDICIONES:")
        print(f"  - etapa_actual.nombre == 'Back Office': {condicion1}")
        print(f"  - etapa_actual.es_bandeja_grupal: {condicion2}")
        print(f"  - AMBAS condiciones: {condicion1 and condicion2}")
        
        if condicion1 and condicion2:
            print(f"\n✅ DEBERÍA usar template: detalle_solicitud_backoffice.html")
            print(f"🎯 URL CORRECTA: http://localhost:8000/workflow/detalle-solicitud/{solicitud_prueba.id}/")
        else:
            print(f"\n❌ NO usará template especial")
            if not condicion1:
                print(f"    Problema: Nombre de etapa es '{solicitud_prueba.etapa_actual.nombre}', no 'Back Office'")
            if not condicion2:
                print(f"    Problema: es_bandeja_grupal es False")
    
    except Solicitud.DoesNotExist:
        print("  ❌ No se encontró la solicitud TEST-BO-COMPLETO-001")
    
    # Listar todas las etapas para verificar nombres exactos
    print(f"\n📝 TODAS LAS ETAPAS EN EL SISTEMA:")
    etapas = Etapa.objects.all().order_by('pipeline__nombre', 'orden')
    
    for etapa in etapas:
        bandeja_str = "SÍ" if etapa.es_bandeja_grupal else "NO"
        print(f"  • '{etapa.nombre}' (Pipeline: {etapa.pipeline.nombre}) | Bandeja: {bandeja_str}")

if __name__ == "__main__":
    try:
        debug_solicitud_actual()
        
    except Exception as e:
        print(f"❌ Error durante el debug: {str(e)}")
        import traceback
        traceback.print_exc()
