#!/usr/bin/env python
"""
Script para verificar y corregir solicitudes SURA que no tienen el campo cotizar_sura_makito=True
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/Users/andresrdrgz_/Documents/GitHub/PACIFICO')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pacifico.settings')
django.setup()

from workflow.models import Solicitud

def fix_sura_tracking_field():
    """
    Encuentra y corrige solicitudes SURA que no tienen cotizar_sura_makito=True
    """
    print("🔍 Buscando solicitudes SURA sin cotizar_sura_makito=True...")
    
    # Buscar solicitudes que tienen datos SURA pero no el flag activado
    solicitudes_sura_sin_flag = Solicitud.objects.filter(
        sura_status__isnull=False,
        cotizar_sura_makito=False
    ).exclude(sura_status='')
    
    print(f"📊 Encontradas {solicitudes_sura_sin_flag.count()} solicitudes SURA sin flag de tracking")
    
    if solicitudes_sura_sin_flag.exists():
        print("\n📋 Solicitudes encontradas:")
        for solicitud in solicitudes_sura_sin_flag:
            print(f"  - Código: {solicitud.codigo}")
            print(f"    Cliente: {solicitud.cliente_nombre_completo or 'Sin cliente'}")
            print(f"    SURA Status: {solicitud.sura_status}")
            print(f"    Fecha solicitud: {solicitud.sura_fecha_solicitud}")
            print(f"    cotizar_sura_makito: {solicitud.cotizar_sura_makito}")
            print()
        
        respuesta = input("¿Desea corregir estas solicitudes? (y/N): ").strip().lower()
        
        if respuesta == 'y':
            actualizadas = solicitudes_sura_sin_flag.update(cotizar_sura_makito=True)
            print(f"✅ {actualizadas} solicitudes actualizadas correctamente")
            
            # Verificar el resultado
            print("\n🔍 Verificando corrección...")
            solicitudes_corregidas = Solicitud.objects.filter(
                sura_status__isnull=False,
                cotizar_sura_makito=True
            ).exclude(sura_status='')
            
            print(f"✅ Ahora hay {solicitudes_corregidas.count()} solicitudes SURA con tracking habilitado")
        else:
            print("❌ Operación cancelada")
    else:
        print("✅ Todas las solicitudes SURA ya tienen el flag de tracking correctamente configurado")
    
    # Mostrar resumen total
    print(f"\n📊 RESUMEN FINAL:")
    total_sura = Solicitud.objects.filter(
        sura_status__isnull=False,
        cotizar_sura_makito=True
    ).exclude(sura_status='').count()
    
    print(f"Total de solicitudes SURA con tracking: {total_sura}")

if __name__ == '__main__':
    fix_sura_tracking_field()
