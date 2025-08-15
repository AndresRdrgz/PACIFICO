#!/usr/bin/env python3
"""
Standalone script to resend reconsideración email
Usage: python3 simple_resend_reconsideracion.py
"""

import os
import sys
import django

# Setup Django environment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pacifico.settings')

def setup_django():
    """Setup Django environment"""
    try:
        django.setup()
        return True
    except Exception as e:
        print(f"❌ Django setup error: {e}")
        return False

def resend_email_for_solicitud(solicitud_id):
    """Resend email for specific solicitud"""
    try:
        from workflow.modelsWorkflow import Solicitud
        from workflow.views_workflow import enviar_correo_pdf_resultado_consulta
        
        solicitud = Solicitud.objects.get(id=solicitud_id)
        print(f"📧 Found solicitud: {solicitud.codigo}")
        print(f"   Owner: {solicitud.propietario.get_full_name() if solicitud.propietario else 'N/A'}")
        print(f"   Email: {solicitud.propietario.email if solicitud.propietario else 'N/A'}")
        
        # Check for reconsideration
        reconsideraciones = solicitud.reconsideraciones.all()
        print(f"   Reconsiderations: {reconsideraciones.count()}")
        
        if reconsideraciones.exists():
            latest = reconsideraciones.order_by('-fecha_analisis').first()
            print(f"   Latest: #{latest.numero_reconsideracion} - {latest.estado}")
        
        print("🔄 Sending email...")
        enviar_correo_pdf_resultado_consulta(solicitud)
        print("✅ Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Resending Reconsideración Email")
    print("=" * 50)
    
    if not setup_django():
        sys.exit(1)
    
    # Default solicitud ID
    solicitud_id = 170
    
    if len(sys.argv) > 1:
        try:
            solicitud_id = int(sys.argv[1])
        except:
            pass
    
    print(f"📋 Solicitud ID: {solicitud_id}")
    success = resend_email_for_solicitud(solicitud_id)
    
    print("=" * 50)
    if success:
        print("🎉 SUCCESS: Email resent!")
    else:
        print("❌ FAILED: Could not resend email")
