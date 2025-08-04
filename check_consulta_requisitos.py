#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PACIFICO.settings')
django.setup()

from workflow.modelsWorkflow import RequisitoTransicion, TransicionEtapa, Etapa

print('🔍 Checking requisitos for transitions to Consulta stage...')
consulta_etapas = Etapa.objects.filter(nombre__icontains='Consulta')
print(f'Found Consulta stages: {[e.nombre for e in consulta_etapas]}')

for etapa in consulta_etapas:
    print(f'\n📋 Requirements for transitions TO {etapa.nombre}:')
    transiciones_to_consulta = TransicionEtapa.objects.filter(etapa_destino=etapa)
    
    for transicion in transiciones_to_consulta:
        print(f'  🔄 {transicion.nombre} ({transicion.etapa_origen.nombre} -> {transicion.etapa_destino.nombre})')
        requisitos = RequisitoTransicion.objects.filter(transicion=transicion)
        
        for req in requisitos:
            obligatorio_text = 'Obligatorio' if req.obligatorio else 'Opcional'
            mensaje = req.mensaje_personalizado if req.mensaje_personalizado else '-'
            print(f'    - {req.requisito.nombre} ({obligatorio_text}) - {mensaje}')
        
        if not requisitos.exists():
            print('    - No requirements configured')
