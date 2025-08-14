from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pacifico.models import UserProfile


class Command(BaseCommand):
    help = 'Configura usuarios con el rol Back Office y muestra información sobre permisos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nombre de usuario específico para asignar rol Back Office'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='Listar usuarios con rol Back Office'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Configuración del Rol Back Office\n')
        )
        
        if options['list']:
            self.list_backoffice_users()
            return
        
        if options['username']:
            self.assign_backoffice_role(options['username'])
        else:
            self.show_help_info()

    def list_backoffice_users(self):
        """Listar usuarios con rol Back Office"""
        self.stdout.write('\n📋 Usuarios con Rol Back Office:')
        self.stdout.write('=' * 50)
        
        try:
            backoffice_users = UserProfile.objects.filter(rol='Back Office').select_related('user')
            
            if not backoffice_users.exists():
                self.stdout.write(
                    self.style.WARNING('  No hay usuarios con rol Back Office asignado.')
                )
                return
            
            for profile in backoffice_users:
                user = profile.user
                self.stdout.write(
                    f'  👤 {user.username} - {user.get_full_name() or "Sin nombre"}'
                )
                self.stdout.write(f'      📧 {user.email or "Sin email"}')
                self.stdout.write(f'      🏢 Sucursal: {profile.sucursal or "No asignada"}')
                self.stdout.write('')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  Error al listar usuarios: {str(e)}')
            )

    def assign_backoffice_role(self, username):
        """Asignar rol Back Office a un usuario específico"""
        self.stdout.write(f'\n🔐 Asignando rol Back Office a usuario: {username}')
        self.stdout.write('=' * 50)
        
        try:
            # Buscar usuario
            user = User.objects.get(username=username)
            
            # Obtener o crear UserProfile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={'rol': 'Back Office'}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Creado UserProfile para {username} con rol Back Office')
                )
            else:
                # Actualizar rol existente
                old_role = profile.rol
                profile.rol = 'Back Office'
                profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Usuario {username} actualizado de rol "{old_role}" a "Back Office"')
                )
            
            # Mostrar información del usuario
            self.stdout.write(f'\n📊 Información del Usuario:')
            self.stdout.write(f'  👤 Username: {user.username}')
            self.stdout.write(f'  📝 Nombre: {user.get_full_name() or "Sin nombre"}')
            self.stdout.write(f'  📧 Email: {user.email or "Sin email"}')
            self.stdout.write(f'  🏢 Sucursal: {profile.sucursal or "No asignada"}')
            self.stdout.write(f'  🔑 Rol: {profile.rol}')
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Usuario "{username}" no encontrado')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error: {str(e)}')
            )

    def show_help_info(self):
        """Mostrar información de ayuda"""
        self.stdout.write('\n📚 Información del Rol Back Office:')
        self.stdout.write('=' * 50)
        
        self.stdout.write('\n🔐 Permisos del Rol Back Office:')
        self.stdout.write('  ✅ Acceso a Bandejas de Trabajo (con PermisoBandeja específico)')
        self.stdout.write('  ✅ Vista de Análisis de Solicitudes')
        self.stdout.write('  ✅ Gestión de Requisitos de Transición')
        self.stdout.write('  ✅ Acceso a Solicitudes Asignadas')
        self.stdout.write('  ✅ Filtros por Etapa y Pipeline')
        
        self.stdout.write('\n🔄 Comandos Disponibles:')
        self.stdout.write('  python manage.py setup_backoffice_role --username <username>')
        self.stdout.write('    → Asignar rol Back Office a un usuario específico')
        self.stdout.write('  python manage.py setup_backoffice_role --list')
        self.stdout.write('    → Listar usuarios con rol Back Office')
        
        self.stdout.write('\n💡 Ejemplos de Uso:')
        self.stdout.write('  python manage.py setup_backoffice_role --username juan.perez')
        self.stdout.write('  python manage.py setup_backoffice_role --list')
        
        self.stdout.write('\n⚠️  Notas Importantes:')
        self.stdout.write('  • El rol Back Office tiene los mismos permisos que Analista')
        self.stdout.write('  • Solo pueden ver bandejas donde tengan PermisoBandeja específico')
        self.stdout.write('  • No tienen acceso automático a todas las bandejas grupales')
        self.stdout.write('  • Requieren configuración manual de PermisoBandeja para cada etapa')
