#!/usr/bin/env python
"""
Script para verificar las URLs de Back Office
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from django.urls import reverse
from workflow.models import Solicitud

def verificar_urls_backoffice():
    print("🔍 Verificando URLs para Back Office...")
    print("=" * 50)
    
    # Verificar que la URL existe
    try:
        test_url = reverse('workflow:detalle_solicitud_backoffice', args=[1])
        print(f"✅ URL 'detalle_solicitud_backoffice' configurada correctamente")
        print(f"   Patrón: {test_url}")
    except Exception as e:
        print(f"❌ Error con URL 'detalle_solicitud_backoffice': {e}")
        return
    
    # Buscar solicitudes de Back Office
    print("\n🔍 Buscando solicitudes en etapa Back Office...")
    solicitudes_backoffice = Solicitud.objects.filter(
        etapa_actual__nombre="Back Office",
        etapa_actual__es_bandeja_grupal=True
    ).select_related('etapa_actual')
    
    if solicitudes_backoffice.exists():
        print(f"✅ Encontradas {solicitudes_backoffice.count()} solicitudes en Back Office")
        
        for solicitud in solicitudes_backoffice[:3]:  # Mostrar solo las primeras 3
            try:
                url_backoffice = reverse('workflow:detalle_solicitud_backoffice', args=[solicitud.id])
                print(f"   📋 Solicitud {solicitud.codigo}: {url_backoffice}")
            except Exception as e:
                print(f"   ❌ Error generando URL para solicitud {solicitud.codigo}: {e}")
    else:
        print("⚠️  No hay solicitudes en etapa Back Office")
    
    print("\n🔍 URLs de ejemplo:")
    print(f"   📋 Back Office URL: /workflow/solicitudes/106/backoffice/")
    print(f"   📋 Normal URL:     /workflow/solicitudes/106/detalle/")
    print(f"   📋 Análisis URL:   /workflow/solicitudes/106/analisis/")
    
    print("\n✅ Verificación completada!")

if __name__ == "__main__":
    verificar_urls_backoffice()
