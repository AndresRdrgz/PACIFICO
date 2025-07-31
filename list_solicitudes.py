#!/usr/bin/env python
"""
Script para listar solicitudes disponibles
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

def list_solicitudes():
    """Listar solicitudes disponibles"""
    from workflow.models import Solicitud
    
    try:
        solicitudes = Solicitud.objects.all()[:10]  # Primeras 10
        print(f"📋 Solicitudes encontradas: {Solicitud.objects.count()}")
        
        for sol in solicitudes:
            print(f"- Código: {sol.codigo}")
            print(f"  Cliente: {getattr(sol, 'cliente_nombre_completo', 'No disponible')}")
            print(f"  Propietario: {sol.propietario.get_full_name() if sol.propietario else 'Sin propietario'}")
            print(f"  Email: {sol.propietario.email if sol.propietario else 'Sin email'}")
            print(f"  Etapa: {sol.etapa_actual.nombre if sol.etapa_actual else 'Sin etapa'}")
            print()
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    list_solicitudes()
