#!/usr/bin/env python3
"""
Debug script to check SLA calculation issues in vista_mixta_bandejas
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.insert(0, '/Users/andresrdrgz_/Documents/GitHub/PACIFICO')

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pacifico.settings')
django.setup()

from workflow.modelsWorkflow import Solicitud, Etapa
from django.utils import timezone
from datetime import timedelta

def debug_sla_calculation():
    """Debug SLA calculation for solicitudes"""
    
    print("=== DEBUG SLA CALCULATION ===")
    
    # Get some solicitudes to test
    solicitudes = Solicitud.objects.filter(etapa_actual__isnull=False).select_related('etapa_actual')[:5]
    
    if not solicitudes:
        print("No solicitudes found with etapa_actual")
        return
    
    ahora = timezone.now()
    print(f"Current time: {ahora}")
    
    for solicitud in solicitudes:
        print(f"\n--- Solicitud ID: {solicitud.id} ---")
        print(f"Etapa actual: {solicitud.etapa_actual}")
        print(f"Fecha última actualización: {solicitud.fecha_ultima_actualizacion}")
        
        if solicitud.etapa_actual:
            print(f"Etapa SLA: {solicitud.etapa_actual.sla}")
            print(f"Etapa SLA type: {type(solicitud.etapa_actual.sla)}")
            
            if solicitud.etapa_actual.sla:
                # Calculate SLA like in the view
                tiempo_total = solicitud.etapa_actual.sla.total_seconds()
                tiempo_transcurrido = (ahora - solicitud.fecha_ultima_actualizacion).total_seconds()
                segundos_restantes = tiempo_total - tiempo_transcurrido
                porcentaje_restante = (segundos_restantes / tiempo_total) * 100 if tiempo_total > 0 else 0
                
                abs_segundos = abs(int(segundos_restantes))
                horas = abs_segundos // 3600
                minutos = (abs_segundos % 3600) // 60
                
                print(f"Tiempo total (segundos): {tiempo_total}")
                print(f"Tiempo transcurrido (segundos): {tiempo_transcurrido}")
                print(f"Segundos restantes: {segundos_restantes}")
                print(f"Porcentaje restante: {porcentaje_restante}%")
                print(f"Horas: {horas}, Minutos: {minutos}")
                
                if segundos_restantes < 0:
                    if horas > 0:
                        sla_restante = f"-{horas}h {minutos}m"
                    else:
                        sla_restante = f"-{minutos}m"
                    sla_color = 'text-danger'
                elif porcentaje_restante > 40:
                    if horas > 0:
                        sla_restante = f"{horas}h {minutos}m"
                    else:
                        sla_restante = f"{minutos}m"
                    sla_color = 'text-success'
                elif porcentaje_restante > 0:
                    if horas > 0:
                        sla_restante = f"{horas}h {minutos}m"
                    else:
                        sla_restante = f"{minutos}m"
                    sla_color = 'text-warning'
                else:
                    if horas > 0:
                        sla_restante = f"-{horas}h {minutos}m"
                    else:
                        sla_restante = f"-{minutos}m"
                    sla_color = 'text-danger'
                
                print(f"Calculated SLA restante: {sla_restante}")
                print(f"Calculated SLA color: {sla_color}")
            else:
                print("No SLA defined for this etapa")
                sla_restante = 'N/A'
                sla_color = 'text-secondary'
                print(f"Default SLA restante: {sla_restante}")
                print(f"Default SLA color: {sla_color}")
        else:
            print("No etapa_actual found")

if __name__ == "__main__":
    debug_sla_calculation()
