"""
Django management command to resend resultado consulta email for a specific solicitud
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from workflow.modelsWorkflow import Solicitud
from workflow.views_workflow import enviar_correo_pdf_resultado_consulta


class Command(BaseCommand):
    help = 'Resend resultado consulta email with PDF for a specific solicitud'

    def add_arguments(self, parser):
        parser.add_argument(
            'solicitud_id',
            type=int,
            help='ID of the solicitud to resend resultado consulta email'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending the email',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        solicitud_id = options['solicitud_id']
        dry_run = options.get('dry_run', False)
        force = options.get('force', False)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"🔍 Resultado Consulta Email Resend - Solicitud ID: {solicitud_id}"
            )
        )
        self.stdout.write("=" * 60)
        
        try:
            # Get solicitud
            solicitud = Solicitud.objects.get(pk=solicitud_id)
            
            # Display solicitud info
            self.stdout.write(f"📋 Información de la Solicitud:")
            self.stdout.write(f"   - Código: {solicitud.codigo}")
            self.stdout.write(f"   - Cliente: {getattr(solicitud.cliente, 'nombreCliente', 'N/A') if solicitud.cliente else 'N/A'}")
            self.stdout.write(f"   - Cédula: {getattr(solicitud.cliente, 'cedulaCliente', 'N/A') if solicitud.cliente else 'N/A'}")
            self.stdout.write(f"   - Propietario: {solicitud.propietario.get_full_name() if solicitud.propietario else 'Sin propietario'}")
            self.stdout.write(f"   - Email: {solicitud.propietario.email if solicitud.propietario else 'Sin email'}")
            self.stdout.write(f"   - Pipeline: {solicitud.pipeline.nombre if solicitud.pipeline else 'N/A'}")
            self.stdout.write(f"   - Etapa: {solicitud.etapa_actual.nombre if solicitud.etapa_actual else 'N/A'}")
            self.stdout.write(f"   - Subestado: {solicitud.subestado_actual.nombre if solicitud.subestado_actual else 'N/A'}")
            self.stdout.write(f"   - Fecha creación: {solicitud.fecha_creacion}")
            
            # Check if solicitud has valid email
            if not solicitud.propietario or not solicitud.propietario.email:
                raise CommandError(
                    f"❌ Error: La solicitud {solicitud_id} no tiene propietario con email válido"
                )
            
            # Check related data
            self.stdout.write(f"\n🔍 Verificando datos relacionados:")
            
            # Check calificaciones
            from workflow.models import CalificacionCampo
            calificaciones_count = CalificacionCampo.objects.filter(solicitud=solicitud).count()
            self.stdout.write(f"   - Calificaciones: {calificaciones_count} registros")
            
            # Check comentarios analista
            from workflow.modelsWorkflow import SolicitudComentario
            comentarios_count = SolicitudComentario.objects.filter(
                solicitud=solicitud,
                tipo="analista_credito"
            ).count()
            self.stdout.write(f"   - Comentarios analista: {comentarios_count} registros")
            
            # Check comentarios compliance
            from workflow.models import ComentarioDocumentoBackoffice
            compliance_count = ComentarioDocumentoBackoffice.objects.filter(
                requisito_solicitud__solicitud=solicitud
            ).count()
            self.stdout.write(f"   - Comentarios compliance: {compliance_count} registros")
            
            # Check cotizacion
            if solicitud.cotizacion:
                monto = ""
                if hasattr(solicitud.cotizacion, 'montoPrestamo') and solicitud.cotizacion.montoPrestamo:
                    monto = f" (Monto: B/. {solicitud.cotizacion.montoPrestamo:,.2f})"
                self.stdout.write(f"   - Cotización: Sí{monto}")
            else:
                self.stdout.write(f"   - Cotización: No")
            
            # Determine email style based on subestado
            status_info = self._get_status_info(solicitud)
            self.stdout.write(f"   - Estilo del email: {status_info['description']}")
            
            if dry_run:
                self.stdout.write(f"\n🧪 MODO DRY-RUN - NO SE ENVIARÁ EMAIL REAL")
                self.stdout.write(f"   - Destinatario: {solicitud.propietario.email}")
                self.stdout.write(f"   - Asunto: Resultado Consulta - Solicitud {solicitud.codigo}")
                self.stdout.write(f"   - Archivo adjunto: resultado_consulta_solicitud_{solicitud.codigo}.pdf")
                self.stdout.write(f"   - Estado: {status_info['text']}")
                self.stdout.write(self.style.WARNING("✅ Dry-run completado - No se envió email real"))
                return
            
            # Confirmation unless forced
            if not force:
                self.stdout.write(f"\n📧 Email será enviado a: {solicitud.propietario.email}")
                response = input("¿Confirma el envío del email? (sí/no): ").strip().lower()
                if response not in ['sí', 'si', 'yes', 'y', 's']:
                    self.stdout.write(self.style.WARNING("❌ Envío cancelado por el usuario"))
                    return
            
            # Send email
            self.stdout.write(f"\n📤 Enviando correo con PDF...")
            
            # Call the actual email function
            enviar_correo_pdf_resultado_consulta(solicitud)
            
            # Success message
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ ¡Correo enviado exitosamente!"
                )
            )
            self.stdout.write(f"   - Destinatario: {solicitud.propietario.email}")
            self.stdout.write(f"   - Solicitud: {solicitud.codigo}")
            self.stdout.write(f"   - Fecha/Hora: {timezone.now().strftime('%d/%m/%Y %H:%M:%S')}")
            self.stdout.write(f"   - Estado: {status_info['text']}")
            
        except Solicitud.DoesNotExist:
            raise CommandError(f"❌ Solicitud con ID {solicitud_id} no encontrada")
        except Exception as e:
            import traceback
            self.stdout.write(self.style.ERROR(f"❌ Error: {str(e)}"))
            if options.get('verbosity', 1) >= 2:
                self.stdout.write(traceback.format_exc())
            raise CommandError(f"Error procesando solicitud {solicitud_id}: {str(e)}")

    def _get_status_info(self, solicitud):
        """
        Get status information for email styling
        """
        if not solicitud.subestado_actual:
            return {
                'text': 'En Proceso',
                'description': 'Azul (En Proceso)'
            }
        
        subestado_nombre = solicitud.subestado_actual.nombre.lower()
        
        if 'aprobado' in subestado_nombre or 'aprueba' in subestado_nombre or 'autorizado' in subestado_nombre:
            return {
                'text': 'Aprobado',
                'description': 'Verde (Aprobado)'
            }
        elif 'alternativa' in subestado_nombre:
            return {
                'text': 'Alternativa',
                'description': 'Amarillo/Naranja (Alternativa)'
            }
        elif 'rechazado' in subestado_nombre or 'rechaza' in subestado_nombre or 'negado' in subestado_nombre:
            return {
                'text': 'Rechazado',
                'description': 'Rojo (Rechazado)'
            }
        else:
            return {
                'text': 'En Proceso',
                'description': 'Azul (En Proceso)'
            }
