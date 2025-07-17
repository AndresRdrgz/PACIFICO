#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import RequisitoSolicitud

def fix_requisitos():
    """Fix requisitos that have files but are not marked as cumplido"""
    print("🔧 Fixing requisitos...")
    
    # Find requisitos that have files but cumplido=False
    requisitos_con_archivos = RequisitoSolicitud.objects.filter(
        archivo__isnull=False,
        cumplido=False
    )
    
    print(f"📋 Found {requisitos_con_archivos.count()} requisitos with files but cumplido=False")
    
    fixed_count = 0
    for req in requisitos_con_archivos:
        print(f"   - {req.requisito.nombre} (Solicitud: {req.solicitud.codigo})")
        req.cumplido = True
        req.save()
        fixed_count += 1
    
    print(f"✅ Fixed {fixed_count} requisitos")
    
    # Also check for requisitos that are marked as cumplido but don't have files
    requisitos_sin_archivos = RequisitoSolicitud.objects.filter(
        archivo__isnull=True,
        cumplido=True
    )
    
    print(f"📋 Found {requisitos_sin_archivos.count()} requisitos marked as cumplido but without files")
    
    for req in requisitos_sin_archivos:
        print(f"   - {req.requisito.nombre} (Solicitud: {req.solicitud.codigo})")

if __name__ == '__main__':
    fix_requisitos() 