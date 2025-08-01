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
    
    print("=== CALIFICACION CAMPO ANALYSIS ===")
    
    # Check CalificacionCampo records
    calificaciones = CalificacionCampo.objects.filter(solicitud=solicitud)
    
    print(f"Total calificaciones: {calificaciones.count()}")
    
    # Look for any campo that might contain resultado_analisis
    resultado_campos = calificaciones.filter(campo__icontains='resultado')
    print(f"Campos with 'resultado': {resultado_campos.count()}")
    
    for cal in resultado_campos:
        print(f"  Campo: {cal.campo}")
        print(f"  Estado: {cal.estado}")  
        print(f"  Comentario: {cal.comentario}")
        print(f"  ---")
    
    # Look for specific resultado_analisis campo
    try:
        resultado_cal = calificaciones.get(campo='resultado_analisis')
        print(f"\n🎯 FOUND resultado_analisis campo:")
        print(f"  Estado: '{resultado_cal.estado}'")
        print(f"  Comentario: '{resultado_cal.comentario}'")
        print(f"  Fecha: {resultado_cal.fecha_actualizacion}")
    except CalificacionCampo.DoesNotExist:
        print(f"\n❌ No 'resultado_analisis' campo found")
    except CalificacionCampo.MultipleObjectsReturned:
        resultado_cals = calificaciones.filter(campo='resultado_analisis')
        print(f"\n⚠️ Multiple 'resultado_analisis' campos found: {resultado_cals.count()}")
        for i, cal in enumerate(resultado_cals):
            print(f"  #{i+1}: Estado='{cal.estado}', Comentario='{cal.comentario}'")
    
    # Check all campos to see their structure
    print(f"\n📋 ALL CAMPOS (first 10):")
    for cal in calificaciones[:10]:
        print(f"  {cal.campo}: {cal.estado} - {cal.comentario[:50] if cal.comentario else 'No comment'}")
    
    print(f"\n🔍 SUMMARY:")
    print(f"  - Solicitud.resultado_consulta: '{solicitud.resultado_consulta}'")
    print(f"  - CalificacionCampo 'resultado_analisis': Look above")
    print(f"  - Frontend showing: 'Rechazado'")
    print(f"  - PDF showing: '{solicitud.resultado_consulta}'")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
