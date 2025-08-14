#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Requisito

print('Campos del modelo Requisito:')
for field in Requisito._meta.fields:
    print(f'  {field.name}: {field.get_internal_type()}')

print('\nVerificando si existe algún requisito con tipo_especial:')
requisitos = Requisito.objects.all()
for req in requisitos:
    print(f'  ID: {req.id}, Nombre: {req.nombre}, Tipo Especial: {req.tipo_especial}')
