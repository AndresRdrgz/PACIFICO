#!/usr/bin/env python3
"""
Debug script for user permissions on solicitudes
"""
from workflow.modelsWorkflow import Pipeline, Solicitud
from django.contrib.auth.models import User
from django.db.models import Q

print("🔍 DEBUGGING USER PERMISSIONS ON SOLICITUDES")
print("=" * 60)

# Get pipeline 12
pipeline = Pipeline.objects.get(id=12)
print(f"✅ Pipeline: {pipeline.nombre}")

# Get all solicitudes in pipeline
all_solicitudes = Solicitud.objects.filter(pipeline=pipeline).select_related('creada_por', 'asignada_a', 'propietario')
print(f"\n📋 All solicitudes in pipeline: {all_solicitudes.count()}")

print(f"\n👥 User assignments:")
for sol in all_solicitudes:
    print(f"   - {sol.codigo}:")
    print(f"     * creada_por: {sol.creada_por.username if sol.creada_por else 'None'}")
    print(f"     * asignada_a: {sol.asignada_a.username if sol.asignada_a else 'None'}")
    print(f"     * propietario: {sol.propietario.username if sol.propietario else 'None'}")
    print(f"     * etapa_actual: {sol.etapa_actual.nombre if sol.etapa_actual else 'None'}")

print(f"\n👤 Available users:")
users = User.objects.all()[:10]  # Show first 10 users
for user in users:
    print(f"   - {user.username} (ID: {user.id}) - {user.get_full_name()}")
    if user.is_superuser:
        print(f"     * Superuser: YES")
    else:
        print(f"     * Superuser: NO")

print(f"\n✨ Debug complete!")
