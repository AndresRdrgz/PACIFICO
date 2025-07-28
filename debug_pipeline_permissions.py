#!/usr/bin/env python
"""
Script to debug pipeline permissions for the negocios view
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pacifico.settings')
django.setup()

from workflow.modelsWorkflow import Pipeline, PermisoPipeline
from django.contrib.auth.models import User
from django.db.models import Q

print("=== PIPELINE PERMISSIONS DEBUG ===")

# Get the superuser
user = User.objects.filter(is_superuser=True).first()
print(f"Superuser found: {user}")
print(f"Is superuser: {user.is_superuser if user else 'No user found'}")

# Check all pipelines
pipelines = Pipeline.objects.all()
print(f"\nTotal pipelines in database: {pipelines.count()}")
for p in pipelines:
    print(f"  - Pipeline: '{p.nombre}' (ID: {p.id})")

# Check permissions
permisos = PermisoPipeline.objects.all()
print(f"\nTotal pipeline permissions: {permisos.count()}")
for perm in permisos:
    print(f"  - {perm.usuario or perm.grupo}: '{perm.pipeline.nombre}' - Ver: {perm.puede_ver}")

# Test the superuser access logic
if user and user.is_superuser:
    print(f"\n✅ SUPERUSER ACCESS:")
    print("   Should be able to see ALL pipelines")
    available_pipelines = Pipeline.objects.all()
    print(f"   Available pipelines for superuser: {available_pipelines.count()}")
    for p in available_pipelines:
        print(f"     - {p.nombre}")
else:
    print(f"\n❌ REGULAR USER ACCESS:")
    if user:
        # Test the permission logic for regular users
        available_pipelines = Pipeline.objects.filter(
            Q(permisopipeline__usuario=user) |
            Q(etapas__permisos__grupo__user=user)
        ).distinct()
        print(f"   Available pipelines for user '{user}': {available_pipelines.count()}")
        for p in available_pipelines:
            print(f"     - {p.nombre}")

print("\n=== DEBUG COMPLETE ===")
