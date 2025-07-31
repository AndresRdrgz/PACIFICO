#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Solicitud

# Get solicitud 130
try:
    solicitud = Solicitud.objects.get(id=130)
    print(f"Solicitud 130 info:")
    print(f"  Código: {solicitud.codigo}")
    print(f"  __dict__ keys: {list(solicitud.__dict__.keys())}")
    print(f"  cliente_nombre in __dict__: {'cliente_nombre' in solicitud.__dict__}")
    if 'cliente_nombre' in solicitud.__dict__:
        print(f"  cliente_nombre value: '{solicitud.__dict__['cliente_nombre']}'")
    
    print(f"  cliente_nombre_completo: '{solicitud.cliente_nombre_completo}'")
    
    # Check the cliente relation
    print(f"  cliente relation: {solicitud.cliente}")
    if solicitud.cliente:
        print(f"    cliente.nombreCliente: '{solicitud.cliente.nombreCliente}'")
        print(f"    cliente.cedulaCliente: '{solicitud.cliente.cedulaCliente}'")
    
    # Check the cotizacion relation
    print(f"  cotizacion relation: {solicitud.cotizacion}")
    if solicitud.cotizacion:
        print(f"    cotizacion.nombreCliente: '{solicitud.cotizacion.nombreCliente}'")
        print(f"    cotizacion.cedulaCliente: '{solicitud.cotizacion.cedulaCliente}'")
        
except Solicitud.DoesNotExist:
    print("Solicitud 130 not found")
except Exception as e:
    print(f"Error: {e}")
