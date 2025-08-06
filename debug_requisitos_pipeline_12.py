#!/usr/bin/env python
"""
Debug script to check requisitos for Pipeline 12 transition.
This will help us understand what the backend is returning.
"""

import os
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PACIFICO.settings')
django.setup()

from workflow.models import *
from django.contrib.auth.models import User

def check_pipeline_12_requisitos():
    """Check what requisitos exist for Pipeline 12 (Flujo de Consulta de Auto)"""
    
    print("=" * 70)
    print("🔍 DEBUGGING PIPELINE 12 REQUISITOS")
    print("=" * 70)
    
    # Get Pipeline 12
    try:
        pipeline = Pipeline.objects.get(id=12)
        print(f"📋 Pipeline: {pipeline.nombre}")
    except Pipeline.DoesNotExist:
        print("❌ Pipeline 12 not found!")
        return
    
    # Get etapas for this pipeline
    etapas = pipeline.etapas.all().order_by('orden')
    print(f"\n📍 Etapas in Pipeline 12:")
    for etapa in etapas:
        print(f"  - ID: {etapa.id}, Nombre: {etapa.nombre}, Orden: {etapa.orden}")
    
    # Look for transition from "nuevo lead" to "consulta"
    nuevo_lead = None
    consulta = None
    
    for etapa in etapas:
        if 'nuevo' in etapa.nombre.lower() and 'lead' in etapa.nombre.lower():
            nuevo_lead = etapa
        elif 'consulta' in etapa.nombre.lower():
            consulta = etapa
    
    print(f"\n🔄 Target Transition:")
    print(f"  - From: {nuevo_lead.nombre if nuevo_lead else 'NOT FOUND'}")
    print(f"  - To: {consulta.nombre if consulta else 'NOT FOUND'}")
    
    if not nuevo_lead or not consulta:
        print("❌ Could not find the target transition!")
        return
    
    # Find the transition
    transicion = TransicionEtapa.objects.filter(
        pipeline=pipeline,
        etapa_origen=nuevo_lead,
        etapa_destino=consulta
    ).first()
    
    if not transicion:
        print("❌ Transition not found!")
        return
    
    print(f"\n✅ Found Transition: {transicion.nombre}")
    
    # Get requisitos for this transition
    requisitos_transicion = RequisitoTransicion.objects.filter(
        transicion=transicion
    ).select_related('requisito')
    
    print(f"\n📄 Requisitos for this transition:")
    print(f"  Total requisitos: {requisitos_transicion.count()}")
    
    obligatorios = []
    opcionales = []
    
    for i, req_trans in enumerate(requisitos_transicion, 1):
        requisito = req_trans.requisito
        obligatorio = req_trans.obligatorio
        
        print(f"\n  {i}. Requisito: {requisito.nombre}")
        print(f"     - ID: {requisito.id}")
        print(f"     - Descripción: {requisito.descripcion or 'No description'}")
        print(f"     - Obligatorio: {obligatorio}")
        print(f"     - Mensaje personalizado: {req_trans.mensaje_personalizado or 'None'}")
        
        if obligatorio:
            obligatorios.append(requisito.nombre)
        else:
            opcionales.append(requisito.nombre)
    
    print(f"\n📊 Summary:")
    print(f"  - Requisitos Obligatorios ({len(obligatorios)}): {', '.join(obligatorios)}")
    print(f"  - Requisitos Opcionales ({len(opcionales)}): {', '.join(opcionales)}")
    
    # Test with a real solicitud if any exists
    solicitudes = Solicitud.objects.filter(pipeline=pipeline).order_by('-id')[:5]
    
    if solicitudes:
        print(f"\n🧪 Testing with recent solicitudes:")
        for solicitud in solicitudes:
            print(f"\n  Solicitud ID: {solicitud.id}")
            print(f"  - Estado actual: {solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'No etapa'}")
            print(f"  - Creada por: {solicitud.creada_por.username}")
            
            # Check requisitos for this solicitud
            requisitos_solicitud = RequisitoSolicitud.objects.filter(
                solicitud=solicitud
            ).select_related('requisito')
            
            for req_sol in requisitos_solicitud:
                print(f"    * {req_sol.requisito.nombre}: {'✅ Cumplido' if req_sol.cumplido else '❌ No cumplido'} ({'Con archivo' if req_sol.archivo else 'Sin archivo'})")
    else:
        print(f"\n  No solicitudes found for Pipeline 12")

if __name__ == "__main__":
    check_pipeline_12_requisitos()
