"""
Script para verificar y configurar permisos de bandeja para el Comité de Crédito
Ejecutar con: python manage.py shell < verificar_permisos_comite_shell.py
"""

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

# Ejecutar las verificaciones
print("🚀 VERIFICACIÓN DE PERMISOS COMITÉ DE CRÉDITO")
print("=" * 70)

etapa_comite = verificar_etapa_comite()
analistas = verificar_usuarios_analistas()
verificar_permisos_existentes(etapa_comite)

print("\n" + "=" * 70)
print("✅ VERIFICACIÓN COMPLETADA")
print("Para habilitar el acceso de analistas al comité:")
print("1. Ve al admin de Django")
print("2. Busca 'Permisos de Bandeja' o 'PermisoBandeja'") 
print("3. Crea un nuevo permiso:")
print("   - Etapa: Comité de Crédito")
print("   - Grupo: (el grupo donde están los analistas)")
print("   - Puede ver: ✓")
print("   - Puede tomar: ✓ (opcional)")
print("=" * 70)
