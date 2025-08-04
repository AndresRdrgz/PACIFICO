# Modal de Requisitos con Documentos Opcionales - Implementación Completa

## Resumen de Cambios

Se ha implementado exitosamente la funcionalidad para mostrar y manejar documentos opcionales en el modal de requisitos faltantes, además de los obligatorios.

## Cambios Realizados

### 1. Backend (Django) - `views_workflow.py`

#### API `api_obtener_requisitos_faltantes_detallado`
- **Antes**: Solo obtenía requisitos obligatorios (`obligatorio=True`)
- **Después**: Obtiene TODOS los requisitos (obligatorios y opcionales)

```python
# ANTES
requisitos_transicion = RequisitoTransicion.objects.filter(
    transicion=transicion,
    obligatorio=True
).select_related('requisito')

# DESPUÉS
requisitos_transicion = RequisitoTransicion.objects.filter(
    transicion=transicion
).select_related('requisito')
```

#### Respuesta JSON Enriquecida
Se agregaron nuevos campos a la respuesta JSON:

```python
{
    'requisitos': requisitos_detallados,           # Todos los requisitos
    'requisitos_obligatorios': requisitos_obligatorios,    # Solo obligatorios
    'requisitos_opcionales': requisitos_opcionales,        # Solo opcionales
    'total_requisitos_obligatorios': total_requisitos_obligatorios,
    'total_requisitos_opcionales': len(requisitos_opcionales),
    'requisitos_obligatorios_completos': requisitos_obligatorios_completos,
    'requisitos_obligatorios_faltantes': requisitos_obligatorios_faltantes,
    'total_obligatorios_faltantes': total_obligatorios_faltantes,
    # ... otros campos existentes
}
```

#### Campo `obligatorio` en Requisitos
Cada requisito ahora incluye el campo `obligatorio`:

```python
requisito_data = {
    'id': req_transicion.requisito.id,
    'nombre': req_transicion.requisito.nombre,
    'descripcion': req_transicion.requisito.descripcion,
    'mensaje_personalizado': req_transicion.mensaje_personalizado,
    'obligatorio': req_transicion.obligatorio,  # ← NUEVO CAMPO
    # ... otros campos
}
```

### 2. Frontend - Modal HTML (`modalRequisitos.html`)

#### Mensaje Informativo Actualizado
```html
<!-- ANTES -->
<p>Antes de continuar a la siguiente etapa, debes completar los siguientes requisitos obligatorios:</p>

<!-- DESPUÉS -->
<p>Antes de continuar a la siguiente etapa, debes completar los requisitos obligatorios. También puedes subir documentos opcionales que faciliten el proceso.</p>
```

#### Nuevos Estilos CSS
```css
.requisito-item.opcional {
    border-color: #6c757d;
    background: linear-gradient(135deg, rgba(108, 117, 125, 0.05), rgba(173, 181, 189, 0.1));
}

.seccion-titulo.opcional {
    border-left-color: #6c757d;
}

.badge-opcional {
    background: linear-gradient(135deg, #6c757d, #adb5bd);
}
```

### 3. Frontend - JavaScript (`negocios.html`)

#### Función `llenarListaRequisitosFaltantes` Rediseñada
- **Antes**: Mostraba una lista simple de requisitos
- **Después**: Muestra secciones separadas para obligatorios y opcionales

```javascript
// Nuevas secciones diferenciadas
if (requisitosObligatorios.length > 0) {
    // Sección de Requisitos Obligatorios
    const seccionObligatoriosHtml = `
        <div class="seccion-requisitos">
            <div class="seccion-titulo obligatorio">
                <h6>Requisitos Obligatorios</h6>
                <span class="badge badge-obligatorio">${completos}/${total}</span>
            </div>
            ...
        </div>
    `;
}

if (requisitosOpcionales.length > 0) {
    // Sección de Requisitos Opcionales
    const seccionOpcionalesHtml = `
        <div class="seccion-requisitos">
            <div class="seccion-titulo opcional">
                <h6>Requisitos Opcionales</h6>
                <span class="badge badge-opcional">${completos}/${total}</span>
            </div>
            ...
        </div>
    `;
}
```

#### Función `buildRequisitoHtml` Creada
Nueva función auxiliar que genera HTML diferenciado:

```javascript
function buildRequisitoHtml(requisito, esObligatorio) {
    const badgeText = isCompleto ? 'Completo' : (esObligatorio ? 'Faltante' : 'Opcional');
    const marcador = esObligatorio ? '<span class="text-danger">*</span>' : '<span class="text-secondary">(opcional)</span>';
    // ...
}
```

#### Validación Solo de Requisitos Obligatorios
La función `verificarTodosRequisitosCompletos` ahora solo valida requisitos obligatorios:

```javascript
// ANTES: Validaba todos los requisitos
const totalRequisitos = requisitosData.total_requisitos;
const requisitosCompletos = requisitosData.requisitos_completos;

// DESPUÉS: Solo valida obligatorios
const totalRequisitosObligatorios = requisitosData.total_requisitos_obligatorios || 0;
const requisitosObligatoriosCompletos = requisitosData.requisitos_obligatorios_completos || 0;
const totalObligatoriosFaltantes = requisitosData.total_obligatorios_faltantes || 0;
```

#### Estados del Botón "Validar y Continuar"
```javascript
// Todos los obligatorios completos
if (totalObligatoriosFaltantes === 0) {
    btnValidar.innerHTML = '<i class="fas fa-check me-2"></i>Requisitos Obligatorios Completos - Continuar';
    btnValidar.disabled = false;
}

// Archivos seleccionados para obligatorios incompletos
if (archivosSeleccionadosParaObligatoriosIncompletos > 0) {
    btnValidar.innerHTML = `<i class="fas fa-upload me-2"></i>Validar y Continuar (${completos}/${total} obligatorios)`;
    btnValidar.disabled = false;
}

// Obligatorios faltantes sin archivos
btnValidar.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Completar Requisitos Obligatorios (${completos}/${total})`;
btnValidar.disabled = true;
```

## Funcionalidades Implementadas

### ✅ Separación Visual Clara
- **Sección "Requisitos Obligatorios"**: Con borde rojo y badge rojo
- **Sección "Requisitos Opcionales"**: Con borde gris y badge gris
- **Íconos diferenciados**: 
  - Obligatorios: `fas fa-exclamation-triangle` (triángulo de advertencia)
  - Opcionales: `fas fa-plus-circle` (círculo con plus)

### ✅ Validación Inteligente
- **Solo los requisitos obligatorios bloquean la transición**
- Los documentos opcionales pueden subirse pero no son requeridos
- El botón se habilita cuando todos los obligatorios están completos o tienen archivos seleccionados

### ✅ Experiencia de Usuario Mejorada
- **Información clara**: El usuario entiende qué es obligatorio y qué es opcional
- **Flexibilidad**: Puede subir documentos adicionales que faciliten el proceso
- **Progreso visual**: Contadores separados para cada tipo de requisito

### ✅ Compatibilidad
- **Retrocompatible**: Funciona con transiciones que solo tienen requisitos obligatorios
- **Modelo existente**: Usa el campo `obligatorio` del modelo `RequisitoTransicion`
- **API consistente**: Mantiene todos los campos existentes y agrega nuevos

## Cómo Usar

### Para Administradores
1. Ir a la configuración de pipelines
2. Crear o editar una transición
3. Asignar requisitos marcando si son "Obligatorios" o no (opcionales)

### Para Usuarios
1. Al intentar cambiar de etapa, se abre el modal
2. Ver claramente qué documentos son obligatorios (sección roja)
3. Ver qué documentos son opcionales (sección gris)
4. Subir documentos obligatorios para poder continuar
5. Opcionalmente subir documentos adicionales
6. El botón "Continuar" se habilita solo cuando todos los obligatorios están completos

## Ejemplos de Uso

### Transición Nuevo Lead → Consulta
**Requisitos Obligatorios:**
- APC (Antecedentes Penales) ✅ Obligatorio
- Cédula de Identidad ✅ Obligatorio

**Requisitos Opcionales:**
- Referencias Comerciales 📄 Opcional
- Comprobante de Ingresos 📄 Opcional

### Resultado
- Usuario debe subir APC y Cédula para continuar
- Puede opcionalmente subir Referencias y Comprobantes
- La transición se permite cuando APC y Cédula están completos
- Referencias y Comprobantes ayudan en el proceso pero no bloquean

## Archivos Modificados

1. `workflow/views_workflow.py` - API backend
2. `workflow/templates/workflow/partials/modalRequisitos.html` - Modal HTML y CSS
3. `workflow/templates/workflow/negocios.html` - JavaScript frontend

## Pruebas

Se han creado archivos de prueba:
- `test_requisitos_modal.py` - Test del modelo Django
- `test_modal_requisitos.html` - Demo visual del modal

## Beneficios

1. **Flexibilidad**: Los usuarios pueden proporcionar documentación adicional
2. **Eficiencia**: No bloquea el proceso por documentos opcionales
3. **Claridad**: Distinción visual clara entre obligatorio y opcional
4. **Escalabilidad**: Fácil agregar nuevos tipos de documentos
5. **Compatibilidad**: No rompe funcionalidad existente
