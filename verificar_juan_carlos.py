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

def verificar_solicitud_juan_carlos():
    """
    Verificar específicamente la solicitud de Juan Carlos Mendoza Rodriguez
    que se está viendo en la imagen
    """
    print("=== VERIFICANDO SOLICITUD DE JUAN CARLOS ===")
    
    # Buscar todas las solicitudes de Juan Carlos
    solicitudes_juan = Solicitud.objects.filter(
        cliente_nombre__icontains="Juan Carlos Mendoza"
    )
    
    print(f"\n📋 SOLICITUDES DE JUAN CARLOS ENCONTRADAS: {solicitudes_juan.count()}")
    
    for sol in solicitudes_juan:
        print(f"\n🔍 SOLICITUD ID {sol.id}: {sol.codigo}")
        print(f"  - Cliente: {sol.cliente_nombre}")
        print(f"  - Pipeline: {sol.pipeline.nombre}")
        print(f"  - Etapa actual: {sol.etapa_actual.nombre if sol.etapa_actual else 'Sin etapa'}")
        print(f"  - Es bandeja grupal: {sol.etapa_actual.es_bandeja_grupal if sol.etapa_actual else 'N/A'}")
        print(f"  - Propietario: {sol.propietario.username if sol.propietario else 'Sin propietario'}")
        print(f"  - Asignada a: {sol.asignada_a.username if sol.asignada_a else 'Sin asignar'}")
        
        # Verificar condiciones EXACTAS
        if sol.etapa_actual:
            nombre_exacto = sol.etapa_actual.nombre
            es_bandeja = sol.etapa_actual.es_bandeja_grupal
            
            print(f"\n  🔍 VERIFICACIÓN DE CONDICIONES:")
            print(f"    - Nombre etapa: '{nombre_exacto}'")
            print(f"    - Es exactamente 'Back Office': {nombre_exacto == 'Back Office'}")
            print(f"    - Es bandeja grupal: {es_bandeja}")
            print(f"    - AMBAS condiciones: {nombre_exacto == 'Back Office' and es_bandeja}")
            
            if nombre_exacto == "Back Office" and es_bandeja:
                print(f"  ✅ DEBERÍA mostrar template: detalle_solicitud_backoffice.html")
                print(f"  🎯 URL: http://localhost:8000/workflow/detalle-solicitud/{sol.id}/")
            else:
                print(f"  ❌ NO mostrará template especial")
                if nombre_exacto != "Back Office":
                    print(f"    ❌ Problema: Etapa es '{nombre_exacto}', no 'Back Office'")
                if not es_bandeja:
                    print(f"    ❌ Problema: es_bandeja_grupal es False")
        
        print(f"  📱 URL para probar: /workflow/detalle-solicitud/{sol.id}/")
        print("-" * 60)
    
    # Verificar también las etapas "Back Office" existentes
    print(f"\n🏢 VERIFICANDO ETAPAS 'Back Office':")
    etapas_bo = Etapa.objects.filter(nombre="Back Office")
    
    for etapa in etapas_bo:
        print(f"\n  ✓ Etapa: '{etapa.nombre}'")
        print(f"    Pipeline: {etapa.pipeline.nombre}")
        print(f"    Es bandeja grupal: {etapa.es_bandeja_grupal}")
        print(f"    Orden: {etapa.orden}")
        
        # Contar solicitudes en esta etapa
        solicitudes_count = Solicitud.objects.filter(etapa_actual=etapa).count()
        print(f"    Solicitudes en esta etapa: {solicitudes_count}")
        
        if solicitudes_count > 0:
            solicitudes_en_etapa = Solicitud.objects.filter(etapa_actual=etapa)
            for sol in solicitudes_en_etapa:
                print(f"      • {sol.codigo} (ID: {sol.id}) - Cliente: {sol.cliente_nombre}")
    
    # Sugerir la URL correcta
    print(f"\n🎯 RECOMENDACIÓN:")
    solicitud_correcta = solicitudes_juan.filter(
        etapa_actual__nombre="Back Office",
        etapa_actual__es_bandeja_grupal=True
    ).first()
    
    if solicitud_correcta:
        print(f"  ✅ Usa esta URL para ver el template correcto:")
        print(f"     http://localhost:8000/workflow/detalle-solicitud/{solicitud_correcta.id}/")
    else:
        print(f"  ❌ No hay solicitudes de Juan Carlos en etapa Back Office con bandeja grupal")
        print(f"  💡 Crea una nueva o mueve una existente a la etapa correcta")

if __name__ == "__main__":
    try:
        verificar_solicitud_juan_carlos()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
