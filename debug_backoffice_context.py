#!/usr/bin/env python
"""
Script para debuggear el contexto del Back Office
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Solicitud

def debug_solicitud_context(solicitud_id):
    try:
        solicitud = Solicitud.objects.get(id=solicitud_id)
        print(f"📋 DEBUGGING SOLICITUD {solicitud_id}")
        print(f"   Etapa actual: {solicitud.etapa_actual}")
        print(f"   Subestado actual: {solicitud.subestado_actual}")
        
        if solicitud.etapa_actual:
            print(f"   Es bandeja grupal: {solicitud.etapa_actual.es_bandeja_grupal}")
            print(f"   Nombre etapa: {solicitud.etapa_actual.nombre}")
            
            # Mostrar subestados disponibles
            subestados = solicitud.etapa_actual.subestados.all()
            print(f"   Subestados disponibles: {[s.nombre for s in subestados]}")
            
            # Verificar archivos por subestado
            from workflow.views_workflow import TransicionEtapa
            transiciones_salida = TransicionEtapa.objects.filter(
                pipeline=solicitud.pipeline,
                etapa_origen=solicitud.etapa_actual
            ).prefetch_related('requisitos_obligatorios__requisito')
            
            transiciones_entrada = TransicionEtapa.objects.filter(
                pipeline=solicitud.pipeline,
                etapa_destino=solicitud.etapa_actual
            ).prefetch_related('requisitos_obligatorios__requisito')
            
            print(f"   Transiciones de salida: {transiciones_salida.count()}")
            print(f"   Transiciones de entrada: {transiciones_entrada.count()}")
            
            # Verificar requisitos
            from workflow.modelsWorkflow import RequisitoSolicitud
            requisitos_solicitud = RequisitoSolicitud.objects.filter(solicitud=solicitud)
            print(f"   Requisitos de solicitud: {requisitos_solicitud.count()}")
            
            for req in requisitos_solicitud:
                print(f"     - {req.requisito.nombre}: {req.cumplido} ({req.archivo})")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_solicitud_context(114)
