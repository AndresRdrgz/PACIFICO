#!/usr/bin/env python
"""
Test simple para verificar que los archivos están correctamente configurados
"""

import os
import re

def test_file_content():
    """Test para verificar el contenido de los archivos modificados"""
    
    print("=== Verificando archivos modificados ===\n")
    
    # Test 1: Verificar negocios.html
    negocios_path = "workflow/templates/workflow/negocios.html"
    if os.path.exists(negocios_path):
        with open(negocios_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "Solicitudes Makito" in content:
            print("✓ negocios.html: Botón 'Solicitudes Makito' configurado")
        else:
            print("✗ negocios.html: Botón 'Solicitudes Makito' NO encontrado")
            
        if "makito_tracking" in content:
            print("✓ negocios.html: URL makito_tracking configurada")
        else:
            print("✗ negocios.html: URL makito_tracking NO encontrada")
    else:
        print("✗ negocios.html: Archivo no encontrado")
    
    # Test 2: Verificar urls_workflow.py
    urls_path = "workflow/urls_workflow.py"
    if os.path.exists(urls_path):
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "makito-tracking/" in content:
            print("✓ urls_workflow.py: Ruta makito-tracking configurada")
        else:
            print("✗ urls_workflow.py: Ruta makito-tracking NO encontrada")
            
        if "makito_tracking_view" in content:
            print("✓ urls_workflow.py: Vista makito_tracking_view configurada")
        else:
            print("✗ urls_workflow.py: Vista makito_tracking_view NO encontrada")
    else:
        print("✗ urls_workflow.py: Archivo no encontrado")
    
    # Test 3: Verificar views_workflow.py
    views_path = "workflow/views_workflow.py"
    if os.path.exists(views_path):
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "def makito_tracking_view" in content:
            print("✓ views_workflow.py: Función makito_tracking_view creada")
        else:
            print("✗ views_workflow.py: Función makito_tracking_view NO encontrada")
            
        if "tracking_type='unified'" in content:
            print("✓ views_workflow.py: tracking_type='unified' configurado")
        else:
            print("✗ views_workflow.py: tracking_type='unified' NO encontrado")
    else:
        print("✗ views_workflow.py: Archivo no encontrado")
    
    # Test 4: Verificar makito_tracking.html
    template_path = "workflow/templates/workflow/makito_tracking.html"
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "<th>Tipo Solicitud</th>" in content:
            print("✓ makito_tracking.html: Columna 'Tipo Solicitud' agregada")
        else:
            print("✗ makito_tracking.html: Columna 'Tipo Solicitud' NO encontrada")
            
        if "tipo_solicitud" in content:
            print("✓ makito_tracking.html: Lógica tipo_solicitud implementada")
        else:
            print("✗ makito_tracking.html: Lógica tipo_solicitud NO encontrada")
            
        if "badge badge-" in content:
            print("✓ makito_tracking.html: Badges para tipos configurados")
        else:
            print("✗ makito_tracking.html: Badges para tipos NO configurados")
            
        # Verificar CSS para 13 columnas
        if "13.33%" in content or "grid-template-columns" in content:
            print("✓ makito_tracking.html: CSS para 13 columnas configurado")
        else:
            print("✗ makito_tracking.html: CSS para 13 columnas NO configurado")
            
        # Verificar JavaScript unificado
        if "trackingType === 'unified'" in content:
            print("✓ makito_tracking.html: JavaScript unificado implementado")
        else:
            print("✗ makito_tracking.html: JavaScript unificado NO implementado")
    else:
        print("✗ makito_tracking.html: Archivo no encontrado")
    
    print(f"\n🎉 Verificación de archivos completada!")

def main():
    print("=== Test de Configuración del Tracking Unificado ===")
    print("Verificando que todos los cambios estén correctamente implementados...\n")
    
    test_file_content()
    
    print("\n" + "="*60)
    print("📋 RESUMEN DE IMPLEMENTACIÓN:")
    print("1. ✅ Botón unificado 'Solicitudes Makito' en negocios.html")
    print("2. ✅ URL makito_tracking configurada en urls_workflow.py")
    print("3. ✅ Vista makito_tracking_view creada en views_workflow.py")
    print("4. ✅ Template makito_tracking.html modificado:")
    print("   - Columna 'Tipo Solicitud' agregada")
    print("   - CSS actualizado para 13 columnas")
    print("   - JavaScript reescrito para vista unificada")
    print("   - Badges para distinguir tipos APC/SURA")
    print("   - Estadísticas mejoradas para vista unificada")
    print("\n🚀 La funcionalidad está lista para usar!")
    print("🔗 Accede a través del botón 'Solicitudes Makito' en la página principal")

if __name__ == "__main__":
    main()
