#!/usr/bin/env python
"""
Script para crear reportes de ejemplo y datos de prueba para el módulo de reportería
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from django.contrib.auth.models import User, Group
from workflow.modelsWorkflow import *
from datetime import datetime, timedelta
import json
import random

def crear_reportes_ejemplo():
    """Crear algunos reportes de ejemplo"""
    
    # Obtener o crear un usuario admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser(
            username='admin_reportes',
            email='admin@pacifico.com',
            password='admin123',
            first_name='Administrador',
            last_name='Reportes'
        )
    
    # Crear grupo de supervisores si no existe
    grupo_supervisores, created = Group.objects.get_or_create(name='Supervisores')
    grupo_gerencia, created = Group.objects.get_or_create(name='Gerencia')
    
    # Reporte 1: Dashboard Ejecutivo
    reporte1, created = ReportePersonalizado.objects.get_or_create(
        nombre="Dashboard Ejecutivo",
        defaults={
            'descripcion': 'Vista general del estado de todas las solicitudes para gerencia',
            'usuario': admin_user,
            'filtros_json': {
                'fecha_inicio': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'fecha_fin': datetime.now().strftime('%Y-%m-%d')
            },
            'campos_json': [
                'codigo', 'pipeline', 'etapa_actual', 'cliente_nombre', 
                'monto', 'producto', 'asignada_a', 'fecha_creacion', 
                'tiempo_en_etapa', 'sla_status', 'prioridad'
            ],
            'configuracion_json': {
                'tipo': 'general',
                'incluir_graficos': True,
                'incluir_resumen': True
            },
            'es_publico': True,
            'es_favorito': True,
            'veces_ejecutado': random.randint(15, 50)
        }
    )
    if created:
        reporte1.grupos_compartidos.add(grupo_gerencia, grupo_supervisores)
    
    # Reporte 2: SLA y Cumplimiento
    reporte2, created = ReportePersonalizado.objects.get_or_create(
        nombre="Análisis de SLA y Cumplimiento",
        defaults={
            'descripcion': 'Análisis detallado del cumplimiento de SLA por etapa y pipeline',
            'usuario': admin_user,
            'filtros_json': {
                'fecha_inicio': (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'fecha_fin': datetime.now().strftime('%Y-%m-%d'),
                'estado_sla': 'vencido'
            },
            'campos_json': [
                'codigo', 'pipeline', 'etapa_actual', 'tiempo_en_etapa', 
                'sla_status', 'asignada_a', 'prioridad', 'fecha_creacion'
            ],
            'configuracion_json': {
                'tipo': 'sla',
                'incluir_metricas': True,
                'alertas_sla': True
            },
            'es_publico': True,
            'es_favorito': True,
            'veces_ejecutado': random.randint(10, 30)
        }
    )
    if created:
        reporte2.grupos_compartidos.add(grupo_supervisores)
    
    # Reporte 3: Productividad por Usuario
    reporte3, created = ReportePersonalizado.objects.get_or_create(
        nombre="Productividad por Analista",
        defaults={
            'descripcion': 'Reporte de productividad y carga de trabajo por analista',
            'usuario': admin_user,
            'filtros_json': {
                'fecha_inicio': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'fecha_fin': datetime.now().strftime('%Y-%m-%d')
            },
            'campos_json': [
                'codigo', 'asignada_a', 'etapa_actual', 'tiempo_en_etapa',
                'fecha_creacion', 'fecha_actualizacion', 'prioridad'
            ],
            'configuracion_json': {
                'tipo': 'productividad',
                'agrupar_por': 'usuario',
                'incluir_metricas': True
            },
            'es_publico': True,
            'veces_ejecutado': random.randint(5, 25)
        }
    )
    if created:
        reporte3.grupos_compartidos.add(grupo_supervisores, grupo_gerencia)
    
    # Reporte 4: Reporte de Montos y Productos
    reporte4, created = ReportePersonalizado.objects.get_or_create(
        nombre="Análisis de Montos y Productos",
        defaults={
            'descripcion': 'Análisis de solicitudes por monto y tipo de producto',
            'usuario': admin_user,
            'filtros_json': {
                'fecha_inicio': (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'),
                'fecha_fin': datetime.now().strftime('%Y-%m-%d'),
                'monto_min': '5000'
            },
            'campos_json': [
                'codigo', 'cliente_nombre', 'cliente_cedula', 'monto', 
                'producto', 'pipeline', 'etapa_actual', 'fecha_creacion'
            ],
            'configuracion_json': {
                'tipo': 'financiero',
                'incluir_totales': True,
                'agrupar_por': 'producto'
            },
            'es_publico': False,
            'es_favorito': False,
            'veces_ejecutado': random.randint(3, 15)
        }
    )
    
    # Reporte 5: Reporte Compliance
    reporte5, created = ReportePersonalizado.objects.get_or_create(
        nombre="Estado de Compliance y Documentos",
        defaults={
            'descripcion': 'Estado de requisitos y documentos de compliance por solicitud',
            'usuario': admin_user,
            'filtros_json': {
                'fecha_inicio': (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
                'fecha_fin': datetime.now().strftime('%Y-%m-%d')
            },
            'campos_json': [
                'codigo', 'cliente_nombre', 'pipeline', 'etapa_actual',
                'asignada_a', 'fecha_creacion', 'tiempo_en_etapa'
            ],
            'configuracion_json': {
                'tipo': 'compliance',
                'incluir_requisitos': True,
                'incluir_calificaciones': True
            },
            'es_publico': True,
            'es_favorito': True,
            'veces_ejecutado': random.randint(8, 20)
        }
    )
    if created:
        reporte5.grupos_compartidos.add(grupo_supervisores)
    
    print("✅ Reportes de ejemplo creados exitosamente:")
    for reporte in [reporte1, reporte2, reporte3, reporte4, reporte5]:
        print(f"   • {reporte.nombre}")
        
        # Crear algunas ejecuciones de ejemplo
        for i in range(random.randint(2, 5)):
            fecha_ejecucion = datetime.now() - timedelta(days=random.randint(1, 30))
            EjecucionReporte.objects.get_or_create(
                reporte=reporte,
                usuario=admin_user,
                fecha_ejecucion=fecha_ejecucion,
                defaults={
                    'parametros_json': {},
                    'tiempo_ejecucion': random.uniform(0.5, 3.0),
                    'registros_resultantes': random.randint(10, 500),
                    'exitosa': random.choice([True, True, True, False])  # 75% exitosas
                }
            )

def crear_datos_estadisticos():
    """Crear algunos datos estadísticos de ejemplo"""
    
    # Actualizar fechas de última ejecución para hacer más realistas los reportes
    reportes = ReportePersonalizado.objects.all()
    for reporte in reportes:
        if reporte.veces_ejecutado > 0:
            ultima_ejecucion = datetime.now() - timedelta(
                days=random.randint(0, 7),
                hours=random.randint(0, 23)
            )
            reporte.ultima_ejecucion = ultima_ejecucion
            reporte.save()
    
    print("✅ Datos estadísticos actualizados")

def main():
    print("🚀 Iniciando creación de datos de ejemplo para Reportería...")
    print()
    
    try:
        crear_reportes_ejemplo()
        print()
        crear_datos_estadisticos()
        print()
        print("🎉 ¡Datos de ejemplo creados exitosamente!")
        print()
        print("📊 Puedes acceder al módulo de reportes en:")
        print("   http://127.0.0.1:8000/workflow/reportes/")
        print()
        print("👤 Usuario administrador:")
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            print(f"   Usuario: {admin_user.username}")
            print("   Contraseña: (la que ya tienes configurada)")
        
    except Exception as e:
        print(f"❌ Error creando datos de ejemplo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
