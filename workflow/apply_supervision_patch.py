#!/usr/bin/env python3
"""
Script para aplicar parches de supervisión de grupos de manera automática y segura
"""

import re
import os
import shutil
from datetime import datetime

def backup_file(file_path):
    """Crear backup del archivo antes de modificarlo"""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    return backup_path

def apply_supervision_patch():
    """Aplicar parche de supervisión de grupos"""
    
    file_path = "workflow/views_workflow.py"
    
    if not os.path.exists(file_path):
        print(f"❌ Archivo no encontrado: {file_path}")
        return False
    
    # Crear backup
    backup_path = backup_file(file_path)
    
    try:
        # Leer archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Patrón a buscar (primera función)
        old_pattern1 = r'(\s+# Filtrar por permisos de usuario\n\s+if not \(request\.user\.is_superuser or request\.user\.is_staff\):\n\s+# Usuarios regulares solo ven sus propias cotizaciones\n\s+cotizaciones = cotizaciones\.filter\(added_by=request\.user\))'
        
        # Nuevo contenido
        new_content = '''        # Filtrar por permisos de usuario
        if not (request.user.is_superuser or request.user.is_staff):
            # Usuarios regulares: ver sus propias cotizaciones + cotizaciones de grupos supervisados
            from django.db.models import Q
            
            # Cotizaciones propias
            cotizaciones_propias = cotizaciones.filter(added_by=request.user)
            
            # Verificar si es supervisor de grupo
            cotizaciones_supervisadas = Cotizacion.objects.none()
            try:
                from pacifico.utils_grupos import obtener_grupos_supervisados_por_usuario
                grupos_supervisados = obtener_grupos_supervisados_por_usuario(request.user)
                
                if grupos_supervisados.exists():
                    print(f"🔍 DEBUG: Usuario {request.user.username} es supervisor de {grupos_supervisados.count()} grupos")
                    
                    # Obtener usuarios supervisados
                    usuarios_supervisados = []
                    for grupo_profile in grupos_supervisados:
                        miembros = grupo_profile.group.user_set.all()
                        usuarios_supervisados.extend(miembros)
                    
                    print(f"🔍 DEBUG: Usuarios supervisados encontrados: {len(usuarios_supervisados)}")
                    
                    # Filtrar cotizaciones de usuarios supervisados
                    if usuarios_supervisados:
                        cotizaciones_supervisadas = cotizaciones.filter(
                            added_by__in=usuarios_supervisados
                        )
                        print(f"🔍 DEBUG: Cotizaciones supervisadas encontradas: {cotizaciones_supervisadas.count()}")
            except ImportError as e:
                print(f"⚠️ DEBUG: No se pudo importar utils_grupos: {e}")
                pass  # Si no existe el módulo, continuar sin supervisión
            
            # Combinar cotizaciones propias y supervisadas
            cotizaciones = cotizaciones_propias | cotizaciones_supervisadas
            print(f"🔍 DEBUG: Total cotizaciones (propias + supervisadas): {cotizaciones.count()}")'''
        
        # Aplicar primera corrección
        if re.search(old_pattern1, content):
            content = re.sub(old_pattern1, new_content, content)
            print("✅ Primera función corregida")
        else:
            print("⚠️ No se encontró la primera función para corregir")
        
        # Buscar y corregir segunda función (si existe)
        # Buscar por contexto más específico
        old_pattern2 = r'(\s+# Filtrar por permisos de usuario\n\s+if not \(request\.user\.is_superuser or request\.user\.is_staff\):\n\s+# Usuarios regulares solo ven sus propias cotizaciones\n\s+cotizaciones = cotizaciones\.filter\(added_by=request\.user\)\n\s+\n\s+# Ordenar y limitar resultados\n\s+cotizaciones = cotizaciones\.order_by\(\'-created_at\'\)\[:limit\]\n\s+\n\s+# Serializar resultados\n\s+resultados = \[\]\n\s+for cotizacion in cotizaciones:\n\s+resultado = \{)'
        
        if re.search(old_pattern2, content):
            # Aplicar segunda corrección
            content = re.sub(old_pattern2, new_content + '\n        \n        # Ordenar y limitar resultados\n        cotizaciones = cotizaciones.order_by(\'-created_at\')[:limit]\n        \n        # Serializar resultados\n        resultados = []\n        for cotizacion in cotizaciones:\n            resultado = {', content)
            print("✅ Segunda función corregida")
        else:
            print("⚠️ No se encontró la segunda función para corregir")
        
        # Guardar archivo modificado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Parche aplicado exitosamente")
        print(f"📁 Archivo original respaldado en: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error aplicando parche: {e}")
        # Restaurar backup en caso de error
        try:
            shutil.copy2(backup_path, file_path)
            print(f"🔄 Archivo restaurado desde backup: {backup_path}")
        except:
            print("❌ No se pudo restaurar el archivo")
        return False

if __name__ == "__main__":
    print("🔧 Aplicando parche de supervisión de grupos...")
    success = apply_supervision_patch()
    
    if success:
        print("\n🎉 PARCHE APLICADO EXITOSAMENTE")
        print("📋 Próximos pasos:")
        print("1. Reiniciar el servidor Django")
        print("2. Probar la funcionalidad de búsqueda de cotizaciones")
        print("3. Verificar logs de debug en la consola")
    else:
        print("\n❌ ERROR APLICANDO PARCHE")
        print("📋 Verificar:")
        print("1. Que el archivo workflow/views_workflow.py existe")
        print("2. Que tienes permisos de escritura")
        print("3. Que el archivo no esté abierto en otro programa")
