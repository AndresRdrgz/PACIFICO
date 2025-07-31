#!/usr/bin/env python3
"""
Debug script for Kanban view issue
"""
# Run in Django shell: python manage.py shell < debug_kanban.py

from workflow.modelsWorkflow import Pipeline, Solicitud, Etapa
from django.contrib.auth.models import User
from django.db.models import Q

print("🔍 DEBUGGING KANBAN VIEW")
print("=" * 50)

# Get pipeline 12
try:
    pipeline = Pipeline.objects.get(id=12)
    print(f"✅ Pipeline found: {pipeline.nombre}")
    print(f"   Description: {pipeline.descripcion}")
except Pipeline.DoesNotExist:
    print("❌ Pipeline with ID 12 not found")
    exit()

# Check etapas
etapas = pipeline.etapas.all()
print(f"\n📊 Pipeline has {etapas.count()} etapas:")
for etapa in etapas:
    print(f"   - {etapa.nombre} (ID: {etapa.id}, Order: {etapa.orden})")

# Check total solicitudes in pipeline
total_solicitudes = Solicitud.objects.filter(pipeline=pipeline).count()
print(f"\n📋 Total solicitudes in pipeline: {total_solicitudes}")

# Check solicitudes per etapa
print(f"\n📊 Solicitudes por etapa:")
for etapa in etapas:
    count = Solicitud.objects.filter(pipeline=pipeline, etapa_actual=etapa).count()
    print(f"   - {etapa.nombre}: {count} solicitudes")
    
    # Show some sample solicitudes
    if count > 0:
        samples = Solicitud.objects.filter(pipeline=pipeline, etapa_actual=etapa)[:3]
        for sol in samples:
            print(f"     * {sol.codigo} - {sol.cliente_nombre or 'Sin cliente'}")

# Check solicitudes without etapa
sin_etapa = Solicitud.objects.filter(pipeline=pipeline, etapa_actual__isnull=True).count()
if sin_etapa > 0:
    print(f"   - Sin etapa: {sin_etapa} solicitudes")

print(f"\n✨ Debug complete!")
