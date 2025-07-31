#!/bin/bash

# Script para verificar el estado del modal de requisitos

echo "🔍 Verificando modal de requisitos..."

# 1. Verificar que el modal existe en el template
echo "1. Verificando estructura del modal..."
if grep -q "modalRequisitosFaltantes" workflow/templates/workflow/partials/modalRequisitos.html; then
    echo "✅ Modal existe en modalRequisitos.html"
else
    echo "❌ Modal no encontrado en modalRequisitos.html"
fi

# 2. Verificar que el modal se incluye en negocios.html
echo "2. Verificando inclusión del modal..."
if grep -q "modalRequisitos.html" workflow/templates/workflow/negocios.html; then
    echo "✅ Modal incluido en negocios.html"
else
    echo "❌ Modal no incluido en negocios.html"
fi

# 3. Verificar funciones JavaScript
echo "3. Verificando funciones JavaScript..."
if grep -q "mostrarModalRequisitosFaltantes" workflow/templates/workflow/negocios.html; then
    echo "✅ Función mostrarModalRequisitosFaltantes encontrada"
else
    echo "❌ Función mostrarModalRequisitosFaltantes no encontrada"
fi

# 4. Verificar API endpoint
echo "4. Verificando API endpoint..."
if grep -q "requisitos-faltantes-detallado" workflow/urls_workflow.py; then
    echo "✅ API endpoint existe"
else
    echo "❌ API endpoint no encontrado"
fi

# 5. Verificar vista de API
echo "5. Verificando vista de API..."
if grep -q "api_obtener_requisitos_faltantes_detallado" workflow/views_workflow.py; then
    echo "✅ Vista de API existe"
else
    echo "❌ Vista de API no encontrada"
fi

echo ""
echo "🎯 Problemas potenciales a revisar:"
echo "- ¿Está Bootstrap cargado correctamente?"
echo "- ¿Se está llamando la función en el momento correcto?"
echo "- ¿Hay errores en la consola del navegador?"
echo "- ¿El endpoint API está respondiendo correctamente?"
echo ""
echo "💡 Para debuggear:"
echo "1. Abre las herramientas de desarrollador"
echo "2. Ve a la pestaña Console"
echo "3. Ejecuta: testModalRequisitos()"
echo "4. Revisa los logs de la función mostrarModalRequisitosFaltantes"
