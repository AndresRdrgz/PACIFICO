from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from workflow.models import Etapa, PermisoBandeja

class Command(BaseCommand):
    help = 'Crea los grupos necesarios para las restricciones de navegación del sidebar'

    def handle(self, *args, **options):
        # Crear grupo Comité de Crédito
        comite_group, created = Group.objects.get_or_create(name="Comité de Crédito")
        if created:
            self.stdout.write(
                self.style.SUCCESS('Grupo "Comité de Crédito" creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Grupo "Comité de Crédito" ya existe')
            )

        # Crear grupo Canal Digital
        canal_group, created = Group.objects.get_or_create(name="Canal Digital")
        if created:
            self.stdout.write(
                self.style.SUCCESS('Grupo "Canal Digital" creado exitosamente')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Grupo "Canal Digital" ya existe')
            )

        # Mostrar información sobre las etapas de bandeja grupal existentes
        etapas_grupales = Etapa.objects.filter(es_bandeja_grupal=True)
        if etapas_grupales.exists():
            self.stdout.write(
                self.style.SUCCESS(f'\nEtapas de bandeja grupal encontradas ({etapas_grupales.count()}):')
            )
            for etapa in etapas_grupales:
                permisos_count = PermisoBandeja.objects.filter(etapa=etapa).count()
                self.stdout.write(f'  - {etapa.nombre} (Pipeline: {etapa.pipeline.nombre}) - {permisos_count} permisos configurados')
        else:
            self.stdout.write(
                self.style.WARNING('\nNo se encontraron etapas de bandeja grupal.')
            )
            self.stdout.write(
                'Para configurar una etapa como bandeja grupal, '
                'marca el campo "es_bandeja_grupal" como True en el admin de Django.'
            )

        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Configuración completada. Los grupos están listos para usar.\n'
                '\nPara asignar usuarios a estos grupos:'
                '\n1. Ve al admin de Django (/admin/)'
                '\n2. Navega a Authentication and Authorization > Users'
                '\n3. Edita un usuario y asígnalo a los grupos correspondientes'
                '\n\nPara configurar permisos de bandejas grupales:'
                '\n1. Ve al admin de Django'
                '\n2. Navega a Workflow > Permisos de Bandeja'
                '\n3. Crea permisos para relacionar grupos con etapas de bandeja grupal'
            )
        )
