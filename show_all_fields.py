#!/usr/bin/env python
"""
Script para mostrar TODOS los campos de una entrevista
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
    print(f"=== TODOS LOS CAMPOS DE LA ENTREVISTA {entrevista.id} ===\n")
    
    # Obtener todos los campos del modelo
    fields = entrevista._meta.get_fields()
    
    for field in fields:
        if hasattr(field, 'name'):
            field_name = field.name
            # Excluir campos relacionados que no son del formulario
            if field_name not in ['referencias_personales', 'referencias_comerciales', 'otros_ingresos']:
                value = getattr(entrevista, field_name, None)
                if value is not None and value != '':
                    print(f"✅ {field_name}: {value}")
                else:
                    print(f"❌ {field_name}: [VACÍO]")
    
    print(f"\n=== CAMPOS CON DATOS ===")
    campos_con_datos = []
    for field in fields:
        if hasattr(field, 'name'):
            field_name = field.name
            if field_name not in ['referencias_personales', 'referencias_comerciales', 'otros_ingresos']:
                value = getattr(entrevista, field_name, None)
                if value is not None and value != '':
                    campos_con_datos.append(field_name)
    
    print(f"Total campos con datos: {len(campos_con_datos)}")
    for campo in campos_con_datos:
        print(f"- {campo}")
        
else:
    print("No hay entrevistas en la base de datos")
