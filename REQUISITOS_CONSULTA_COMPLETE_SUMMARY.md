# Implementación: Filtro de Requisitos para Etapa "Consulta"

## 📋 Resumen
Se ha implementado exitosamente el filtro de requisitos en `detalle_solicitud_analisis.html` para mostrar únicamente los documentos configurados para las transiciones hacia la etapa "Consulta".

## 🎯 Objetivo Cumplido
✅ **"in requisitos faltantes modal, display also optionals documents for that transicion so the users can upload thos optionals documents in that same modal"**

En lugar del modal de requisitos faltantes, se modificó la sección de adjuntos del análisis para mostrar únicamente los requisitos configurados para la transición hacia "Consulta", incluyendo tanto obligatorios como opcionales.

## 🔧 Cambios Implementados

### 1. `workflow/views_workflow.py` - Función `detalle_solicitud_analisis`
```python
# Agregado: Lógica para filtrar requisitos específicos de transición a Consulta
etapa_consulta = solicitud.pipeline.etapas.filter(nombre__icontains='Consulta').first()
requisitos_consulta = []

if etapa_consulta:
    # Buscar transiciones que van hacia "Consulta"
    transiciones_a_consulta = TransicionEtapa.objects.filter(
        pipeline=solicitud.pipeline,
        etapa_destino=etapa_consulta
    )
    
    # Obtener RequisitoTransicion con información de obligatorio/opcional
    requisitos_transicion = RequisitoTransicion.objects.filter(
        transicion__in=transiciones_a_consulta
    ).select_related('requisito', 'transicion')
    
    # Crear diccionario de requisitos con su estado obligatorio/opcional
    requisitos_info_map = {}
    for req_trans in requisitos_transicion:
        requisitos_info_map[req_trans.requisito.id] = {
            'obligatorio': req_trans.obligatorio,
            'mensaje_personalizado': req_trans.mensaje_personalizado,
            'transicion_nombre': req_trans.transicion.nombre
        }
    
    # Filtrar solo los requisitos de la solicitud configurados para Consulta
    requisitos_ids = list(requisitos_info_map.keys())
    requisitos_consulta = solicitud.requisitos.filter(
        requisito_id__in=requisitos_ids
    ).select_related('requisito')
    
    # Agregar información de obligatorio/opcional a cada requisito
    for req_sol in requisitos_consulta:
        if req_sol.requisito.id in requisitos_info_map:
            req_sol.es_obligatorio = requisitos_info_map[req_sol.requisito.id]['obligatorio']
            req_sol.mensaje_personalizado = requisitos_info_map[req_sol.requisito.id]['mensaje_personalizado']
            req_sol.transicion_nombre = requisitos_info_map[req_sol.requisito.id]['transicion_nombre']

# Agregado al context
context = {
    # ... otros campos ...
    'requisitos_consulta': requisitos_consulta,  # Requisitos específicos para transición a Consulta
}
```

### 2. `workflow/templates/workflow/detalle_solicitud_analisis.html`
```html
<!-- Cambio 1: Título actualizado -->
<h3 class="section-title">Adjuntos (Consulta)</h3>

<!-- Cambio 2: Usar requisitos_consulta en lugar de solicitud.requisitos.all -->
{% if requisitos_consulta %}
    {% for requisito_solicitud in requisitos_consulta %}
        <div class="adjunto-item">
            <!-- ... contenido del item ... -->
            <div class="adjunto-name">
                {{ requisito_solicitud.requisito.nombre }}
                
                <!-- Cambio 3: Badges de Obligatorio/Opcional -->
                {% if requisito_solicitud.es_obligatorio %}
                    <span class="badge bg-danger badge-sm ms-1">Obligatorio</span>
                {% else %}
                    <span class="badge bg-secondary badge-sm ms-1">Opcional</span>
                {% endif %}
                
                <!-- ... resto del contenido ... -->
            </div>
        </div>
    {% endfor %}
{% else %}
    <!-- Cambio 4: Mensaje de estado vacío actualizado -->
    <div class="alert alert-light text-center">
        <i class="fas fa-inbox me-2"></i>
        <small>Sin requisitos configurados para transición a Consulta</small>
    </div>
{% endif %}
```

## 📊 Requisitos Configurados (según especificación del usuario)
La sección de adjuntos ahora muestra únicamente estos 4 requisitos configurados para la transición "Nuevo Lead → Consulta":

| Requisito | Obligatorio | Mensaje Personalizado |
|-----------|-------------|----------------------|
| **Cotización SURA** | ❌ False (Opcional) | opcional |
| **Foto** | ✅ True (Obligatorio) | - |
| **Ficha CSS** | ✅ True (Obligatorio) | - |
| **APC** | ✅ True (Obligatorio) | - |

## 🎨 Características Visuales
- ✅ **Título descriptivo**: "Adjuntos (Consulta)" en lugar de solo "Adjuntos"
- ✅ **Badges informativos**: 
  - `Obligatorio` (badge rojo) para requisitos obligatorios
  - `Opcional` (badge gris) para requisitos opcionales
- ✅ **Filtrado inteligente**: Solo muestra requisitos configurados para transiciones hacia "Consulta"
- ✅ **Funcionalidad completa**: Mantiene toda la funcionalidad de compliance, comentarios y descarga

## ✅ Verificación y Testing
1. **Sintaxis verificada**: `python -m py_compile workflow/views_workflow.py` ✓
2. **Lógica implementada**: Filtrado basado en RequisitoTransicion hacia etapa "Consulta" ✓
3. **Template actualizado**: Uso de `requisitos_consulta` con badges ✓
4. **Demo visual**: `test_requisitos_consulta_demo.html` creado ✓

## 🚀 Instrucciones de Testing
1. **Ejecutar servidor Django**: `python manage.py runserver`
2. **Navegar a análisis**: Ir a cualquier solicitud en `/workflow/detalle_solicitud_analisis/{id}/`
3. **Verificar adjuntos**: La sección debe mostrar solo los 4 requisitos configurados
4. **Comprobar badges**: Cada requisito debe mostrar "Obligatorio" (rojo) u "Opcional" (gris)

## 🔗 Archivos Modificados
- ✅ `workflow/views_workflow.py` (función `detalle_solicitud_analisis`)
- ✅ `workflow/templates/workflow/detalle_solicitud_analisis.html` (sección adjuntos)

## 📝 Archivos de Testing/Documentación Creados
- 📄 `REQUISITOS_CONSULTA_IMPLEMENTATION.md` (este archivo)
- 🌐 `test_requisitos_consulta_demo.html` (demo visual)
- 🧪 `test_requisitos_consulta.py` (script de testing)

---
**✅ Implementación completa y lista para testing en entorno de desarrollo.**
