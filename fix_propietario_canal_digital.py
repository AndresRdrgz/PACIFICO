#!/usr/bin/env python
"""
Script para actualizar la lógica de asignación de propietarios en Canal Digital
"""

def fix_propietario_assignment():
    file_path = 'workflow/views_workflow.py'
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Texto a buscar y reemplazar
    old_text = """        # NO asignar propietario - las solicitudes del Canal Digital llegan sin propietario
        solicitud.propietario = None"""
    
    new_text = """        # Asignar propietario por defecto si está configurado
        propietario_por_defecto = ConfiguracionCanalDigital.get_propietario_por_defecto()
        if propietario_por_defecto:
            solicitud.propietario = propietario_por_defecto
            # También asignar al formulario para consistencia
            formulario.propietario = propietario_por_defecto
        else:
            solicitud.propietario = None"""
    
    # Reemplazar todas las ocurrencias
    updated_content = content.replace(old_text, new_text)
    
    # Verificar si se hicieron cambios
    if updated_content != content:
        # Escribir el archivo actualizado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✅ Se actualizaron las asignaciones de propietario en {file_path}")
        
        # Contar cuántos cambios se hicieron
        changes = content.count(old_text)
        print(f"📊 Se reemplazaron {changes} ocurrencias")
    else:
        print("❌ No se encontraron ocurrencias para reemplazar")

if __name__ == '__main__':
    fix_propietario_assignment()
