#!/usr/bin/env python3
"""
Script para reactivar automáticamente la funcionalidad de subsanado_por_oficial y pendiente_completado
después de ejecutar la migration 0042.

USO:
1. Ejecutar: python manage.py migrate workflow
2. Ejecutar: python reactivar_funcionalidad.py
"""

import os
import re

def reemplazar_en_archivo(archivo, patrones_reemplazo):
    """Reemplaza patrones en un archivo"""
    if not os.path.exists(archivo):
        print(f"❌ Archivo no encontrado: {archivo}")
        return False
    
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    contenido_modificado = contenido
    cambios_realizados = 0
    
    for patron, reemplazo in patrones_reemplazo:
        if patron in contenido_modificado:
            contenido_modificado = contenido_modificado.replace(patron, reemplazo)
            cambios_realizados += 1
    
    if cambios_realizados > 0:
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido_modificado)
        print(f"✅ {archivo}: {cambios_realizados} cambio(s) aplicado(s)")
        return True
    else:
        print(f"⚠️  {archivo}: No se encontraron patrones para cambiar")
        return False

def main():
    print("🚀 REACTIVANDO FUNCIONALIDAD COMPLETA DE SUBSANADO/PENDIENTE...")
    print("=" * 60)
    
    # Verificar si estamos en el directorio correcto
    if not os.path.exists('workflow/models.py'):
        print("❌ Error: Ejecutar desde el directorio raíz del proyecto Django")
        return
    
    cambios_exitosos = 0
    
    # 0. workflow/models.py - PRIMERO Y MÁS IMPORTANTE
    print("\n0️⃣  Reactivando campos en models.py (CRITICO)...")
    patrones_modelo = [
        (
            "    # NUEVOS CAMPOS TEMPORALMENTE COMENTADOS HASTA EJECUTAR MIGRATION\n"
            "    # subsanado_por_oficial = models.BooleanField(\n"
            "    #     default=False,\n"
            "    #     verbose_name=\"Subsanado por Oficial\",\n"
            "    #     help_text=\"Indica si la oficial ya subió/reemplazó el documento para subsanar el problema\"\n"
            "    # )\n"
            "    # pendiente_completado = models.BooleanField(\n"
            "    #     default=False,\n"
            "    #     verbose_name=\"Pendiente Completado\",\n"
            "    #     help_text=\"Indica si la oficial ya subió archivo para un documento que estaba pendiente\"\n"
            "    # )",
            
            "    # NUEVOS CAMPOS PARA MEJORA DE FLUJO OFICIAL-BACKOFFICE\n"
            "    subsanado_por_oficial = models.BooleanField(\n"
            "        default=False,\n"
            "        verbose_name=\"Subsanado por Oficial\",\n"
            "        help_text=\"Indica si la oficial ya subió/reemplazó el documento para subsanar el problema\"\n"
            "    )\n"
            "    pendiente_completado = models.BooleanField(\n"
            "        default=False,\n"
            "        verbose_name=\"Pendiente Completado\",\n"
            "        help_text=\"Indica si la oficial ya subió archivo para un documento que estaba pendiente\"\n"
            "    )"
        )
    ]
    if reemplazar_en_archivo('workflow/models.py', patrones_modelo):
        cambios_exitosos += 1
        print("✨ IMPORTANTE: Los campos del modelo están ahora activos")
    else:
        print("⚠️ WARNING: No se pudieron activar los campos del modelo - hazlo manualmente")
    
    # 1. workflow/views_workflow.py
    print("\n1️⃣  Reactivando views_workflow.py...")
    patrones_views = [
        (
            "                # NUEVOS CAMPOS TEMPORALMENTE COMENTADOS HASTA EJECUTAR MIGRATION\n"
            "                # 'subsanado_por_oficial': calificacion.subsanado_por_oficial if calificacion else False,\n"
            "                # 'pendiente_completado': calificacion.pendiente_completado if calificacion else False,\n"
            "                'subsanado_por_oficial': False,  # Temporal - hasta migration\n"
            "                'pendiente_completado': False,   # Temporal - hasta migration",
            
            "                # NUEVOS CAMPOS PARA FLUJO OFICIAL-BACKOFFICE\n"
            "                'subsanado_por_oficial': calificacion.subsanado_por_oficial if calificacion else False,\n"
            "                'pendiente_completado': calificacion.pendiente_completado if calificacion else False,"
        )
    ]
    if reemplazar_en_archivo('workflow/views_workflow.py', patrones_views):
        cambios_exitosos += 1
    
    # 2. workflow/views_calificacion.py
    print("\n2️⃣  Reactivando views_calificacion.py...")
    patrones_calificacion = [
        (
            "                'fecha': calificacion.fecha_calificacion.strftime('%d/%m/%Y %H:%M')\n"
            "                # NUEVOS CAMPOS temporalmente comentados hasta migration\n"
            "                # 'subsanado_por_oficial': calificacion.subsanado_por_oficial,\n"
            "                # 'pendiente_completado': calificacion.pendiente_completado",
            
            "                'fecha': calificacion.fecha_calificacion.strftime('%d/%m/%Y %H:%M'),\n"
            "                # NUEVOS CAMPOS para feedback en UI\n"
            "                'subsanado_por_oficial': calificacion.subsanado_por_oficial,\n"
            "                'pendiente_completado': calificacion.pendiente_completado"
        )
    ]
    if reemplazar_en_archivo('workflow/views_calificacion.py', patrones_calificacion):
        cambios_exitosos += 1
    
    # 3. Reactivar signals_backoffice.py (patrones más complejos)
    print("\n3️⃣  Reactivando signals_backoffice.py...")
    if os.path.exists('workflow/signals_backoffice.py'):
        with open('workflow/signals_backoffice.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Reemplazar lógica comentada
        contenido = contenido.replace(
            "    # NUEVO: Manejar reseteo de campos - TEMPORALMENTE COMENTADO HASTA MIGRATION",
            "    # NUEVO: Manejar reseteo de campos cuando backoffice califica"
        )
        
        # Descomentar if created
        contenido = re.sub(
            r'    # if created:.*?print\(f"🔄 Signal de reseteo de campos temporalmente deshabilitado.*?\n',
            '    if created:  # Nueva calificación creada por backoffice\n'
            '        try:\n'
            '            # Si es una nueva calificación "malo", resetear subsanado_por_oficial en TODAS las calificaciones del mismo documento\n'
            '            if instance.estado == \'malo\':\n'
            '                CalificacionDocumentoBackoffice.objects.filter(\n'
            '                    requisito_solicitud=instance.requisito_solicitud\n'
            '                ).update(\n'
            '                    subsanado_por_oficial=False\n'
            '                )\n'
            '                print(f"🔄 Reseteado subsanado_por_oficial para documento: {instance.requisito_solicitud.requisito.nombre}")\n'
            '            \n'
            '            # Si es una nueva calificación "pendiente", resetear pendiente_completado (opcional)\n'
            '            elif instance.estado == \'pendiente\':\n'
            '                CalificacionDocumentoBackoffice.objects.filter(\n'
            '                    requisito_solicitud=instance.requisito_solicitud\n'
            '                ).update(\n'
            '                    pendiente_completado=False\n'
            '                )\n'
            '                print(f"🔄 Reseteado pendiente_completado para documento: {instance.requisito_solicitud.requisito.nombre}")\n'
            '                \n'
            '        except Exception as e:\n'
            '            print(f"Error reseteando campos automáticos: {e}")\n',
            contenido,
            flags=re.DOTALL
        )
        
        with open('workflow/signals_backoffice.py', 'w', encoding='utf-8') as f:
            f.write(contenido)
        print("✅ workflow/signals_backoffice.py: Reactivado")
        cambios_exitosos += 1
    
    # 4. admin.py - reactivar campos en Django Admin
    print("\n4️⃣  Reactivando admin.py (Django Admin)...")
    patrones_admin = [
        (
            "        # 'subsanado_por_oficial', 'pendiente_completado'  # Activar después de migration",
            "        'subsanado_por_oficial', 'pendiente_completado'"
        ),
        (
            "        # 'subsanado_por_oficial', 'pendiente_completado'  # Activar después de migration",
            "        'subsanado_por_oficial', 'pendiente_completado'"
        ),
        (
            "        # ('Flujo Oficial-Backoffice', {  # Activar después de migration\n"
            "        #     'fields': ('subsanado_por_oficial', 'pendiente_completado'),\n"
            "        #     'classes': ('collapse',)\n"
            "        # }),",
            "        ('Flujo Oficial-Backoffice', {\n"
            "            'fields': ('subsanado_por_oficial', 'pendiente_completado'),\n"
            "            'classes': ('collapse',)\n"
            "        }),"
        )
    ]
    if reemplazar_en_archivo('workflow/admin.py', patrones_admin):
        cambios_exitosos += 1
        print("✨ Campos nuevos ahora visibles en Django Admin")
    else:
        print("⚠️ WARNING: No se pudieron activar campos en admin - hazlo manualmente")
    
    # 5. api_upload.py - lógica más compleja, mejor manual por ahora
    print("\n5️⃣  workflow/api_upload.py: ⚠️  REACTIVAR MANUALMENTE")
    print("    Descomentar secciones marcadas como 'TEMPORALMENTE COMENTADO HASTA MIGRATION'")
    
    # 6. UI Template - badges
    print("\n6️⃣  workflow/templates/workflow/partials/modalSolicitud.html: ⚠️  REACTIVAR MANUALMENTE")
    print("    Descomentar lógica de badges en ambas funciones JS")
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN: {cambios_exitosos}/5 archivos reactivados automáticamente")
    print("\n✅ MODELO: Los campos subsanado_por_oficial y pendiente_completado están en el modelo")
    print("✅ DJANGO ADMIN: Los campos nuevos estarán visibles en la interfaz de administración")
    print("\n⚠️  COMPLETAR MANUALMENTE:")
    print("   - workflow/api_upload.py")
    print("   - workflow/templates/workflow/partials/modalSolicitud.html")
    print("\n✅ Después de completar, el sistema tendrá funcionalidad completa!")
    print("\n🔍 VERIFICAR EN DJANGO ADMIN:")
    print("   - Ve a /admin/workflow/calificaciondocumentobackoffice/")
    print("   - Deberías ver columnas: 'Subsanado por Oficial' y 'Pendiente Completado'")
    print("   - Y nuevos filtros laterales para estos campos")

if __name__ == "__main__":
    main()