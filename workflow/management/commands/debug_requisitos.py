from django.core.management.base import BaseCommand
from workflow.modelsWorkflow import Solicitud, TransicionEtapa, RequisitoTransicion, RequisitoSolicitud


class Command(BaseCommand):
    help = 'Debug requisitos for a specific solicitud and transition'

    def add_arguments(self, parser):
        parser.add_argument('solicitud_id', type=int, help='ID of the solicitud')
        parser.add_argument('--etapa-destino', type=int, help='ID of the destination etapa')

    def handle(self, *args, **options):
        solicitud_id = options['solicitud_id']
        etapa_destino_id = options.get('etapa_destino')
        
        try:
            solicitud = Solicitud.objects.get(id=solicitud_id)
            self.stdout.write(f"🔍 Analizando solicitud: {solicitud.codigo}")
            self.stdout.write(f"   Etapa actual: {solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'None'}")
            
            if etapa_destino_id:
                from workflow.modelsWorkflow import Etapa
                etapa_destino = Etapa.objects.get(id=etapa_destino_id)
                self.stdout.write(f"   Etapa destino: {etapa_destino.nombre}")
                
                # Buscar transición
                transicion = TransicionEtapa.objects.filter(
                    pipeline=solicitud.pipeline,
                    etapa_origen=solicitud.etapa_actual,
                    etapa_destino=etapa_destino
                ).first()
                
                if transicion:
                    self.stdout.write(f"✅ Transición encontrada: {transicion.nombre}")
                    
                    # Verificar requisitos de transición
                    requisitos_transicion = RequisitoTransicion.objects.filter(
                        transicion=transicion,
                        obligatorio=True
                    ).select_related('requisito')
                    
                    self.stdout.write(f"📋 Requisitos obligatorios para esta transición: {requisitos_transicion.count()}")
                    
                    for req_trans in requisitos_transicion:
                        self.stdout.write(f"   - {req_trans.requisito.nombre}")
                        
                        # Verificar estado en la solicitud
                        req_solicitud = RequisitoSolicitud.objects.filter(
                            solicitud=solicitud,
                            requisito=req_trans.requisito
                        ).first()
                        
                        if req_solicitud:
                            self.stdout.write(f"     ✅ Existe en solicitud")
                            self.stdout.write(f"     📁 Cumplido: {req_solicitud.cumplido}")
                            self.stdout.write(f"     📄 Archivo: {req_solicitud.archivo.name if req_solicitud.archivo else 'None'}")
                        else:
                            self.stdout.write(f"     ❌ No existe en solicitud")
                else:
                    self.stdout.write(f"❌ No se encontró transición válida")
            else:
                # Mostrar todas las transiciones disponibles
                transiciones = TransicionEtapa.objects.filter(
                    pipeline=solicitud.pipeline,
                    etapa_origen=solicitud.etapa_actual
                ).select_related('etapa_destino')
                
                self.stdout.write(f"📋 Transiciones disponibles desde {solicitud.etapa_actual.nombre}:")
                for trans in transiciones:
                    self.stdout.write(f"   - {trans.nombre} → {trans.etapa_destino.nombre}")
                    
                    # Contar requisitos obligatorios
                    req_count = RequisitoTransicion.objects.filter(
                        transicion=trans,
                        obligatorio=True
                    ).count()
                    self.stdout.write(f"     Requisitos obligatorios: {req_count}")
                    
        except Solicitud.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"❌ Solicitud {solicitud_id} no encontrada"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}")) 