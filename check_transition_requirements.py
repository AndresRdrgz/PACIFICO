import os
import sys
sys.path.append('c:/Users/arodriguez/Documents/GitHub/PACIFICO')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PACIFICO.settings')

import django
django.setup()

from workflow.modelsWorkflow import RequisitoTransicion, TransicionEtapa, Etapa, Requisito

# Find the specific transition
transicion = TransicionEtapa.objects.filter(
    etapa_origen__nombre__icontains='Nuevo Lead', 
    etapa_destino__nombre__icontains='Consulta'
).first()

if transicion:
    print(f'Found transition: {transicion.nombre}')
    print(f'From: {transicion.etapa_origen.nombre} -> To: {transicion.etapa_destino.nombre}')
    print('=' * 60)
    
    requisitos = RequisitoTransicion.objects.filter(transicion=transicion)
    print(f'Total requirements: {requisitos.count()}')
    
    for req in requisitos:
        obligatorio_text = 'True' if req.obligatorio else 'False'
        mensaje = req.mensaje_personalizado if req.mensaje_personalizado else '-'
        print(f'- {req.requisito.nombre} | Obligatorio: {obligatorio_text} | Mensaje: {mensaje}')
    
    # Check if APC exists
    apc_req = requisitos.filter(requisito__nombre__icontains='APC').first()
    if apc_req:
        print(f'\n✅ APC requirement found: {apc_req.requisito.nombre} (Obligatorio: {apc_req.obligatorio})')
    else:
        print('\n❌ APC requirement NOT found - needs to be added')
        # Check if APC requisito exists
        apc_requisito = Requisito.objects.filter(nombre__icontains='APC').first()
        if apc_requisito:
            print(f'   APC requisito exists: {apc_requisito.nombre}')
        else:
            print('   APC requisito does NOT exist in database')
else:
    print('Transition not found')
