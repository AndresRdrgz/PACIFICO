#!/usr/bin/env python
"""
Script para verificar la configuración de supervisores de grupo
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from django.contrib.auth.models import User, Group
from pacifico.models import GroupProfile
from workflow.modelsWorkflow import PermisoBandeja, PermisoPipeline, Etapa, Pipeline

def verificar_configuracion_supervisor(username):
    """Verifica la configuración completa de un supervisor"""
    print(f"🔍 VERIFICANDO CONFIGURACIÓN PARA: {username}")
    print("=" * 60)
    
    try:
        usuario = User.objects.get(username=username)
        print(f"✅ Usuario encontrado: {usuario.username} ({usuario.get_full_name()})")
        print(f"   - is_superuser: {usuario.is_superuser}")
        print(f"   - is_staff: {usuario.is_staff}")
        
        # Verificar UserProfile
        if hasattr(usuario, 'userprofile'):
            print(f"   - Rol: {usuario.userprofile.rol}")
            print(f"   - Sucursal: {usuario.userprofile.sucursal}")
        else:
            print("   ❌ No tiene UserProfile")
        
        print()
        
        # Verificar grupos del usuario
        grupos_usuario = usuario.groups.all()
        print(f"📋 GRUPOS DEL USUARIO ({grupos_usuario.count()}):")
        for grupo in grupos_usuario:
            print(f"   - {grupo.name}")
        print()
        
        # Verificar grupos que supervisa
        try:
            grupos_supervisados = GroupProfile.objects.filter(supervisores=usuario)
            print(f"👑 GRUPOS QUE SUPERVISA ({grupos_supervisados.count()}):")
            
            if grupos_supervisados.exists():
                for gp in grupos_supervisados:
                    print(f"   - {gp.group.name}")
                    print(f"     * Es sucursal: {gp.es_sucursal}")
                    print(f"     * Código sucursal: {gp.sucursal_codigo}")
                    print(f"     * Activo: {gp.activo}")
                    
                    # Verificar miembros del grupo
                    miembros = gp.group.user_set.all()
                    print(f"     * Miembros ({miembros.count()}): {[m.username for m in miembros]}")
                    print()
            else:
                print("   ❌ NO supervisa ningún grupo")
            
        except Exception as e:
            print(f"   ❌ Error verificando grupos supervisados: {e}")
        
        print()
        
        # Verificar permisos de bandeja
        if grupos_supervisados.exists():
            grupos_supervisados_list = [gp.group for gp in grupos_supervisados]
            
            print(f"🎯 PERMISOS DE BANDEJA:")
            permisos_bandeja = PermisoBandeja.objects.filter(grupo__in=grupos_supervisados_list)
            
            if permisos_bandeja.exists():
                for permiso in permisos_bandeja:
                    print(f"   - Etapa: {permiso.etapa.nombre} (Pipeline: {permiso.etapa.pipeline.nombre})")
                    print(f"     * Grupo: {permiso.grupo.name}")
                    print(f"     * Puede ver: {permiso.puede_ver}")
                    print(f"     * Puede tomar: {permiso.puede_tomar}")
                    print(f"     * Puede transicionar: {permiso.puede_transicionar}")
                    print(f"     * Puede editar: {permiso.puede_editar}")
                    print()
            else:
                print("   ❌ NO tiene permisos de bandeja configurados")
            
            print(f"🏗️ PERMISOS DE PIPELINE:")
            permisos_pipeline = PermisoPipeline.objects.filter(grupo__in=grupos_supervisados_list)
            
            if permisos_pipeline.exists():
                for permiso in permisos_pipeline:
                    print(f"   - Pipeline: {permiso.pipeline.nombre}")
                    print(f"     * Grupo: {permiso.grupo.name}")
                    print(f"     * Puede ver: {permiso.puede_ver}")
                    print(f"     * Puede crear: {permiso.puede_crear}")
                    print(f"     * Puede editar: {permiso.puede_editar}")
                    print(f"     * Puede eliminar: {permiso.puede_eliminar}")
                    print()
            else:
                print("   ❌ NO tiene permisos de pipeline configurados")
        
    except User.DoesNotExist:
        print(f"❌ Usuario '{username}' no encontrado")
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        print(traceback.format_exc())

def listar_todos_los_grupos():
    """Lista todos los grupos y sus supervisores"""
    print("\n" + "=" * 60)
    print("📋 TODOS LOS GRUPOS Y SUS SUPERVISORES:")
    print("=" * 60)
    
    grupos = Group.objects.all()
    for grupo in grupos:
        print(f"🏷️  {grupo.name}")
        
        try:
            profile = grupo.profile
            supervisores = profile.supervisores.all()
            if supervisores.exists():
                print(f"   👑 Supervisores: {[s.username for s in supervisores]}")
            else:
                print(f"   ❌ Sin supervisores")
            
            miembros = grupo.user_set.all()
            if miembros.exists():
                print(f"   👥 Miembros: {[m.username for m in miembros]}")
            else:
                print(f"   ❌ Sin miembros")
                
        except GroupProfile.DoesNotExist:
            print(f"   ❌ Sin GroupProfile")
        
        print()

if __name__ == "__main__":
    # Listar todos los grupos primero
    listar_todos_los_grupos()
    
    # Si se proporciona un username, verificar ese usuario específico
    if len(sys.argv) > 1:
        username = sys.argv[1]
        verificar_configuracion_supervisor(username)
    else:
        print("\n💡 Para verificar un usuario específico, ejecuta:")
        print("python debug_supervisor_config.py <username>")
