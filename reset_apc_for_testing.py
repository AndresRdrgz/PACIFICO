#!/usr/bin/env python
"""
Script para resetear el estado APC de una solicitud para testing
"""

import os
import sys
import django

# Configurar Django
sys.path.append('c:\\Users\\arodriguez\\Documents\\GitHub\\PACIFICO')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.models import Solicitud

def reset_apc_status(codigo_solicitud):
    """
    Resetear el estado APC de una solicitud para poder probar el envío de correo
    """
    try:
        solicitud = Solicitud.objects.get(codigo=codigo_solicitud)
        
        print(f"🔄 Reseteando estado APC de solicitud {codigo_solicitud}")
        print(f"📊 Estado ANTES:")
        print(f"   APC Status: {solicitud.apc_status}")
        print(f"   APC Fecha inicio: {solicitud.apc_fecha_inicio}")
        print(f"   APC Fecha completado: {solicitud.apc_fecha_completado}")
        print(f"   APC Observaciones: {solicitud.apc_observaciones}")
        
        # Resetear a estado inicial para permitir testing
        solicitud.apc_status = 'pending'
        solicitud.apc_fecha_inicio = None
        solicitud.apc_fecha_completado = None
        solicitud.apc_observaciones = 'Reseteado para testing de correo'
        
        solicitud.save()
        
        print(f"\n✅ Estado DESPUÉS del reset:")
        print(f"   APC Status: {solicitud.apc_status}")
        print(f"   APC Fecha inicio: {solicitud.apc_fecha_inicio}")
        print(f"   APC Fecha completado: {solicitud.apc_fecha_completado}")
        print(f"   APC Observaciones: {solicitud.apc_observaciones}")
        
        print(f"\n🎯 AHORA PUEDES PROBAR:")
        print(f"   1. Hacer la llamada API POST a:")
        print(f"      http://127.0.0.1:8000/workflow/api/makito/update-status/{codigo_solicitud}/")
        print(f"   2. Con body JSON:")
        print(f"      {{")
        print(f"        \"status\": \"in_progress\",")
        print(f"        \"observaciones\": \"Iniciando procesamiento del APC\"")
        print(f"      }}")
        print(f"   3. El correo se enviará a: otejerai@fpacifico.com")
        
        return True
        
    except Solicitud.DoesNotExist:
        print(f"❌ Solicitud {codigo_solicitud} no encontrada")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    success = reset_apc_status('FLU-101')
    if success:
        print(f"\n🎉 Reset completado exitosamente!")
    else:
        print(f"\n❌ Error en el reset")
