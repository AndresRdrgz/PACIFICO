from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from pacifico.models import GroupProfile, SUCURSALES_OPCIONES


class Command(BaseCommand):
    help = 'Crea grupos automáticamente para cada sucursal con sus respectivos perfiles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué grupos se crearían sin crearlos realmente',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 MODO DRY-RUN: Solo mostrando qué se haría\n')
            )

        self.stdout.write('=== CONFIGURACIÓN DE GRUPOS DE SUCURSALES ===\n')

        grupos_creados = 0
        grupos_existentes = 0

        for codigo, nombre in SUCURSALES_OPCIONES:
            # Nombres de grupos por sucursal
            grupos_sucursal = [
                f"Oficiales - {nombre}",
                f"Asistentes - {nombre}",
                f"Supervisores - {nombre}",
            ]

            for nombre_grupo in grupos_sucursal:
                if dry_run:
                    # En dry-run, solo verificar si existe
                    exists = Group.objects.filter(name=nombre_grupo).exists()
                    if exists:
                        self.stdout.write(f"  ⚠️  Ya existe: {nombre_grupo}")
                        grupos_existentes += 1
                    else:
                        self.stdout.write(f"  ✅ Se crearía: {nombre_grupo}")
                        grupos_creados += 1
                else:
                    # Crear grupo real
                    grupo, created = Group.objects.get_or_create(name=nombre_grupo)
                    
                    if created:
                        self.stdout.write(
                            self.style.SUCCESS(f"✅ Grupo creado: {nombre_grupo}")
                        )
                        grupos_creados += 1
                    else:
                        grupos_existentes += 1

                    # Crear o actualizar GroupProfile
                    profile, profile_created = GroupProfile.objects.get_or_create(
                        group=grupo,
                        defaults={
                            'es_sucursal': True,
                            'sucursal_codigo': codigo,
                            'descripcion': f'Grupo de {nombre_grupo.split(" - ")[0].lower()} para la sucursal {nombre}',
                            'activo': True
                        }
                    )
                    
                    if not profile_created:
                        # Actualizar profile existente para asegurar consistencia
                        profile.es_sucursal = True
                        profile.sucursal_codigo = codigo
                        if not profile.descripcion:
                            profile.descripcion = f'Grupo de {nombre_grupo.split(" - ")[0].lower()} para la sucursal {nombre}'
                        profile.save()

        # Crear también grupos generales (no de sucursal)
        grupos_generales = [
            ("Administradores", "Grupo de administradores del sistema"),
            ("Comité de Crédito", "Grupo para miembros del comité de crédito"),
            ("Canal Digital", "Grupo para usuarios del canal digital"),
        ]

        self.stdout.write('\n=== GRUPOS GENERALES ===\n')

        for nombre_grupo, descripcion in grupos_generales:
            if dry_run:
                exists = Group.objects.filter(name=nombre_grupo).exists()
                if exists:
                    self.stdout.write(f"  ⚠️  Ya existe: {nombre_grupo}")
                    grupos_existentes += 1
                else:
                    self.stdout.write(f"  ✅ Se crearía: {nombre_grupo}")
                    grupos_creados += 1
            else:
                grupo, created = Group.objects.get_or_create(name=nombre_grupo)
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Grupo creado: {nombre_grupo}")
                    )
                    grupos_creados += 1
                else:
                    grupos_existentes += 1

                # Crear GroupProfile para grupos generales (no sucursal)
                profile, profile_created = GroupProfile.objects.get_or_create(
                    group=grupo,
                    defaults={
                        'es_sucursal': False,
                        'descripcion': descripcion,
                        'activo': True
                    }
                )

        # Resumen
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'📊 RESUMEN (DRY-RUN):\n'
                    f'  - Grupos que se crearían: {grupos_creados}\n'
                    f'  - Grupos que ya existen: {grupos_existentes}\n'
                    f'\n💡 Ejecuta sin --dry-run para crear los grupos realmente'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'📊 RESUMEN:\n'
                    f'  - Grupos creados: {grupos_creados}\n'
                    f'  - Grupos ya existentes: {grupos_existentes}\n'
                    f'\n✅ ¡Configuración completada!'
                    f'\n\n💡 Ahora puedes:'
                    f'\n  1. Ir al admin de Django (/admin/)'
                    f'\n  2. Ver "Grupos" para asignar usuarios'
                    f'\n  3. Ver "Perfiles de Grupos" para verificar la configuración'
                )
            )
