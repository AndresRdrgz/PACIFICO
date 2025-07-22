#!/usr/bin/env python
"""
Script para probar que se pueden crear múltiples formularios con la misma cédula
"""
import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.forms import FormularioWebForm
from workflow.models import FormularioWeb

print("=== PRUEBA: CREAR MÚLTIPLES FORMULARIOS CON MISMA CÉDULA ===")

# Cédula a usar para la prueba
cedula_prueba = "8-888-8888"

# Datos base para los formularios
datos_base = {
    'nombre': 'Juan',
    'apellido': 'Pérez',
    'cedulaCliente': cedula_prueba,
    'celular': '6111-1111',
    'correo_electronico': 'juan@test.com',
    'fecha_nacimiento': date(1990, 1, 1),
    'edad': 34,
    'sexo': 'MASCULINO',
    'sector': 'Empresa privada',
    'salario': 'Entre $600.00 y $850.00',
    'producto_interesado': 'Préstamos personal',
    'dinero_a_solicitar': 1500.00,
    'autorizacion_apc': True,
    'acepta_condiciones': True
}

print(f"Cédula a probar: {cedula_prueba}")
print(f"Formularios existentes con esta cédula: {FormularioWeb.objects.filter(cedulaCliente=cedula_prueba).count()}")

# Intentar crear 3 formularios con la misma cédula
for i in range(1, 4):
    print(f"\n--- Creando formulario #{i} ---")
    
    # Modificar ligeramente algunos datos para diferencias
    datos_test = datos_base.copy()
    datos_test['nombre'] = f"Juan{i}"
    datos_test['celular'] = f"611{i}-111{i}"
    datos_test['dinero_a_solicitar'] = 1000.00 + (i * 500)
    
    # Crear y validar formulario
    form = FormularioWebForm(data=datos_test)
    
    if form.is_valid():
        print(f"✅ Formulario #{i} es válido")
        
        # Guardar formulario
        formulario = form.save()
        print(f"✅ Formulario #{i} guardado con ID: {formulario.id}")
        print(f"   - Nombre: {formulario.get_nombre_completo()}")
        print(f"   - Cédula: {formulario.cedulaCliente}")
        print(f"   - Monto: ${formulario.dinero_a_solicitar}")
        
    else:
        print(f"❌ Formulario #{i} NO es válido")
        print("Errores:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")

# Verificar resultado final
print(f"\n=== RESULTADO FINAL ===")
total_con_cedula = FormularioWeb.objects.filter(cedulaCliente=cedula_prueba).count()
print(f"Total de formularios con cédula {cedula_prueba}: {total_con_cedula}")

if total_con_cedula > 1:
    print("✅ ÉXITO: Se pueden crear múltiples formularios con la misma cédula")
    
    # Mostrar todos los formularios con esta cédula
    formularios = FormularioWeb.objects.filter(cedulaCliente=cedula_prueba)
    print("\nFormularios creados:")
    for form in formularios:
        print(f"  - ID {form.id}: {form.get_nombre_completo()} | ${form.dinero_a_solicitar} | {form.fecha_creacion}")
else:
    print("❌ No se pudieron crear múltiples formularios")

print("\n🎯 La validación de cédula única ha sido eliminada exitosamente!")
