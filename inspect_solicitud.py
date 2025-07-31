#!/usr/bin/env python
"""
Script para inspeccionar los campos de solicitud
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

def inspect_solicitud():
    """Inspeccionar campos de solicitud"""
    from workflow.models import Solicitud
    
    try:
        solicitud = Solicitud.objects.get(codigo="FLU-125")
        print(f"📋 Inspección de solicitud: {solicitud.codigo}")
        print(f"  Propietario: {solicitud.propietario}")
        print(f"  Creada por: {solicitud.creada_por}")
        print(f"  Creada por email: {solicitud.creada_por.email if solicitud.creada_por else 'Sin email'}")
        print(f"  Creada por nombre: {solicitud.creada_por.get_full_name() if solicitud.creada_por else 'Sin nombre'}")
        
        # Verificar si existe el campo propietario
        if hasattr(solicitud, 'propietario') and solicitud.propietario:
            print(f"  Propietario email: {solicitud.propietario.email}")
            print(f"  Propietario nombre: {solicitud.propietario.get_full_name()}")
        else:
            print("  No hay propietario definido, usando creada_por")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_solicitud()
