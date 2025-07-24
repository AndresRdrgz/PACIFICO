#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.models import Pipeline, Etapa, SubEstado
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def crear_subestados_backoffice():
    """
    Crear subestados específicos para Back Office basados en los procesos mencionados:
    1. Revisión de documentación
    2. Captura del préstamo 
    3. Firma del cliente
    4. Ordenar el expediente
    """
    print("=== Creando Subestados Específicos para Back Office ===")
    
    # Buscar o crear pipeline y etapa Back Office
    pipeline, created = Pipeline.objects.get_or_create(
        nombre="Proceso Completo Back Office",
        defaults={
            'descripcion': 'Pipeline completo para procesos de Back Office'
        }
    )
    print(f"Pipeline: {pipeline.nombre} ({'creado' if created else 'existente'})")
    
    # Crear etapa Back Office con bandeja grupal
    etapa, created = Etapa.objects.get_or_create(
        pipeline=pipeline,
        nombre="Back Office",
        defaults={
            'es_bandeja_grupal': True,
            'orden': 1,
            'sla': timedelta(hours=24)  # SLA de 24 horas
        }
    )
    
    if not created:
        etapa.es_bandeja_grupal = True
        etapa.save()
    
    print(f"Etapa: {etapa.nombre} ({'creada' if created else 'actualizada'})")
    print(f"  - Es bandeja grupal: {etapa.es_bandeja_grupal}")
    
    # Eliminar subestados existentes para recrearlos
    SubEstado.objects.filter(etapa=etapa).delete()
    print("Eliminados subestados existentes")
    
    # Crear los 4 subestados específicos
    subestados_data = [
        {
            'nombre': 'Revisión de Documentación',
            'orden': 1
        },
        {
            'nombre': 'Captura del Préstamo',
            'orden': 2
        },
        {
            'nombre': 'Firma del Cliente',
            'orden': 3
        },
        {
            'nombre': 'Ordenar el Expediente',
            'orden': 4
        }
    ]
    
    print("\nCreando subestados específicos:")
    subestados_creados = []
    
    for data in subestados_data:
        subestado = SubEstado.objects.create(
            etapa=etapa,
            **data
        )
        subestados_creados.append(subestado)
        print(f"  ✓ {subestado.nombre} (orden: {subestado.orden})")
    
    print(f"\nTotal de subestados creados: {len(subestados_creados)}")
    
    # Verificar el orden
    print("\nVerificando orden de subestados:")
    subestados_ordenados = SubEstado.objects.filter(etapa=etapa).order_by('orden')
    for i, subestado in enumerate(subestados_ordenados, 1):
        print(f"  {i}. {subestado.nombre} (orden: {subestado.orden})")
    
    return pipeline, etapa, subestados_creados

def crear_solicitud_prueba(etapa):
    """Crear una solicitud de prueba para probar el template"""
    from workflow.models import Solicitud
    
    # Buscar o crear usuario de prueba
    user, created = User.objects.get_or_create(
        username='backoffice_test',
        defaults={
            'first_name': 'Test',
            'last_name': 'Back Office',
            'email': 'test@backoffice.com'
        }
    )
    
    # Crear solicitud de prueba
    solicitud, created = Solicitud.objects.get_or_create(
        codigo='TEST-BO-COMPLETO-001',
        defaults={
            'pipeline': etapa.pipeline,
            'etapa_actual': etapa,
            'cliente_nombre': 'Juan Carlos Mendoza Rodriguez',
            'cliente_cedula': '8-123-456',
            'cliente_telefono': '6789-1234',
            'cliente_email': 'jcarlos.mendoza@email.com',
            'producto_solicitado': 'Préstamo Personal',
            'monto_solicitado': 15000.00,
            'motivo_consulta': 'Necesito un préstamo personal para consolidar deudas y realizar mejoras en mi hogar.',
            'origen': 'Sucursal Central',
            'prioridad': 'Alta',
            'creada_por': user,
            'asignada_a': user,
            'propietario': user,
            'observaciones': 'Cliente con buen historial crediticio. Documentación inicial completa.',
            'como_se_entero': 'Sucursal'
        }
    )
    
    print(f"\nSolicitud de prueba: {solicitud.codigo} ({'creada' if created else 'existente'})")
    print(f"  - Cliente: {solicitud.cliente_nombre}")
    print(f"  - Producto: {solicitud.producto_solicitado}")
    print(f"  - Monto: B/. {solicitud.monto_solicitado}")
    print(f"  - Prioridad: {solicitud.prioridad}")
    
    return solicitud

if __name__ == "__main__":
    try:
        pipeline, etapa, subestados = crear_subestados_backoffice()
        solicitud = crear_solicitud_prueba(etapa)
        
        print("\n" + "="*60)
        print("✅ CONFIGURACION COMPLETA")
        print("="*60)
        print(f"Pipeline: {pipeline.nombre}")
        print(f"Etapa: {etapa.nombre} (Bandeja grupal: {etapa.es_bandeja_grupal})")
        print(f"Subestados: {len(subestados)} creados")
        print(f"Solicitud de prueba: {solicitud.codigo}")
        
        print("\n🔗 URLs de prueba:")
        print(f"Admin Django: /admin/")
        print(f"Pipeline: /admin/workflow/pipeline/{pipeline.id}/change/")
        print(f"Etapa: /admin/workflow/etapa/{etapa.id}/change/")
        print(f"Solicitud: /workflow/detalle-solicitud/{solicitud.id}/")
        
        print("\n📋 Pestañas que aparecerán en el template:")
        for subestado in subestados:
            print(f"  • {subestado.nombre}")
        
        print("\n🎯 Template usado: detalle_solicitud_backoffice.html")
        print("   (Con pestañas dinámicas basadas en subestados)")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
