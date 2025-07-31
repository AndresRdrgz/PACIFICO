#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Solicitud

# Fix solicitud 130's cliente_nombre field
try:
    solicitud = Solicitud.objects.get(id=130)
    print(f"Before fix:")
    print(f"  cliente_nombre: '{solicitud.__dict__['cliente_nombre']}'")
    print(f"  cliente_nombre_completo: '{solicitud.cliente_nombre_completo}'")
    
    # Clear the cliente_nombre field so the property can check actual relationships
    solicitud.cliente_nombre = None
    solicitud.save()
    
    # Refresh from database
    solicitud.refresh_from_db()
    
    print(f"After fix:")
    print(f"  cliente_nombre: '{solicitud.__dict__['cliente_nombre']}'")
    print(f"  cliente_nombre_completo: '{solicitud.cliente_nombre_completo}'")
    
except Exception as e:
    print(f"Error: {e}")
