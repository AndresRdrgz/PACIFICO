from django.core.management.base import BaseCommand
from pacifico.models import Sucursal, SUCURSALES_OPCIONES


class Command(BaseCommand):
    help = 'Migra las sucursales hardcodeadas al modelo dinámico Sucursal'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra qué sucursales se crearían sin crearlas realmente',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 MODO DRY-RUN: Solo mostrando qué se haría\n')
            )

        self.stdout.write('=== MIGRACIÓN DE SUCURSALES ===\n')

        sucursales_creadas = 0
        sucursales_existentes = 0

        for codigo, nombre in SUCURSALES_OPCIONES:
            if dry_run:
                # En dry-run, solo verificar si existe
                exists = Sucursal.objects.filter(codigo=codigo).exists()
                if exists:
                    self.stdout.write(f"  ⚠️  Ya existe: {codigo} - {nombre}")
                    sucursales_existentes += 1
                else:
                    self.stdout.write(f"  ✅ Se crearía: {codigo} - {nombre}")
                    sucursales_creadas += 1
            else:
                # Crear sucursal real
                sucursal, created = Sucursal.objects.get_or_create(
                    codigo=codigo,
                    defaults={
                        'nombre': nombre,
                        'activa': True
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Sucursal creada: {codigo} - {nombre}")
                    )
                    sucursales_creadas += 1
                else:
                    self.stdout.write(f"  ⚠️  Ya existía: {codigo} - {nombre}")
                    sucursales_existentes += 1

        # Resumen
        self.stdout.write('\n' + '='*50)
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(
                    f'📊 RESUMEN (DRY-RUN):\n'
                    f'  - Sucursales que se crearían: {sucursales_creadas}\n'
                    f'  - Sucursales que ya existen: {sucursales_existentes}\n'
                    f'\n💡 Ejecuta sin --dry-run para crear las sucursales realmente'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'📊 RESUMEN:\n'
                    f'  - Sucursales creadas: {sucursales_creadas}\n'
                    f'  - Sucursales ya existentes: {sucursales_existentes}\n'
                    f'\n✅ ¡Migración completada!'
                    f'\n\n💡 Ahora puedes:'
                    f'\n  1. Ir al admin de Django (/admin/)'
                    f'\n  2. Ver "Sucursales" para gestionar sucursales dinámicamente'
                    f'\n  3. Agregar nuevas sucursales sin tocar el código'
                    f'\n  4. Ejecutar las migraciones de Django para actualizar los campos'
                )
            )
