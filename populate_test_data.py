#!/usr/bin/env python
"""
Script to populate test data for demonstrating the drawer functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(__file__))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Pipeline, CampoPersonalizado, Requisito, RequisitoPipeline

def populate_test_data():
    """Populate test data with descriptions and more fields"""
    
    print("=" * 60)
    print("POPULATING TEST DATA FOR DRAWER")
    print("=" * 60)
    
    # Get or create a pipeline
    pipeline, created = Pipeline.objects.get_or_create(
        nombre="Préstamo Personal",
        defaults={
            'descripcion': "Pipeline para solicitudes de préstamos personales"
        }
    )
    
    if created:
        print(f"✅ Created pipeline: {pipeline.nombre}")
    else:
        print(f"ℹ️  Using existing pipeline: {pipeline.nombre}")
    
    # Create custom fields with descriptions
    custom_fields = [
        {
            'nombre': 'Monto Solicitado',
            'tipo': 'numero',
            'requerido': True,
            'descripcion': 'Monto del préstamo solicitado por el cliente'
        },
        {
            'nombre': 'Plazo en Meses',
            'tipo': 'entero',
            'requerido': True,
            'descripcion': 'Número de meses para el pago del préstamo'
        },
        {
            'nombre': 'Propósito del Préstamo',
            'tipo': 'texto',
            'requerido': True,
            'descripcion': 'Descripción del uso que se le dará al préstamo'
        },
        {
            'nombre': 'Fecha de Necesidad',
            'tipo': 'fecha',
            'requerido': False,
            'descripcion': 'Fecha en que el cliente necesita el dinero'
        },
        {
            'nombre': 'Tiene Garantía',
            'tipo': 'booleano',
            'requerido': False,
            'descripcion': 'Indica si el cliente puede ofrecer alguna garantía'
        },
        {
            'nombre': 'Observaciones',
            'tipo': 'texto',
            'requerido': False,
            'descripcion': 'Observaciones adicionales sobre la solicitud'
        }
    ]
    
    print("\n📋 CREATING CUSTOM FIELDS:")
    for field_data in custom_fields:
        field, created = CampoPersonalizado.objects.get_or_create(
            pipeline=pipeline,
            nombre=field_data['nombre'],
            defaults={
                'tipo': field_data['tipo'],
                'requerido': field_data['requerido'],
                'descripcion': field_data['descripcion']
            }
        )
        
        if created:
            print(f"   ✅ Created: {field.nombre} ({field.tipo})")
        else:
            # Update existing field with description
            field.descripcion = field_data['descripcion']
            field.save()
            print(f"   ℹ️  Updated: {field.nombre} ({field.tipo})")
    
    # Create requisitos with descriptions
    requisitos_data = [
        {
            'nombre': 'Cédula de Identidad',
            'descripcion': 'Copia de la cédula de identidad personal vigente'
        },
        {
            'nombre': 'Comprobante de Ingresos',
            'descripcion': 'Últimos 3 meses de comprobantes de ingresos (colilla de pago)'
        },
        {
            'nombre': 'Estados de Cuenta',
            'descripcion': 'Estados de cuenta bancarios de los últimos 3 meses'
        },
        {
            'nombre': 'Carta de Trabajo',
            'descripcion': 'Carta de trabajo con salario y antigüedad'
        },
        {
            'nombre': 'APC',
            'descripcion': 'Certificado de la Asociación Panameña de Crédito'
        },
        {
            'nombre': 'Referencias Comerciales',
            'descripcion': 'Cartas de referencia de establecimientos comerciales'
        },
        {
            'nombre': 'Paz y Salvo',
            'descripcion': 'Certificado de paz y salvo laboral'
        }
    ]
    
    print("\n📋 CREATING REQUISITOS:")
    for req_data in requisitos_data:
        requisito, created = Requisito.objects.get_or_create(
            nombre=req_data['nombre'],
            defaults={
                'descripcion': req_data['descripcion']
            }
        )
        
        if created:
            print(f"   ✅ Created: {requisito.nombre}")
        else:
            # Update existing requisito with description
            requisito.descripcion = req_data['descripcion']
            requisito.save()
            print(f"   ℹ️  Updated: {requisito.nombre}")
    
    # Assign requisitos to pipeline
    requisitos_pipeline = [
        ('Cédula de Identidad', True),
        ('Comprobante de Ingresos', True),
        ('Estados de Cuenta', True),
        ('Carta de Trabajo', True),
        ('APC', False),
        ('Referencias Comerciales', False),
        ('Paz y Salvo', False)
    ]
    
    print("\n📋 ASSIGNING REQUISITOS TO PIPELINE:")
    for req_nombre, obligatorio in requisitos_pipeline:
        requisito = Requisito.objects.get(nombre=req_nombre)
        req_pipeline, created = RequisitoPipeline.objects.get_or_create(
            pipeline=pipeline,
            requisito=requisito,
            defaults={
                'obligatorio': obligatorio
            }
        )
        
        if created:
            print(f"   ✅ Assigned: {requisito.nombre} (Obligatorio: {obligatorio})")
        else:
            # Update existing assignment
            req_pipeline.obligatorio = obligatorio
            req_pipeline.save()
            print(f"   ℹ️  Updated: {requisito.nombre} (Obligatorio: {obligatorio})")
    
    print("\n" + "=" * 60)
    print("TEST DATA POPULATION COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    populate_test_data()
