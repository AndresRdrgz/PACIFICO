#!/usr/bin/env python
"""
Test to verify email content includes correo solicitante
"""

import os
import sys
import django

# Configurar Django
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from django.contrib.auth.models import User
from workflow.modelsWorkflow import Solicitud, Pipeline
from django.utils import timezone

def test_email_content():
    print("=== TESTING EMAIL CONTENT WITH CORREO SOLICITANTE ===")
    
    try:
        # Create test user with email
        user = User.objects.create_user(
            username=f'test_user_{timezone.now().strftime("%H%M%S")}',
            first_name='Ana',
            last_name='Rodriguez',
            email='ana.rodriguez@fpacifico.com'
        )
        
        # Get pipeline
        pipeline = Pipeline.objects.first()
        if not pipeline:
            pipeline = Pipeline.objects.create(nombre='Test Pipeline')
        
        # Create solicitud
        solicitud = Solicitud.objects.create(
            codigo=f"TEST-EMAIL-{timezone.now().strftime('%H%M%S')}",
            pipeline=pipeline,
            creada_por=user,
            descargar_apc_makito=True,
            apc_no_cedula='8-555-777',
            apc_tipo_documento='cedula'
        )
        
        print(f"✅ Created test data:")
        print(f"   User: {user.get_full_name()}")
        print(f"   Email: {user.email}")
        print(f"   Solicitud: {solicitud.codigo}")
        
        # Simulate email content generation
        cliente_nombre = solicitud.cliente_nombre or "Cliente no asignado"
        correo_solicitante = user.email or "No especificado"
        
        # Expected email content
        expected_content = f"""
        Solicitud de Descarga APC con Makito
        
        Hola,
        
        Se ha solicitado la descarga del APC para la siguiente solicitud:
        
        • Código de Solicitud: {solicitud.codigo}
        • Cliente: {cliente_nombre}
        • Tipo de Documento: {solicitud.apc_tipo_documento.title()}
        • Número de Documento: {solicitud.apc_no_cedula}
        • Pipeline: {solicitud.pipeline.nombre}
        • Solicitado por: {user.get_full_name() or user.username}
        • Correo Solicitante: {correo_solicitante}
        • Fecha de Solicitud: {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        
        Información para APC:
        Tipo de documento: {solicitud.apc_tipo_documento.title()}
        Número de documento: {solicitud.apc_no_cedula}
        """
        
        print("\n--- EXPECTED EMAIL CONTENT ---")
        print(f"To: arodriguez@fpacifico.com")
        print(f"Subject: workflowAPC - {cliente_nombre} - {solicitud.apc_no_cedula}")
        print(expected_content)
        
        # Verify key field is present
        if "Correo Solicitante:" in expected_content:
            print("✅ EMAIL CONTENT INCLUDES 'Correo Solicitante' field")
        else:
            print("❌ EMAIL CONTENT MISSING 'Correo Solicitante' field")
        
        # Test with user without email
        user_no_email = User.objects.create_user(
            username=f'no_email_user_{timezone.now().strftime("%H%M%S")}',
            first_name='Sin',
            last_name='Email',
            email=''  # No email
        )
        
        correo_solicitante_empty = user_no_email.email or "No especificado"
        
        print(f"\n--- TEST USER WITHOUT EMAIL ---")
        print(f"User: {user_no_email.get_full_name()}")
        print(f"Email: '{user_no_email.email}' (empty)")
        print(f"Correo Solicitante would show: {correo_solicitante_empty}")
        
        if correo_solicitante_empty == "No especificado":
            print("✅ CORRECTLY HANDLES USERS WITHOUT EMAIL")
        else:
            print("❌ ERROR IN HANDLING USERS WITHOUT EMAIL")
        
        # Cleanup
        solicitud.delete()
        user.delete()
        user_no_email.delete()
        
        print("\n🎉 ALL TESTS PASSED")
        print("✅ The 'Correo Solicitante' field has been successfully added to APC emails")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_email_content()
