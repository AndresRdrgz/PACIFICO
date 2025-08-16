#!/usr/bin/env python
"""
Script para actualizar las líneas restantes de asignación de propietarios
"""

def fix_remaining_propietario_assignments():
    file_path = 'workflow/views_workflow.py'
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar y reemplazar las líneas que quedan pendientes
    old_patterns = [
        "                    # NO asignar propietario - las solicitudes del Canal Digital llegan sin propietario\n                    solicitud.propietario = None",
        "                        # NO asignar propietario - las solicitudes del Canal Digital llegan sin propietario\n                        solicitud.propietario = None"
    ]
    
    new_patterns = [
        """                    # Asignar propietario por defecto si está configurado
                    propietario_por_defecto = ConfiguracionCanalDigital.get_propietario_por_defecto()
                    if propietario_por_defecto:
                        solicitud.propietario = propietario_por_defecto
                        # También asignar al formulario para consistencia
                        formulario.propietario = propietario_por_defecto
                    else:
                        solicitud.propietario = None""",
        """                        # Asignar propietario por defecto si está configurado
                        propietario_por_defecto = ConfiguracionCanalDigital.get_propietario_por_defecto()
                        if propietario_por_defecto:
                            solicitud.propietario = propietario_por_defecto
                            # También asignar al formulario para consistencia
                            formulario.propietario = propietario_por_defecto
                        else:
                            solicitud.propietario = None"""
    ]
    
    updated_content = content
    total_changes = 0
    
    for old_pattern, new_pattern in zip(old_patterns, new_patterns):
        old_count = updated_content.count(old_pattern)
        updated_content = updated_content.replace(old_pattern, new_pattern)
        new_count = updated_content.count(old_pattern)
        changes = old_count - new_count
        total_changes += changes
        if changes > 0:
            print(f"✅ Reemplazadas {changes} ocurrencias del patrón")
    
    # Verificar si se hicieron cambios
    if updated_content != content:
        # Escribir el archivo actualizado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✅ Se actualizaron {total_changes} asignaciones adicionales de propietario en {file_path}")
    else:
        print("❌ No se encontraron más ocurrencias para reemplazar")

if __name__ == '__main__':
    fix_remaining_propietario_assignments()
