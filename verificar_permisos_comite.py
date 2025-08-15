#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar y configurar permisos de bandeja para el Comité de Crédito
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pacifico.settings')
django.setup()

from django.contrib.auth.models import User, Group
from workflow.modelsWorkflow import Etapa, PermisoBandeja
from pacifico.models import UserProfile

def verificar_etapa_comite():
    """Verificar que existe la etapa Comité de Crédito"""
    print("=" * 50)
    print("🔍 VERIFICANDO ETAPA COMITÉ DE CRÉDITO")
    print("=" * 50)
    
    etapa_comite = Etapa.objects.filter(nombre__iexact="Comité de Crédito").first()
    if etapa_comite:
        print(f"✅ Etapa encontrada: {etapa_comite.nombre}")
        print(f"   Pipeline: {etapa_comite.pipeline.nombre}")
        print(f"   Es bandeja grupal: {etapa_comite.es_bandeja_grupal}")
        return etapa_comite
    else:
        print("❌ No se encontró la etapa 'Comité de Crédito'")
        return None

def verificar_usuarios_analistas():
    """Verificar usuarios con rol de analista"""
    print("\n" + "=" * 50)
    print("👥 VERIFICANDO USUARIOS ANALISTAS")
    print("=" * 50)
    
    analistas = UserProfile.objects.filter(rol='Analista')
    print(f"📊 Total de analistas: {analistas.count()}")
    
    for profile in analistas:
        print(f"   📋 {profile.user.username} ({profile.user.first_name} {profile.user.last_name})")
    
    return analistas

def verificar_permisos_existentes(etapa_comite):
    """Verificar permisos existentes para la etapa comité"""
    print("\n" + "=" * 50)
    print("🔐 VERIFICANDO PERMISOS EXISTENTES")
    print("=" * 50)
    
    if not etapa_comite:
        print("❌ No se puede verificar permisos sin etapa")
        return
    
    permisos = PermisoBandeja.objects.filter(etapa=etapa_comite)
    print(f"📊 Total de permisos configurados: {permisos.count()}")
    
    for permiso in permisos:
        if permiso.usuario:
            print(f"   👤 Usuario: {permiso.usuario.username}")
        elif permiso.grupo:
            print(f"   👥 Grupo: {permiso.grupo.name}")
        
        print(f"      - Puede ver: {permiso.puede_ver}")
        print(f"      - Puede tomar: {permiso.puede_tomar}")
        print(f"      - Puede transicionar: {permiso.puede_transicionar}")

def crear_permiso_ejemplo(etapa_comite):
    """Crear un permiso de ejemplo para analistas"""
    print("\n" + "=" * 50)
    print("🛠️  CREANDO PERMISO DE EJEMPLO")
    print("=" * 50)
    
    if not etapa_comite:
        print("❌ No se puede crear permiso sin etapa")
        return
    
    # Buscar o crear grupo de analistas
    grupo_analistas, created = Group.objects.get_or_create(name="Analistas")
    if created:
        print(f"✅ Grupo 'Analistas' creado")
    else:
        print(f"📋 Grupo 'Analistas' ya existe")
    
    # Verificar si ya existe el permiso
    permiso_existente = PermisoBandeja.objects.filter(
        etapa=etapa_comite,
        grupo=grupo_analistas
    ).first()
    
    if permiso_existente:
        print(f"📋 Ya existe permiso para el grupo Analistas")
        print(f"   - Puede ver: {permiso_existente.puede_ver}")
        print(f"   - Puede tomar: {permiso_existente.puede_tomar}")
    else:
        # Crear el permiso
        permiso = PermisoBandeja.objects.create(
            etapa=etapa_comite,
            grupo=grupo_analistas,
            puede_ver=True,
            puede_tomar=True,
            puede_devolver=True,
            puede_transicionar=True,
            puede_editar=False
        )
        print(f"✅ Permiso creado para grupo Analistas")
        print(f"   - Puede ver: {permiso.puede_ver}")
        print(f"   - Puede tomar: {permiso.puede_tomar}")

def verificar_acceso_context_processor():
    """Simular el context processor para verificar acceso"""
    print("\n" + "=" * 50)
    print("🔍 SIMULANDO CONTEXT PROCESSOR")
    print("=" * 50)
    
    # Buscar usuarios analistas
    analistas = User.objects.filter(userprofile__rol='Analista')
    
    for usuario in analistas:
        print(f"\n👤 Verificando acceso para: {usuario.username}")
        
        # Simular la lógica del context processor
        can_access_comite = False
        
        # Verificar permisos directos por usuario
        permisos_usuario = PermisoBandeja.objects.filter(
            usuario=usuario,
            etapa__nombre__iexact="Comité de Crédito",
            puede_ver=True
        )
        
        if permisos_usuario.exists():
            can_access_comite = True
            print(f"   ✅ Acceso por permiso directo de usuario")
        
        # Verificar permisos por grupos
        user_groups = usuario.groups.all()
        if user_groups.exists():
            permisos_grupo = PermisoBandeja.objects.filter(
                grupo__in=user_groups,
                etapa__nombre__iexact="Comité de Crédito",
                puede_ver=True
            )
            
            if permisos_grupo.exists():
                can_access_comite = True
                grupos = [g.name for g in user_groups if permisos_grupo.filter(grupo=g).exists()]
                print(f"   ✅ Acceso por grupos: {', '.join(grupos)}")
        
        if not can_access_comite:
            print(f"   ❌ Sin acceso al comité")
        
        resultado = "✅ SÍ" if can_access_comite else "❌ NO"
        print(f"   🎯 Resultado final: {resultado} puede acceder al comité")

def main():
    """Función principal"""
    print("🚀 VERIFICACIÓN DE PERMISOS COMITÉ DE CRÉDITO")
    print("=" * 70)
    
    # 1. Verificar etapa comité
    etapa_comite = verificar_etapa_comite()
    
    # 2. Verificar usuarios analistas
    analistas = verificar_usuarios_analistas()
    
    # 3. Verificar permisos existentes
    verificar_permisos_existentes(etapa_comite)
    
    # 4. Crear permiso de ejemplo (opcional)
    respuesta = input("\n¿Quieres crear un permiso de ejemplo para el grupo 'Analistas'? (s/n): ")
    if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
        crear_permiso_ejemplo(etapa_comite)
    
    # 5. Verificar acceso con context processor
    verificar_acceso_context_processor()
    
    print("\n" + "=" * 70)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("=" * 70)

if __name__ == "__main__":
    main()
