#!/usr/bin/env python
"""
Script para corregir la asignación de creada_por en Canal Digital
"""

def fix_creada_por_assignment():
    file_path = 'workflow/views_workflow.py'
    
    # Leer el archivo
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrón a buscar (código actual)
    old_pattern = """                        # Asignar propietario por defecto si está configurado
                        propietario_por_defecto = ConfiguracionCanalDigital.get_propietario_por_defecto()
                        if propietario_por_defecto:
                            solicitud.propietario = propietario_por_defecto
                            # También asignar al formulario para consistencia
                            formulario.propietario = propietario_por_defecto
                        else:
                            solicitud.propietario = None
                        solicitud.creada_por = usuario_sistema"""
    
    # Nuevo código con corrección
    new_pattern = """                        # Asignar propietario por defecto si está configurado
                        propietario_por_defecto = ConfiguracionCanalDigital.get_propietario_por_defecto()
                        if propietario_por_defecto:
                            solicitud.propietario = propietario_por_defecto
                            # Usar el propietario por defecto como creador para mantener consistencia
                            solicitud.creada_por = propietario_por_defecto
                            # También asignar al formulario para consistencia
                            formulario.propietario = propietario_por_defecto
                        else:
                            solicitud.propietario = None
                            # Si no hay propietario por defecto, usar usuario del sistema
                            solicitud.creada_por = usuario_sistema"""
    
    # Reemplazar todas las ocurrencias
    updated_content = content.replace(old_pattern, new_pattern)
    
    # Verificar si se hicieron cambios
    if updated_content != content:
        # Escribir el archivo actualizado
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        # Contar cuántos cambios se hicieron
        changes = content.count(old_pattern)
        print(f"✅ Se corrigió la asignación de 'creada_por' en {file_path}")
        print(f"📊 Se reemplazaron {changes} ocurrencias")
        print("🔧 Ahora 'creada_por' usará el propietario por defecto cuando esté configurado")
    else:
        print("❌ No se encontraron ocurrencias para reemplazar")
        print("🔍 Verificando si ya está actualizado...")
        
        # Verificar si ya tiene la corrección
        if "Usar el propietario por defecto como creador" in content:
            print("✅ El código ya está actualizado")
        else:
            print("❓ El patrón no coincide, puede que el código haya cambiado")

if __name__ == '__main__':
    fix_creada_por_assignment()
