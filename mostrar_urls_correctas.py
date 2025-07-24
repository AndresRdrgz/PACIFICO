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

def mostrar_urls_correctas():
    """
    Mostrar las URLs correctas para acceder al template de Back Office
    """
    print("=== URLs CORRECTAS PARA TEMPLATE BACK OFFICE ===")
    
    # Buscar solicitudes de Back Office
    solicitudes_bo = Solicitud.objects.filter(
        etapa_actual__nombre="Back Office",
        etapa_actual__es_bandeja_grupal=True
    ).order_by('-id')
    
    print(f"\n🎯 SOLICITUDES QUE USAN TEMPLATE BACK OFFICE: {solicitudes_bo.count()}")
    
    for sol in solicitudes_bo:
        print(f"\n✅ SOLICITUD: {sol.codigo} (ID: {sol.id})")
        print(f"  - Cliente: {sol.cliente_nombre}")
        print(f"  - Pipeline: {sol.pipeline.nombre}")
        print(f"  - Etapa: {sol.etapa_actual.nombre}")
        print(f"  🌐 URL CORRECTA: http://localhost:8000/workflow/solicitud/{sol.id}/")
    
    print(f"\n" + "="*60)
    print(f"🚀 INSTRUCCIONES:")
    print(f"="*60)
    print(f"1. Copia una de las URLs de arriba")
    print(f"2. Pégala en tu navegador")
    print(f"3. Deberías ver el template con:")
    print(f"   • Header verde con 'Back Office - Análisis de Solicitud'")
    print(f"   • 4 pestañas de subestados")
    print(f"   • Información del cliente en grid")
    print(f"   • Contenido específico en cada pestaña")
    
    # Mostrar también las URLs principales
    print(f"\n📋 OTRAS URLs ÚTILES:")
    print(f"  • Admin Django: http://localhost:8000/admin/")
    print(f"  • Bandeja de trabajo: http://localhost:8000/workflow/bandeja/")
    print(f"  • Dashboard: http://localhost:8000/workflow/")

if __name__ == "__main__":
    try:
        mostrar_urls_correctas()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
