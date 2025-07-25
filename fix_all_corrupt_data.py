#!/usr/bin/env python
"""
Script para arreglar TODOS los datos corruptos de la entrevista
"""
import os
import sys
import django

# Agregar el path del proyecto
sys.path.append('c:/Users/jacastillo/Documents/GitHub/PACIFICO')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.models import ClienteEntrevista

# Obtener la entrevista
entrevista = ClienteEntrevista.objects.first()

if entrevista:
    print(f"=== ARREGLANDO DATOS CORRUPTOS ===\n")
    
    # Arreglar campo sexo (debe ser M o F, no una fecha)
    print(f"ANTES - sexo: {entrevista.sexo}")
    if str(entrevista.sexo).startswith('20'):  # Es una fecha
        entrevista.sexo = 'M'  # Default masculino
        print(f"CORREGIDO - sexo: {entrevista.sexo}")
    
    # Verificar otros campos que podrían estar corruptos
    # Verificar que no_dependientes sea un número
    if isinstance(entrevista.no_dependientes, str):
        try:
            entrevista.no_dependientes = int(entrevista.no_dependientes)
        except:
            entrevista.no_dependientes = 0
    
    # Verificar que salario sea un número
    try:
        float(entrevista.salario)
    except:
        entrevista.salario = 0.00
    
    # Verificar fechas
    from datetime import datetime
    if isinstance(entrevista.fecha_nacimiento, str):
        try:
            entrevista.fecha_nacimiento = datetime.strptime(entrevista.fecha_nacimiento, '%Y-%m-%d').date()
        except:
            entrevista.fecha_nacimiento = datetime(1990, 1, 1).date()
    
    # Guardar cambios
    entrevista.save()
    
    print(f"\n✅ Datos corruptos corregidos")
    print(f"- sexo: {entrevista.sexo}")
    print(f"- no_dependientes: {entrevista.no_dependientes}")
    print(f"- salario: {entrevista.salario}")
    print(f"- fecha_nacimiento: {entrevista.fecha_nacimiento}")
    
else:
    print("No hay entrevistas en la base de datos")
