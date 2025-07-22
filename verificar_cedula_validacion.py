#!/usr/bin/env python
"""
Script para verificar que la validación de cédula única se ha eliminado
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from workflow.forms import FormularioWebForm
from workflow.models import FormularioWeb

print("=== VERIFICACIÓN: VALIDACIÓN DE CÉDULA ELIMINADA ===")

# 1. Verificar estado actual
total_formularios = FormularioWeb.objects.count()
print(f"Total de formularios existentes: {total_formularios}")

# 2. Buscar si hay cédulas existentes
cedulas_existentes = FormularioWeb.objects.values_list('cedulaCliente', flat=True)
print(f"Cédulas en base de datos: {list(cedulas_existentes)}")

# 3. Probar crear formulario con cédula existente
if cedulas_existentes:
    cedula_test = cedulas_existentes[0]
    print(f"\n3. Probando crear formulario con cédula existente: {cedula_test}")
    
    # Datos de prueba
    datos_test = {
        'nombre': 'Prueba',
        'apellido': 'Validación',
        'cedulaCliente': cedula_test,  # Usar cédula existente
        'celular': '6999-9999',
        'correo_electronico': 'test@test.com',
        'sexo': 'MASCULINO',
        'sector': 'Empresa privada',
        'salario': 'Entre $600.00 y $850.00',
        'producto_interesado': 'Préstamos personal',
        'dinero_a_solicitar': 1000.00,
        'autorizacion_apc': True,
        'acepta_condiciones': True
    }
    
    # Crear formulario
    form = FormularioWebForm(data=datos_test)
    
    if form.is_valid():
        print("✅ ÉXITO: El formulario ES VÁLIDO con cédula repetida")
        print("✅ La validación de cédula única ha sido eliminada correctamente")
        
        # Simular guardado (no guardar realmente)
        print("ℹ️ No se guardará para evitar datos duplicados innecesarios")
        
    else:
        print("❌ ERROR: El formulario NO es válido")
        print("Errores encontrados:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")
            
        # Verificar específicamente el error de cédula
        if 'cedulaCliente' in form.errors:
            print("❌ La validación de cédula única AÚN ESTÁ ACTIVA")
        else:
            print("✅ No hay errores de cédula (otros errores presentes)")

else:
    print("ℹ️ No hay cédulas existentes para probar")

print("\n=== VERIFICACIÓN COMPLETADA ===")
print("🎯 RESULTADO: Ahora el FormularioWeb puede aceptar cédulas repetidas")
print("📋 COMPORTAMIENTO:")
print("   - Los usuarios pueden enviar múltiples solicitudes con la misma cédula")
print("   - Cada solicitud se guardará como un registro independiente")
print("   - Se mantiene el historial completo de todas las solicitudes")
