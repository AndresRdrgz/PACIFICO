import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Solicitud

try:
    # Update FLU-132 to have Aprobado
    solicitud = Solicitud.objects.get(codigo='FLU-132')
    
    print(f"=== UPDATING FLU-132 ===")
    print(f"Current resultado_consulta: '{solicitud.resultado_consulta}'")
    
    # Update to Aprobado
    solicitud.resultado_consulta = 'Aprobado'
    solicitud.save()
    
    print(f"Updated resultado_consulta: '{solicitud.resultado_consulta}'")
    print("✅ Updated FLU-132 to 'Aprobado' for testing")
    
    # Show all choices for reference
    print("\n=== VALID CHOICES ===")
    for choice in solicitud.RESULTADO_CONSULTA_CHOICES:
        print(f"  {choice[0]}: {choice[1]}")
    
except Solicitud.DoesNotExist:
    print("❌ Solicitud 'FLU-132' not found")
except Exception as e:
    print(f"❌ Error: {e}")
