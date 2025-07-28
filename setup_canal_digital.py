#!/usr/bin/env python3
"""
Script para crear el grupo "Canal Digital" y configurar usuarios de prueba
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/Users/andresrdrgz_/Documents/GitHub/PACIFICO')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pacifico.settings')
django.setup()

from django.contrib.auth.models import Group, User

def crear_grupo_canal_digital():
    """Crear o obtener el grupo Canal Digital"""
    try:
        grupo, created = Group.objects.get_or_create(name="Canal Digital")
        if created:
            print("✅ Grupo 'Canal Digital' creado exitosamente")
        else:
            print("ℹ️  Grupo 'Canal Digital' ya existe")
        
        return grupo
    except Exception as e:
        print(f"❌ Error al crear grupo: {e}")
        return None

def mostrar_estadisticas_grupo():
    """Mostrar estadísticas del grupo Canal Digital"""
    try:
        grupo = Group.objects.get(name="Canal Digital")
        usuarios_en_grupo = grupo.user_set.filter(is_active=True)
        total_usuarios = User.objects.filter(is_active=True).count()
        
        print(f"\n📊 Estadísticas del grupo 'Canal Digital':")
        print(f"   👥 Usuarios en el grupo: {usuarios_en_grupo.count()}")
        print(f"   🔄 Total usuarios activos: {total_usuarios}")
        print(f"   📋 Usuarios disponibles para agregar: {total_usuarios - usuarios_en_grupo.count()}")
        
        if usuarios_en_grupo.exists():
            print(f"\n👤 Usuarios en el grupo:")
            for usuario in usuarios_en_grupo:
                nombre = usuario.get_full_name() or usuario.username
                print(f"   - {nombre} ({usuario.username}) - {usuario.email}")
        
        return grupo
    except Group.DoesNotExist:
        print("❌ El grupo 'Canal Digital' no existe")
        return None
    except Exception as e:
        print(f"❌ Error al obtener estadísticas: {e}")
        return None

def main():
    print("🚀 Configuración del Canal Digital")
    print("=" * 50)
    
    # Crear grupo
    grupo = crear_grupo_canal_digital()
    if not grupo:
        return
    
    # Mostrar estadísticas
    mostrar_estadisticas_grupo()
    
    print(f"\n✅ Configuración completada!")
    print(f"   💡 Los usuarios ahora pueden ser asignados al grupo 'Canal Digital' desde la interfaz web")
    print(f"   🌐 Solo los usuarios del grupo aparecerán en el selector de propietarios")

if __name__ == "__main__":
    main()
