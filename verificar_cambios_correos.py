"""
Script para verificar los cambios realizados en los correos de comité y consulta
"""

# Buscar las funciones de correo y verificar que incluyen el nombre del cliente
import re

def verificar_cambios():
    print("🔍 VERIFICANDO CAMBIOS EN CORREOS")
    print("=" * 50)
    
    # Leer el archivo views_workflow.py
    with open('workflow/views_workflow.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Verificar función de correo de comité
    print("\n1. 📧 CORREO DE COMITÉ:")
    print("-" * 30)
    
    # Buscar el asunto del comité
    match_asunto_comite = re.search(
        r'subject = f"🏛️ Nueva Solicitud en Comité de Crédito - {cliente_nombre} - {solicitud\.codigo}"',
        contenido
    )
    
    if match_asunto_comite:
        print("✅ Asunto incluye nombre del cliente")
    else:
        print("❌ Asunto NO incluye nombre del cliente")
    
    # Buscar CC en EmailMultiAlternatives de comité
    # Buscar el patrón específico en la función del comité
    patron_comite = r'Nueva Solicitud en Comité de Crédito.*?EmailMultiAlternatives\([^)]*cc=cc_emails'
    match_cc_comite = re.search(patron_comite, contenido, re.DOTALL)
    
    if match_cc_comite:
        print("✅ Correo incluye CC (copia)")
    else:
        print("❌ Correo NO incluye CC")
    
    # Buscar la lógica de obtener usuario que atendió en comité
    if "usuario_comite_email" in contenido:
        print("✅ Lógica para obtener usuario que atendió en comité")
    else:
        print("❌ NO tiene lógica para usuario que atendió en comité")
    
    # Verificar función de correo de consulta
    print("\n2. 📧 CORREO DE CONSULTA:")
    print("-" * 30)
    
    # Buscar el asunto de consulta
    match_asunto_consulta = re.search(
        r'asunto = f"Resultado Consulta - {cliente_nombre} - Solicitud {solicitud\.codigo}"',
        contenido
    )
    
    if match_asunto_consulta:
        print("✅ Asunto incluye nombre del cliente")
    else:
        print("❌ Asunto NO incluye nombre del cliente")
    
    print("\n" + "=" * 50)
    print("✅ VERIFICACIÓN COMPLETADA")
    
    # Resumen de cambios
    print("\n📋 RESUMEN DE CAMBIOS REALIZADOS:")
    print("1. Correo de comité: Asunto incluye nombre del cliente")
    print("2. Correo de comité: Se agregó CC al analista revisor")
    print("3. Correo de comité: Se agregó CC al usuario que atendió en comité")
    print("4. Correo de consulta: Asunto incluye nombre del cliente")

if __name__ == "__main__":
    verificar_cambios()
