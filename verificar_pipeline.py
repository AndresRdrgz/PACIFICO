#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Pipeline, Etapa, Solicitud

print("=== VERIFICACIÓN DE PIPELINES Y ETAPAS ===")

# Listar todos los pipelines
print("\n1. Pipelines existentes:")
pipelines = Pipeline.objects.all()
if pipelines:
    for pipeline in pipelines:
        print(f"   - {pipeline.nombre} (ID: {pipeline.id})")
else:
    print("   ❌ No hay pipelines en la base de datos")

# Buscar pipeline específico
print("\n2. Buscando pipeline 'Flujo de Consulta de Auto':")
pipeline_auto = Pipeline.objects.filter(nombre__icontains='Flujo de consulta de Auto').first()
if pipeline_auto:
    print(f"   ✅ Encontrado: {pipeline_auto.nombre}")
    
    # Listar etapas del pipeline
    print(f"\n3. Etapas del pipeline '{pipeline_auto.nombre}':")
    etapas = pipeline_auto.etapas.all().order_by('orden')
    if etapas:
        for etapa in etapas:
            print(f"   - {etapa.nombre} (Orden: {etapa.orden})")
    else:
        print("   ❌ No hay etapas definidas para este pipeline")
    
    # Buscar etapa específica
    print(f"\n4. Buscando etapa 'Nuevo Lead':")
    etapa_lead = pipeline_auto.etapas.filter(nombre__icontains='Nuevo Lead').first()
    if etapa_lead:
        print(f"   ✅ Encontrada: {etapa_lead.nombre}")
    else:
        print("   ❌ No se encontró la etapa 'Nuevo Lead'")
        
        # Mostrar alternativas
        print("\n   Etapas disponibles que podrían ser similares:")
        etapas_similares = pipeline_auto.etapas.filter(nombre__icontains='Lead').all()
        if etapas_similares:
            for etapa in etapas_similares:
                print(f"     - {etapa.nombre}")
        else:
            print("     No hay etapas que contengan 'Lead'")

else:
    print("   ❌ No se encontró el pipeline")
    
    # Buscar pipelines similares
    print("\n   Buscando pipelines similares:")
    pipelines_similares = Pipeline.objects.filter(nombre__icontains='Auto').all()
    if pipelines_similares:
        for pipeline in pipelines_similares:
            print(f"     - {pipeline.nombre}")
    else:
        pipelines_similares = Pipeline.objects.filter(nombre__icontains='Consulta').all()
        if pipelines_similares:
            for pipeline in pipelines_similares:
                print(f"     - {pipeline.nombre}")
        else:
            print("     No se encontraron pipelines similares")

# Verificar solicitudes del canal digital
print("\n5. Verificando solicitudes del Canal Digital:")
solicitudes_canal = Solicitud.objects.filter(origen='Canal Digital').count()
print(f"   Total de solicitudes del Canal Digital: {solicitudes_canal}")

print("\n=== FIN DE VERIFICACIÓN ===")
