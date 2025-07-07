import os
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pacifico.models import UserProfile

class Command(BaseCommand):
    help = 'Verifica los roles de los usuarios'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== VERIFICACIÓN DE ROLES DE USUARIOS ==='))
        
        users = User.objects.all()
        
        for user in users:
            self.stdout.write(f"\n👤 Usuario: {user.username}")
            self.stdout.write(f"   - Nombre completo: {user.get_full_name()}")
            self.stdout.write(f"   - Es superuser: {user.is_superuser}")
            self.stdout.write(f"   - Es staff: {user.is_staff}")
            
            # Verificar UserProfile
            try:
                profile = user.userprofile
                self.stdout.write(f"   - Rol en UserProfile: {profile.rol}")
                self.stdout.write(f"   - Sucursal: {profile.sucursal}")
            except:
                self.stdout.write(f"   - ❌ No tiene UserProfile")
            
            # Verificar grupos
            groups = user.groups.all()
            if groups.exists():
                group_names = [g.name for g in groups]
                self.stdout.write(f"   - Grupos: {group_names}")
            else:
                self.stdout.write(f"   - ❌ No tiene grupos asignados")
            
            self.stdout.write("-" * 50)
        
        self.stdout.write(self.style.SUCCESS('\n=== FIN DE VERIFICACIÓN ===')) 