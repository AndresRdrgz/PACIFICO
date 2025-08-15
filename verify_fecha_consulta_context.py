#!/usr/bin/env python
"""
Script para verificar que todas las funciones PDF incluyen fecha_consulta 
correctamente en el contexto del template
"""

import os
import sys
import re

# Agregar el directorio del proyecto al path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def check_pdf_functions_context():
    """
    Verifica que las 3 funciones PDF incluyan fecha_consulta en su contexto
    """
    print("=== Verificación de Contexto PDF Functions ===")
    
    views_file = "/Users/andresrdrgz_/Documents/GitHub/PACIFICO/workflow/views_workflow.py"
    
    # Funciones que deben tener fecha_consulta
    functions_to_check = [
        'enviar_correo_pdf_resultado_consulta',
        'api_pdf_resultado_consulta', 
        'api_pdf_resultado_comite'
    ]
    
    try:
        with open(views_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = {}
        
        for func_name in functions_to_check:
            print(f"\n--- Verificando {func_name} ---")
            
            # Buscar la función
            func_pattern = rf'def {func_name}\([^)]*\):'
            func_match = re.search(func_pattern, content)
            
            if not func_match:
                print(f"  ❌ Función {func_name} no encontrada")
                results[func_name] = False
                continue
                
            func_start = func_match.start()
            
            # Encontrar el final de la función (siguiente def o final del archivo)
            next_def_pattern = r'\ndef [a-zA-Z_][a-zA-Z0-9_]*\('
            next_match = re.search(next_def_pattern, content[func_start + 100:])
            
            if next_match:
                func_end = func_start + 100 + next_match.start()
            else:
                func_end = len(content)
                
            func_content = content[func_start:func_end]
            
            # Verificar que tiene la lógica de fecha_consulta
            has_fecha_consulta_logic = 'fecha_consulta = solicitud.fecha_creacion' in func_content
            has_historial_lookup = "Etapa.objects.filter(nombre__icontains='Consulta')" in func_content
            has_context_fecha_consulta = "'fecha_consulta': fecha_consulta" in func_content
            
            print(f"  ✓ Lógica fecha_consulta: {'✅' if has_fecha_consulta_logic else '❌'}")
            print(f"  ✓ Búsqueda historial: {'✅' if has_historial_lookup else '❌'}")
            print(f"  ✓ En contexto: {'✅' if has_context_fecha_consulta else '❌'}")
            
            all_checks = has_fecha_consulta_logic and has_historial_lookup and has_context_fecha_consulta
            results[func_name] = all_checks
            
            if all_checks:
                print(f"  ✅ {func_name} está correcta")
            else:
                print(f"  ❌ {func_name} necesita corrección")
        
        print("\n=== RESUMEN ===")
        all_good = True
        for func_name, is_good in results.items():
            status = "✅" if is_good else "❌"
            print(f"{status} {func_name}")
            if not is_good:
                all_good = False
                
        return all_good
        
    except Exception as e:
        print(f"Error leyendo archivo: {e}")
        return False

def check_template_usage():
    """
    Verifica que el template use correctamente fecha_consulta
    """
    print("\n=== Verificación de Template ===")
    
    template_file = "/Users/andresrdrgz_/Documents/GitHub/PACIFICO/workflow/templates/workflow/pdf_resultado_consulta_simple.html"
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Buscar uso de fecha_consulta en el template
        fecha_consulta_usage = 'fecha_consulta|date:' in content
        fecha_consulta_label = 'Fecha Consulta:' in content
        
        print(f"✓ Template usa fecha_consulta: {'✅' if fecha_consulta_usage else '❌'}")
        print(f"✓ Template tiene label 'Fecha Consulta': {'✅' if fecha_consulta_label else '❌'}")
        
        if fecha_consulta_usage:
            # Encontrar la línea exacta
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'fecha_consulta|date:' in line:
                    print(f"  Línea {i}: {line.strip()}")
        
        return fecha_consulta_usage and fecha_consulta_label
        
    except Exception as e:
        print(f"Error leyendo template: {e}")
        return False

if __name__ == "__main__":
    print("Verificando implementación de fecha_consulta en PDFs...")
    
    success = True
    
    # Test 1: Funciones PDF
    if not check_pdf_functions_context():
        success = False
    
    # Test 2: Template
    if not check_template_usage():
        success = False
    
    if success:
        print("\n🎉 ¡ÉXITO! Todas las verificaciones pasaron")
        print("\n✅ Las 3 funciones PDF incluyen fecha_consulta correctamente:")
        print("   - enviar_correo_pdf_resultado_consulta") 
        print("   - api_pdf_resultado_consulta")
        print("   - api_pdf_resultado_comite")
        print("\n✅ El template muestra la fecha correctamente")
        print("\n📅 La fecha mostrada será cuando la solicitud llegó a la etapa 'Consulta'")
        print("   (no la fecha de creación de la solicitud)")
    else:
        print("\n❌ Algunas verificaciones fallaron")
        print("Revisa los detalles arriba para corregir los problemas")
        
    print("\nPara probar en la aplicación:")
    print("1. Ir a una solicitud que esté en Resultado Consulta o posterior")
    print("2. Generar PDF desde 'Resultado Consulta' o 'Comité'")
    print("3. Verificar que 'Fecha Consulta' muestre la fecha correcta (no la de creación)")
