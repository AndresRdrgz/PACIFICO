#!/usr/bin/env python
"""
Script para debuggear el formulario admin
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
from workflow.forms import ClienteEntrevistaForm

# Buscar una entrevista existente para debuggear
entrevistas = ClienteEntrevista.objects.all()
print(f"Total entrevistas: {entrevistas.count()}")

if entrevistas.exists():
    entrevista = entrevistas.first()
    print(f"\n=== DATOS DE LA ENTREVISTA ===")
    print(f"ID: {entrevista.id}")
    print(f"Nombre: {entrevista.primer_nombre} {entrevista.primer_apellido}")
    print(f"Email: {entrevista.email}")
    print(f"Teléfono: {entrevista.telefono}")
    print(f"Provincia cédula: {entrevista.provincia_cedula}")
    print(f"Tipo letra: {entrevista.tipo_letra}")
    print(f"Tomo cédula: {entrevista.tomo_cedula}")
    print(f"Partida cédula: {entrevista.partida_cedula}")
    
    # Crear formulario con instancia
    form = ClienteEntrevistaForm(instance=entrevista)
    
    print(f"\n=== VALORES INICIALES DEL FORMULARIO ===")
    print(f"primer_nombre: {form.initial.get('primer_nombre', 'NO ENCONTRADO')}")
    print(f"primer_apellido: {form.initial.get('primer_apellido', 'NO ENCONTRADO')}")
    print(f"email: {form.initial.get('email', 'NO ENCONTRADO')}")
    print(f"telefono: {form.initial.get('telefono', 'NO ENCONTRADO')}")
    print(f"provincia_cedula: {form.initial.get('provincia_cedula', 'NO ENCONTRADO')}")
    print(f"tipo_letra: {form.initial.get('tipo_letra', 'NO ENCONTRADO')}")
    print(f"tomo_cedula: {form.initial.get('tomo_cedula', 'NO ENCONTRADO')}")
    print(f"partida_cedula: {form.initial.get('partida_cedula', 'NO ENCONTRADO')}")
    
    # Verificar el campo provincia_cedula específicamente
    provincia_field = form['provincia_cedula']
    print(f"\n=== CAMPO PROVINCIA CÉDULA ===")
    print(f"Valor actual: {provincia_field.value()}")
    print(f"Widget: {provincia_field.field.widget}")
    print(f"Choices: {provincia_field.field.choices[:5]}...")  # Primeras 5 opciones
    
else:
    print("No hay entrevistas en la base de datos")
