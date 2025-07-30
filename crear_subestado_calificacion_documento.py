#!/usr/bin/env python3
"""
Script para agregar el nuevo subestado 'Pendiente calificaciondocumentobackoffice'
a todas las etapas de Back Office existentes
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Etapa, SubEstado

def agregar_nuevo_subestado():
    """Agrega el nuevo subestado a todas las etapas de Back Office existentes"""
    
    # Buscar todas las etapas de Back Office
    etapas_backoffice = Etapa.objects.filter(
        nombre="Back Office", 
        es_bandeja_grupal=True
    )
    
    print(f"📋 Encontradas {etapas_backoffice.count()} etapas de Back Office")
    
    for etapa in etapas_backoffice:
        print(f"\n🔄 Procesando etapa: {etapa.pipeline.nombre} - {etapa.nombre}")
        
        # Verificar si ya existe el subestado
        subestado_existente = SubEstado.objects.filter(
            etapa=etapa,
            nombre='Pendiente calificaciondocumentobackoffice'
        ).first()
        
        if subestado_existente:
            print(f"   ⚠️  El subestado ya existe (ID: {subestado_existente.id})")
            continue
        
        # Crear el nuevo subestado
        nuevo_subestado = SubEstado.objects.create(
            etapa=etapa,
            pipeline=etapa.pipeline,
            nombre='Pendiente calificaciondocumentobackoffice',
            orden=5
        )
        
        print(f"   ✅ Creado subestado: {nuevo_subestado.nombre} (ID: {nuevo_subestado.id})")
    
    print(f"\n🎉 Proceso completado!")

if __name__ == '__main__':
    try:
        agregar_nuevo_subestado()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
