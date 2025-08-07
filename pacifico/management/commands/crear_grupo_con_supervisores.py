from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User
from pacifico.models import GroupProfile


class Command(BaseCommand):
    help = 'Crea un grupo con supervisores asignados'

    def add_arguments(self, parser):
        parser.add_argument(
            'nombre_grupo',
            type=str,
            help='Nombre del grupo a crear (ej: "Guapos")'
        )
        parser.add_argument(
            '--supervisores',
            nargs='+',
            type=str,
            help='Lista de usernames de supervisores (ej: --supervisores supervisor1 supervisor2)'
        )
        parser.add_argument(
            '--descripcion',
            type=str,
            default='',
            help='Descripción del grupo'
        )
        parser.add_argument(
            '--es-sucursal',
            action='store_true',
            help='Marcar si es un grupo de sucursal'
        )
        parser.add_argument(
            '--sucursal-codigo',
            type=str,
            help='Código de sucursal si es un grupo de sucursal'
        )

    def handle(self, *args, **options):
        nombre_grupo = options['nombre_grupo']
        supervisores_usernames = options.get('supervisores', [])
        descripcion = options.get('descripcion', '')
        es_sucursal = options.get('es_sucursal', False)
        sucursal_codigo = options.get('sucursal_codigo')

        self.stdout.write(f'=== CREANDO GRUPO "{nombre_grupo}" ===\n')

        # Crear o obtener el grupo
        grupo, created = Group.objects.get_or_create(name=nombre_grupo)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Grupo "{nombre_grupo}" creado')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Grupo "{nombre_grupo}" ya existía')
            )

        # Crear o actualizar GroupProfile
        grupo_profile, profile_created = GroupProfile.objects.get_or_create(
            group=grupo,
            defaults={
                'descripcion': descripcion,
                'es_sucursal': es_sucursal,
                'sucursal_codigo': sucursal_codigo if es_sucursal else None,
                'activo': True
            }
        )

        if profile_created:
            self.stdout.write(
                self.style.SUCCESS('✅ Perfil de grupo creado')
            )
        else:
            # Actualizar perfil existente
            if descripcion:
                grupo_profile.descripcion = descripcion
            grupo_profile.es_sucursal = es_sucursal
            grupo_profile.sucursal_codigo = sucursal_codigo if es_sucursal else None
            grupo_profile.save()
            self.stdout.write(
                self.style.SUCCESS('✅ Perfil de grupo actualizado')
            )

        # Asignar supervisores
        supervisores_asignados = 0
        supervisores_errores = 0

        if supervisores_usernames:
            self.stdout.write('\n--- ASIGNANDO SUPERVISORES ---')
            
            for username in supervisores_usernames:
                try:
                    supervisor = User.objects.get(username=username)
                    
                    # Verificar que tenga rol apropiado
                    if hasattr(supervisor, 'userprofile'):
                        if supervisor.userprofile.rol in ['Supervisor', 'Administrador']:
                            grupo_profile.supervisores.add(supervisor)
                            supervisores_asignados += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'✅ Supervisor asignado: {username} ({supervisor.userprofile.rol})'
                                )
                            )
                        else:
                            supervisores_errores += 1
                            self.stdout.write(
                                self.style.ERROR(
                                    f'❌ {username} no tiene rol de Supervisor o Administrador (rol actual: {supervisor.userprofile.rol})'
                                )
                            )
                    else:
                        supervisores_errores += 1
                        self.stdout.write(
                            self.style.ERROR(f'❌ {username} no tiene UserProfile')
                        )
                        
                except User.DoesNotExist:
                    supervisores_errores += 1
                    self.stdout.write(
                        self.style.ERROR(f'❌ Usuario {username} no encontrado')
                    )

        # Resumen
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'📊 RESUMEN:\n'
                f'  - Grupo: {nombre_grupo}\n'
                f'  - Descripción: {descripcion or "Sin descripción"}\n'
                f'  - Es sucursal: {"Sí" if es_sucursal else "No"}\n'
                f'  - Código sucursal: {sucursal_codigo or "N/A"}\n'
                f'  - Supervisores asignados: {supervisores_asignados}\n'
                f'  - Errores en supervisores: {supervisores_errores}\n'
                f'\n✅ ¡Grupo configurado exitosamente!'
                f'\n\n💡 Próximos pasos:'
                f'\n  1. Ir al admin (/admin/) → Grupos → "{nombre_grupo}"'
                f'\n  2. Agregar usuarios oficiales al grupo'
                f'\n  3. Los supervisores podrán ver solicitudes del grupo'
            )
        )

        # Mostrar supervisores actuales
        supervisores_actuales = grupo_profile.supervisores.all()
        if supervisores_actuales:
            self.stdout.write('\n👥 SUPERVISORES ACTUALES:')
            for supervisor in supervisores_actuales:
                rol = supervisor.userprofile.rol if hasattr(supervisor, 'userprofile') else 'Sin rol'
                self.stdout.write(f'  - {supervisor.username} ({rol})')
