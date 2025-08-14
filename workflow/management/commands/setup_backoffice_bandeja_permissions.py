from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pacifico.models import UserProfile
from workflow.modelsWorkflow import Etapa, PermisoBandeja


class Command(BaseCommand):
    help = 'Configura automáticamente los permisos de bandeja para usuarios con rol Back Office'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nombre de usuario específico para configurar permisos'
        )
        parser.add_argument(
            '--etapa',
            type=str,
            help='Nombre de etapa específica para configurar'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Configurar permisos para todos los usuarios Back Office en todas las etapas'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='Listar permisos de bandeja existentes'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Configuración de Permisos de Bandeja para Back Office\n')
        )
        
        if options['list']:
            self.list_existing_permissions()
            return
        
        if options['username']:
            self.setup_user_permissions(options['username'], options['etapa'])
        elif options['all']:
            self.setup_all_backoffice_users()
        else:
            self.show_help_info()

    def setup_user_permissions(self, username, etapa_nombre=None):
        """Configurar permisos de bandeja para un usuario específico"""
        self.stdout.write(f'\n🔐 Configurando permisos para usuario: {username}')
        self.stdout.write('=' * 60)
        
        try:
            user = User.objects.get(username=username)
            profile = UserProfile.objects.get(user=user)
            
            if profile.rol != 'Back Office':
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Usuario {username} no tiene rol "Back Office" (tiene: {profile.rol})')
                )
                return
            
            self.stdout.write(f'  👤 Usuario: {user.username}')
            self.stdout.write(f'  🔑 Rol: {profile.rol}')
            
            # Obtener etapas con bandeja grupal
            etapas_query = Etapa.objects.filter(es_bandeja_grupal=True)
            
            if etapa_nombre:
                etapas_query = etapas_query.filter(nombre__icontains=etapa_nombre)
            
            etapas = etapas_query.exclude(nombre__iexact="Comité de Crédito")
            
            if not etapas.exists():
                self.stdout.write(
                    self.style.WARNING('  No hay etapas con bandeja grupal disponibles para configurar.')
                )
                return
            
            self.stdout.write(f'\n📋 Configurando permisos en {etapas.count()} etapas:')
            self.stdout.write('=' * 40)
            
            permisos_creados = 0
            permisos_actualizados = 0
            
            for etapa in etapas:
                self.stdout.write(f'\n  🏢 Etapa: {etapa.nombre}')
                self.stdout.write(f'     📍 ID: {etapa.id}')
                self.stdout.write(f'     🔗 Pipeline: {etapa.pipeline.nombre}')
                
                # Verificar si ya existe un permiso
                permiso_existente, created = PermisoBandeja.objects.get_or_create(
                    etapa=etapa,
                    usuario=user,
                    defaults={
                        'puede_ver': True,
                        'puede_tomar': True,
                        'puede_devolver': True,
                        'puede_transicionar': True,
                        'puede_editar': False
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'     ✅ Permiso creado exitosamente')
                    )
                    permisos_creados += 1
                else:
                    # Actualizar permisos existentes
                    old_tomar = permiso_existente.puede_tomar
                    old_ver = permiso_existente.puede_ver
                    
                    permiso_existente.puede_ver = True
                    permiso_existente.puede_tomar = True
                    permiso_existente.puede_devolver = True
                    permiso_existente.puede_transicionar = True
                    permiso_existente.save()
                    
                    if old_tomar != True or old_ver != True:
                        self.stdout.write(
                            self.style.SUCCESS(f'     🔄 Permiso actualizado (antes: ver={old_ver}, tomar={old_tomar})')
                        )
                        permisos_actualizados += 1
                    else:
                        self.stdout.write(
                            self.style.WARNING(f'     ⚠️  Permiso ya existía con configuración correcta')
                        )
                
                # Mostrar estado final del permiso
                self.stdout.write(f'     📊 Estado final:')
                self.stdout.write(f'        Ver: {permiso_existente.puede_ver}')
                self.stdout.write(f'        Tomar: {permiso_existente.puede_tomar}')
                self.stdout.write(f'        Devolver: {permiso_existente.puede_devolver}')
                self.stdout.write(f'        Transicionar: {permiso_existente.puede_transicionar}')
                self.stdout.write(f'        Editar: {permiso_existente.puede_editar}')
            
            # Resumen final
            self.stdout.write(f'\n🎉 Resumen de Configuración:')
            self.stdout.write('=' * 40)
            self.stdout.write(f'  ✅ Permisos creados: {permisos_creados}')
            self.stdout.write(f'  🔄 Permisos actualizados: {permisos_actualizados}')
            self.stdout.write(f'  📋 Total de etapas configuradas: {etapas.count()}')
            
            if permisos_creados > 0 or permisos_actualizados > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'\n  🎯 El usuario {username} ahora puede tomar solicitudes en todas las etapas configuradas!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'\n  ⚠️  No se realizaron cambios. El usuario ya tenía todos los permisos necesarios.')
                )
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Usuario "{username}" no encontrado')
            )
        except UserProfile.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'  ❌ UserProfile no encontrado para {username}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ❌ Error: {str(e)}')
            )

    def setup_all_backoffice_users(self):
        """Configurar permisos para todos los usuarios Back Office"""
        self.stdout.write('\n🔐 Configurando permisos para todos los usuarios Back Office')
        self.stdout.write('=' * 60)
        
        try:
            backoffice_users = UserProfile.objects.filter(rol='Back Office').select_related('user')
            
            if not backoffice_users.exists():
                self.stdout.write(
                    self.style.WARNING('  No hay usuarios con rol Back Office asignado.')
                )
                return
            
            for profile in backoffice_users:
                self.setup_user_permissions(profile.user.username)
                self.stdout.write('')  # Línea en blanco entre usuarios
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  Error al listar usuarios: {str(e)}')
            )

    def list_existing_permissions(self):
        """Listar permisos de bandeja existentes"""
        self.stdout.write('\n📋 Permisos de Bandeja Existentes:')
        self.stdout.write('=' * 50)
        
        try:
            permisos = PermisoBandeja.objects.select_related('etapa', 'usuario', 'grupo').order_by('etapa__nombre', 'usuario__username')
            
            if not permisos.exists():
                self.stdout.write('  No hay permisos de bandeja configurados.')
                return
            
            etapa_actual = None
            for permiso in permisos:
                if permiso.etapa != etapa_actual:
                    etapa_actual = permiso.etapa
                    self.stdout.write(f'\n🏢 Etapa: {etapa_actual.nombre}')
                    self.stdout.write(f'   📍 ID: {etapa_actual.id}')
                    self.stdout.write(f'   🔗 Pipeline: {etapa_actual.pipeline.nombre}')
                
                if permiso.usuario:
                    self.stdout.write(f'   👤 {permiso.usuario.username}:')
                elif permiso.grupo:
                    self.stdout.write(f'   👥 Grupo {permiso.grupo.name}:')
                
                self.stdout.write(f'      Ver: {permiso.puede_ver}, Tomar: {permiso.puede_tomar}, Transicionar: {permiso.puede_transicionar}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  Error al listar permisos: {str(e)}')
            )

    def show_help_info(self):
        """Mostrar información de ayuda"""
        self.stdout.write('\n📚 Ayuda para Configurar Permisos de Bandeja:')
        self.stdout.write('=' * 50)
        
        self.stdout.write('\n🔧 Comandos Disponibles:')
        self.stdout.write('  python manage.py setup_backoffice_bandeja_permissions --username javito2')
        self.stdout.write('    → Configurar permisos para un usuario específico')
        self.stdout.write('  python manage.py setup_backoffice_bandeja_permissions --username javito2 --etapa Validación')
        self.stdout.write('    → Configurar permisos para un usuario en una etapa específica')
        self.stdout.write('  python manage.py setup_backoffice_bandeja_permissions --all')
        self.stdout.write('    → Configurar permisos para todos los usuarios Back Office')
        self.stdout.write('  python manage.py setup_backoffice_bandeja_permissions --list')
        self.stdout.write('    → Listar permisos de bandeja existentes')
        
        self.stdout.write('\n💡 Ejemplos de Uso:')
        self.stdout.write('  python manage.py setup_backoffice_bandeja_permissions --username javito2')
        self.stdout.write('  python manage.py setup_backoffice_bandeja_permissions --all')
        self.stdout.write('  python manage.py setup_backoffice_bandeja_permissions --list')
        
        self.stdout.write('\n⚠️  Notas Importantes:')
        self.stdout.write('  • Solo se configuran etapas con es_bandeja_grupal=True')
        self.stdout.write('  • Se excluye automáticamente la etapa "Comité de Crédito"')
        self.stdout.write('  • Los permisos se crean con puede_tomar=True por defecto')
        self.stdout.write('  • Los permisos existentes se actualizan si es necesario')
