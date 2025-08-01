import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.modelsWorkflow import Solicitud, SolicitudComentario

try:
    # Get solicitud FLU-132
    solicitud = Solicitud.objects.get(codigo='FLU-132')
    
    print("=== SOLICITUD FLU-132 ANALYSIS ===")
    print(f"Solicitud.resultado_consulta: '{solicitud.resultado_consulta}'")
    
    # Check SolicitudComentario records
    comentarios = SolicitudComentario.objects.filter(
        solicitud=solicitud,
        tipo="analista_credito"
    ).order_by("-fecha_creacion")
    
    print(f"\nComentarios de analista_credito: {comentarios.count()}")
    
    for i, comentario in enumerate(comentarios[:5]):  # Show first 5
        print(f"\n--- Comentario #{i+1} ---")
        print(f"  ID: {comentario.pk}")
        print(f"  Usuario: {comentario.usuario.username}")
        print(f"  Fecha: {comentario.fecha_creacion}")
        print(f"  Contenido: {comentario.contenido[:100]}...")
        
        # Check if this comentario has resultado_analisis
        if hasattr(comentario, 'resultado_analisis'):
            print(f"  resultado_analisis: '{comentario.resultado_analisis}'")
        else:
            print(f"  resultado_analisis: No tiene este campo")
    
    # Check the latest comment specifically
    if comentarios.exists():
        latest = comentarios.first()
        print(f"\n🔍 LATEST COMMENT ANALYSIS:")
        print(f"  Latest comment ID: {latest.pk}")
        print(f"  Latest comment fecha: {latest.fecha_creacion}")
        
        # Check all fields of the latest comment
        print(f"  All fields:")
        for field in latest._meta.get_fields():
            if hasattr(latest, field.name) and not field.name.startswith('_'):
                value = getattr(latest, field.name)
                print(f"    {field.name}: {value}")
                
    print(f"\n🎯 DIAGNOSIS:")
    print(f"  - Solicitud model says: '{solicitud.resultado_consulta}'")
    print(f"  - Frontend shows: 'Rechazado' (from data-original-resultado)")
    print(f"  - PDF generates: '{solicitud.resultado_consulta}' (from backend)")
    print(f"  - This suggests the frontend is loading from a different source!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
