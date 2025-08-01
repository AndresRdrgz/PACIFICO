import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Solicitud
from workflow.models import CalificacionCampo

try:
    # Get solicitud FLU-132
    solicitud = Solicitud.objects.get(codigo='FLU-132')
    
    print("=== SOLICITUD FLU-132 DATA ===")
    print(f"Código: {solicitud.codigo}")
    print(f"resultado_consulta: '{solicitud.resultado_consulta}' (type: {type(solicitud.resultado_consulta)})")
    print(f"Pipeline: {solicitud.pipeline.nombre if solicitud.pipeline else 'N/A'}")
    print(f"Etapa: {solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'N/A'}")
    print(f"Cliente: {solicitud.cliente.nombreCliente if solicitud.cliente else 'N/A'}")
    
    # Check calificaciones
    calificaciones = CalificacionCampo.objects.filter(solicitud=solicitud)
    print(f"Calificaciones: {calificaciones.count()}")
    
    # Test the context that would be sent to PDF
    print("\n=== PDF CONTEXT TEST ===")
    context = {
        'solicitud': solicitud,
        'resultado_analisis': solicitud.resultado_consulta,  # This is what should be passed
        'calificaciones': calificaciones,
    }
    
    print(f"resultado_analisis in context: '{context['resultado_analisis']}'")
    
    # Check if it's valid
    expected_values = ['Pendiente', 'Aprobado', 'Rechazado', 'Alternativa', 'En Comité']
    is_valid = context['resultado_analisis'] in expected_values
    print(f"Is valid value: {is_valid}")
    if not is_valid:
        print(f"Expected one of: {expected_values}")
    
    print("\n=== RESULT ===")
    if context['resultado_analisis'] == 'Aprobado':
        print("✅ Should show GREEN for 'Aprobado'")
    elif context['resultado_analisis'] == 'Rechazado':
        print("🔴 Should show RED for 'Rechazado'")
    elif context['resultado_analisis'] == 'Alternativa':
        print("🟠 Should show ORANGE for 'Alternativa'")
    else:
        print(f"⚪ Should show default color for '{context['resultado_analisis']}'")
        
except Solicitud.DoesNotExist:
    print("❌ Solicitud 'FLU-132' not found")
except Exception as e:
    print(f"❌ Error: {e}")
