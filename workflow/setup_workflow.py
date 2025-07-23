#!/usr/bin/env python
"""
Script de configuración inicial del Sistema de Workflow
Ejecutar después de las migraciones para crear datos de ejemplo
"""

import os
import sys
import django
from datetime import timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from workflow.modelsWorkflow import *

def crear_grupos_usuarios():
    """Crear grupos de usuarios básicos"""
    print("🔧 Creando grupos de usuarios...")
    
    grupos = [
        {
            'name': 'Comité',
            'description': 'Grupo para revisión y aprobación de solicitudes'
        },
        {
            'name': 'Trámite',
            'description': 'Grupo para procesamiento inicial de solicitudes'
        },
        {
            'name': 'Legal',
            'description': 'Grupo para validación legal de solicitudes'
        },
        {
            'name': 'Administración',
            'description': 'Grupo para administración del sistema'
        }
    ]
    
    for grupo_data in grupos:
        grupo, created = Group.objects.get_or_create(
            name=grupo_data['name']
        )
        if created:
            print(f"  ✅ Creado grupo: {grupo.name}")
        else:
            print(f"  ⚠️  Grupo ya existe: {grupo.name}")

def crear_usuarios_ejemplo():
    """Crear usuarios de ejemplo"""
    print("👥 Creando usuarios de ejemplo...")
    
    usuarios = [
        {
            'username': 'admin_workflow',
            'email': 'admin@pacifico.com',
            'first_name': 'Administrador',
            'last_name': 'Workflow',
            'password': 'admin123',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'comite_user',
            'email': 'comite@pacifico.com',
            'first_name': 'Usuario',
            'last_name': 'Comité',
            'password': 'comite123',
            'groups': ['Comité']
        },
        {
            'username': 'tramite_user',
            'email': 'tramite@pacifico.com',
            'first_name': 'Usuario',
            'last_name': 'Trámite',
            'password': 'tramite123',
            'groups': ['Trámite']
        },
        {
            'username': 'legal_user',
            'email': 'legal@pacifico.com',
            'first_name': 'Usuario',
            'last_name': 'Legal',
            'password': 'legal123',
            'groups': ['Legal']
        }
    ]
    
    for user_data in usuarios:
        username = user_data['username']
        if not User.objects.filter(username=username).exists():
            user = User.objects.create(
                username=username,
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                password=make_password(user_data['password']),
                is_staff=user_data.get('is_staff', False),
                is_superuser=user_data.get('is_superuser', False)
            )
            
            # Asignar grupos
            if 'groups' in user_data:
                for grupo_nombre in user_data['groups']:
                    grupo = Group.objects.get(name=grupo_nombre)
                    user.groups.add(grupo)
            
            print(f"  ✅ Creado usuario: {username} ({user_data['password']})")
        else:
            print(f"  ⚠️  Usuario ya existe: {username}")

def crear_tipos_solicitud():
    """Crear tipos de solicitud básicos"""
    print("🏷️  Creando tipos de solicitud...")
    
    tipos = [
        'Préstamo Personal',
        'Préstamo Auto',
        'Préstamo Hipotecario',
        'Refinanciamiento',
        'Línea de Crédito',
        'Tarjeta de Crédito'
    ]
    
    for tipo_nombre in tipos:
        tipo, created = TipoSolicitud.objects.get_or_create(nombre=tipo_nombre)
        if created:
            print(f"  ✅ Creado tipo: {tipo.nombre}")
        else:
            print(f"  ⚠️  Tipo ya existe: {tipo.nombre}")

def crear_pipelines_ejemplo():
    """Crear pipelines de ejemplo"""
    print("🔄 Creando pipelines de ejemplo...")
    
    # Pipeline de Préstamo Personal
    pipeline_personal, created = Pipeline.objects.get_or_create(
        nombre='Préstamo Personal',
        defaults={'descripcion': 'Pipeline para solicitudes de préstamo personal'}
    )
    
    if created:
        print(f"  ✅ Creado pipeline: {pipeline_personal.nombre}")
        
        # Crear etapas
        etapas_personal = [
            {
                'nombre': 'Recepción',
                'orden': 1,
                'sla': timedelta(hours=24),
                'es_bandeja_grupal': True
            },
            {
                'nombre': 'Validación',
                'orden': 2,
                'sla': timedelta(hours=48),
                'es_bandeja_grupal': False
            },
            {
                'nombre': 'Análisis',
                'orden': 3,
                'sla': timedelta(days=3),
                'es_bandeja_grupal': False
            },
            {
                'nombre': 'Comité',
                'orden': 4,
                'sla': timedelta(days=2),
                'es_bandeja_grupal': True
            },
            {
                'nombre': 'Aprobación',
                'orden': 5,
                'sla': timedelta(hours=24),
                'es_bandeja_grupal': False
            }
        ]
        
        for etapa_data in etapas_personal:
            etapa = Etapa.objects.create(
                pipeline=pipeline_personal,
                **etapa_data
            )
            print(f"    ✅ Creada etapa: {etapa.nombre}")
        
        # Crear transiciones
        transiciones = [
            (1, 2, 'Validar'),
            (2, 3, 'Enviar a Análisis'),
            (3, 4, 'Enviar a Comité'),
            (4, 5, 'Aprobar'),
            (2, 1, 'Devolver'),
            (3, 2, 'Devolver'),
            (4, 3, 'Devolver'),
            (5, 4, 'Devolver')
        ]
        
        for origen, destino, nombre in transiciones:
            etapa_origen = Etapa.objects.get(pipeline=pipeline_personal, orden=origen)
            etapa_destino = Etapa.objects.get(pipeline=pipeline_personal, orden=destino)
            
            TransicionEtapa.objects.create(
                pipeline=pipeline_personal,
                etapa_origen=etapa_origen,
                etapa_destino=etapa_destino,
                nombre=nombre
            )
            print(f"    ✅ Creada transición: {etapa_origen.nombre} → {etapa_destino.nombre}")
    
    # Pipeline de Préstamo Auto
    pipeline_auto, created = Pipeline.objects.get_or_create(
        nombre='Préstamo Auto',
        defaults={'descripcion': 'Pipeline para solicitudes de préstamo de auto'}
    )
    
    if created:
        print(f"  ✅ Creado pipeline: {pipeline_auto.nombre}")
        
        # Crear etapas
        etapas_auto = [
            {
                'nombre': 'Recepción',
                'orden': 1,
                'sla': timedelta(hours=24),
                'es_bandeja_grupal': True
            },
            {
                'nombre': 'Validación',
                'orden': 2,
                'sla': timedelta(hours=48),
                'es_bandeja_grupal': False
            },
            {
                'nombre': 'Evaluación Vehículo',
                'orden': 3,
                'sla': timedelta(days=2),
                'es_bandeja_grupal': False
            },
            {
                'nombre': 'Análisis',
                'orden': 4,
                'sla': timedelta(days=3),
                'es_bandeja_grupal': False
            },
            {
                'nombre': 'Aprobación',
                'orden': 5,
                'sla': timedelta(hours=24),
                'es_bandeja_grupal': False
            }
        ]
        
        for etapa_data in etapas_auto:
            etapa = Etapa.objects.create(
                pipeline=pipeline_auto,
                **etapa_data
            )
            print(f"    ✅ Creada etapa: {etapa.nombre}")
    else:
        print(f"  ⚠️  Pipeline ya existe: {pipeline_auto.nombre}")

def crear_requisitos_ejemplo():
    """Crear requisitos básicos"""
    print("📋 Creando requisitos de ejemplo...")
    
    requisitos = [
        'Cédula de Identidad',
        'Comprobante de Ingresos',
        'Estados de Cuenta Bancarios',
        'Referencias Personales',
        'Referencias Comerciales',
        'Certificado de Trabajo',
        'Declaración de Renta',
        'Certificado de Vehículo',
        'Póliza de Seguro',
        'Cotización del Vehículo'
    ]
    
    for requisito_nombre in requisitos:
        requisito, created = Requisito.objects.get_or_create(
            nombre=requisito_nombre,
            defaults={'descripcion': f'Requisito: {requisito_nombre}'}
        )
        if created:
            print(f"  ✅ Creado requisito: {requisito.nombre}")
        else:
            print(f"  ⚠️  Requisito ya existe: {requisito.nombre}")

def asignar_requisitos_pipelines():
    """Asignar requisitos a pipelines y tipos"""
    print("🔗 Asignando requisitos a pipelines...")
    
    # Obtener pipelines y tipos
    pipeline_personal = Pipeline.objects.get(nombre='Préstamo Personal')
    pipeline_auto = Pipeline.objects.get(nombre='Préstamo Auto')
    
    tipo_personal = TipoSolicitud.objects.get(nombre='Préstamo Personal')
    tipo_auto = TipoSolicitud.objects.get(nombre='Préstamo Auto')
    
    # Requisitos para Préstamo Personal
    requisitos_personal = [
        'Cédula de Identidad',
        'Comprobante de Ingresos',
        'Estados de Cuenta Bancarios',
        'Referencias Personales',
        'Referencias Comerciales',
        'Certificado de Trabajo',
        'Declaración de Renta'
    ]
    
    for requisito_nombre in requisitos_personal:
        requisito = Requisito.objects.get(nombre=requisito_nombre)
        req_pipeline, created = RequisitoPipelineTipo.objects.get_or_create(
            pipeline=pipeline_personal,
            tipo_solicitud=tipo_personal,
            requisito=requisito,
            defaults={'obligatorio': True}
        )
        if created:
            print(f"  ✅ Asignado requisito: {requisito.nombre} a Préstamo Personal")
    
    # Requisitos para Préstamo Auto
    requisitos_auto = [
        'Cédula de Identidad',
        'Comprobante de Ingresos',
        'Estados de Cuenta Bancarios',
        'Certificado de Vehículo',
        'Póliza de Seguro',
        'Cotización del Vehículo'
    ]
    
    for requisito_nombre in requisitos_auto:
        requisito = Requisito.objects.get(nombre=requisito_nombre)
        req_pipeline, created = RequisitoPipelineTipo.objects.get_or_create(
            pipeline=pipeline_auto,
            tipo_solicitud=tipo_auto,
            requisito=requisito,
            defaults={'obligatorio': True}
        )
        if created:
            print(f"  ✅ Asignado requisito: {requisito.nombre} a Préstamo Auto")

def crear_campos_personalizados():
    """Crear campos personalizados de ejemplo"""
    print("📝 Creando campos personalizados...")
    
    # Campos para Préstamo Personal
    pipeline_personal = Pipeline.objects.get(nombre='Préstamo Personal')
    
    campos_personal = [
        {
            'nombre': 'Monto Solicitado',
            'tipo': 'numero',
            'requerido': True
        },
        {
            'nombre': 'Plazo (meses)',
            'tipo': 'entero',
            'requerido': True
        },
        {
            'nombre': 'Destino del Crédito',
            'tipo': 'texto',
            'requerido': True
        },
        {
            'nombre': 'Fecha de Desembolso',
            'tipo': 'fecha',
            'requerido': False
        },
        {
            'nombre': 'Acepta Seguro',
            'tipo': 'booleano',
            'requerido': False
        }
    ]
    
    for campo_data in campos_personal:
        campo, created = CampoPersonalizado.objects.get_or_create(
            pipeline=pipeline_personal,
            nombre=campo_data['nombre'],
            defaults=campo_data
        )
        if created:
            print(f"  ✅ Creado campo: {campo.nombre}")

def asignar_permisos_etapas():
    """Asignar permisos a etapas"""
    print("🔐 Asignando permisos a etapas...")
    
    # Obtener grupos
    grupo_comite = Group.objects.get(name='Comité')
    grupo_tramite = Group.objects.get(name='Trámite')
    grupo_legal = Group.objects.get(name='Legal')
    
    # Obtener pipelines
    pipeline_personal = Pipeline.objects.get(nombre='Préstamo Personal')
    pipeline_auto = Pipeline.objects.get(nombre='Préstamo Auto')
    
    # Asignar permisos por etapa
    permisos_etapas = [
        # Pipeline Personal
        (pipeline_personal, 'Recepción', [grupo_tramite], True, True),
        (pipeline_personal, 'Validación', [grupo_tramite], True, False),
        (pipeline_personal, 'Análisis', [grupo_legal], True, False),
        (pipeline_personal, 'Comité', [grupo_comite], True, True),
        (pipeline_personal, 'Aprobación', [grupo_comite], True, False),
        
        # Pipeline Auto
        (pipeline_auto, 'Recepción', [grupo_tramite], True, True),
        (pipeline_auto, 'Validación', [grupo_tramite], True, False),
        (pipeline_auto, 'Evaluación Vehículo', [grupo_legal], True, False),
        (pipeline_auto, 'Análisis', [grupo_legal], True, False),
        (pipeline_auto, 'Aprobación', [grupo_comite], True, False),
    ]
    
    for pipeline, etapa_nombre, grupos, puede_ver, puede_autoasignar in permisos_etapas:
        try:
            etapa = Etapa.objects.get(pipeline=pipeline, nombre=etapa_nombre)
            
            for grupo in grupos:
                permiso, created = PermisoEtapa.objects.get_or_create(
                    etapa=etapa,
                    grupo=grupo,
                    defaults={
                        'puede_ver': puede_ver,
                        'puede_autoasignar': puede_autoasignar
                    }
                )
                if created:
                    print(f"  ✅ Permiso asignado: {grupo.name} → {etapa.nombre}")
        except Etapa.DoesNotExist:
            print(f"  ⚠️  Etapa no encontrada: {etapa_nombre}")

def crear_solicitudes_ejemplo():
    """Crear solicitudes de ejemplo"""
    print("📄 Creando solicitudes de ejemplo...")
    
    # Obtener datos necesarios
    pipeline_personal = Pipeline.objects.get(nombre='Préstamo Personal')
    etapa_recepcion = Etapa.objects.get(pipeline=pipeline_personal, nombre='Recepción')
    usuario_tramite = User.objects.get(username='tramite_user')
    
    # Crear 5 solicitudes de ejemplo
    for i in range(1, 6):
        if not Solicitud.objects.filter(pipeline=pipeline_personal, creada_por=usuario_tramite).exists():
            solicitud = Solicitud.objects.create(
                pipeline=pipeline_personal,
                etapa_actual=etapa_recepcion,
                creada_por=usuario_tramite,
                asignada_a=usuario_tramite if i % 2 == 0 else None
            )
            
            # Crear historial inicial
            HistorialSolicitud.objects.create(
                solicitud=solicitud,
                etapa=etapa_recepcion,
                usuario_responsable=usuario_tramite
            )
            
            # Crear requisitos
            requisitos_pipeline = RequisitoPipeline.objects.filter(
                pipeline=pipeline_personal
            )
            
            for req_pipeline in requisitos_pipeline:
                RequisitoSolicitud.objects.create(
                    solicitud=solicitud,
                    requisito=req_pipeline.requisito,
                    cumplido=i % 3 == 0  # Algunos requisitos cumplidos
                )
            
            print(f"  ✅ Creada solicitud: {solicitud.codigo}")

def main():
    """Función principal"""
    print("🚀 Iniciando configuración del Sistema de Workflow...")
    print("=" * 60)
    
    try:
        crear_grupos_usuarios()
        print()
        
        crear_usuarios_ejemplo()
        print()
        
        crear_pipelines_ejemplo()
        print()
        
        crear_requisitos_ejemplo()
        print()
        
        asignar_requisitos_pipelines()
        print()
        
        crear_campos_personalizados()
        print()
        
        asignar_permisos_etapas()
        print()
        
        crear_solicitudes_ejemplo()
        print()
        
        print("=" * 60)
        print("✅ Configuración completada exitosamente!")
        print()
        print("📋 Resumen de la configuración:")
        print(f"  • Grupos: {Group.objects.count()}")
        print(f"  • Usuarios: {User.objects.count()}")
        print(f"  • Pipelines: {Pipeline.objects.count()}")
        print(f"  • Etapas: {Etapa.objects.count()}")
        print(f"  • Requisitos: {Requisito.objects.count()}")
        print(f"  • Solicitudes: {Solicitud.objects.count()}")
        print()
        print("🔑 Credenciales de acceso:")
        print("  • Admin: admin_workflow / admin123")
        print("  • Comité: comite_user / comite123")
        print("  • Trámite: tramite_user / tramite123")
        print("  • Legal: legal_user / legal123")
        print()
        print("🌐 Acceder al sistema:")
        print("  • URL: http://localhost:8000/workflow/")
        print("  • Admin: http://localhost:8000/admin/")
        
    except Exception as e:
        print(f"❌ Error durante la configuración: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 