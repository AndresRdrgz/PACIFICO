# API PDF Resultado Consulta - Reconsideraciones Update

## Overview

Updated the `api_pdf_resultado_consulta` function in `views_workflow.py` to properly retrieve and display ALL reconsiderations associated with a solicitud in the PDF template.

## Changes Made

### 1. Enhanced Reconsiderations Retrieval Logic

**File**: `workflow/views_workflow.py` - Function: `api_pdf_resultado_consulta`

#### Previous Behavior:

- Only retrieved reconsiderations in specific modes (preview mode with specific ID)
- Did not always include all historical reconsiderations
- Complex conditional logic that could miss reconsiderations

#### New Behavior:

- **Always retrieves ALL reconsiderations** for the solicitud, regardless of mode
- Simplifies the logic by making reconsideration retrieval the primary data source
- Maintains backward compatibility with preview mode functionality
- Proper error handling and comprehensive logging

### 2. Key Improvements

#### Universal Reconsiderations Retrieval

```python
# Always get ALL reconsiderations for the solicitud, ordered chronologically
reconsideraciones = ReconsideracionSolicitud.objects.filter(
    solicitud=solicitud
).select_related(
    'solicitada_por', 'analizada_por', 'cotizacion_original', 'cotizacion_nueva'
).order_by('numero_reconsideracion')  # Chronological order
```

#### Enhanced User Name Resolution

- Improved fallback chain for user names:
  1. `solicitud.propietario` (owner)
  2. `solicitud.creada_por` (creator)
  3. `reconsideracion.solicitada_por` (individual reconsideration requester)

#### Preview Mode Integration

- When in preview mode with a specific reconsideration ID, overlay preview data on that specific reconsideration
- All other reconsiderations remain unchanged
- Preview indicators are properly set for template rendering

### 3. Data Structure

#### `reconsideraciones_data` (List)

Contains all reconsiderations for the solicitud with complete information:

```python
reconsideracion_item = {
    'numero_reconsideracion': int,
    'estado': str,
    'motivo': str,
    'fecha_solicitud': datetime,
    'fecha_analisis': datetime|None,
    'comentario_analisis': str,
    'decision_preview': str|None,  # Only for preview mode
    'usar_nueva_cotizacion': bool,
    'usar_misma_cotizacion': bool,
    'resultado_consulta_anterior': str,
    'comentario_consulta_anterior': str,
    'solicitada_por_nombre': str,
    'analizada_por_nombre': str,
    'cotizacion_original': Cotizacion|None,
    'cotizacion_nueva': Cotizacion|None,
    'is_preview': bool,  # Only true for preview reconsideration
}
```

#### `reconsideracion_data` (Single)

Maintained for backward compatibility - contains the most recent reconsideration.

### 4. Template Integration

The existing template `pdf_resultado_consulta_simple.html` already supports both:

#### Multiple Reconsiderations Display

```django
{% if reconsideraciones_data %}
    <div class="comite-section">
        <div class="comite-title">Historial de Reconsideraciones</div>
        <div>Total de reconsideraciones: {{ reconsideraciones_data|length }}</div>

        {% for reconsideracion in reconsideraciones_data %}
            <!-- Display each reconsideration chronologically -->
        {% endfor %}
    </div>
{% elif reconsideracion_data %}
    <!-- Backward compatibility single reconsideration display -->
{% endif %}
```

### 5. Testing Results

#### Test Data: Solicitud 170

- **Found**: 3 reconsiderations
- **Reconsideration #1**: rechazada - "tesa"
- **Reconsideration #2**: aprobada - "Prueba de reconsideracion #2"
- **Reconsideration #3**: enviada - "como asi"

All reconsiderations are now properly retrieved and will be displayed in the PDF.

### 6. Error Handling

#### Comprehensive Error Handling

```python
try:
    # Reconsideration retrieval logic
    print(f"Found {reconsideraciones.count()} total reconsideraciones")
    # Process each reconsideration
except Exception as e:
    print(f"Error obteniendo datos de reconsideraciones: {e}")
    import traceback
    traceback.print_exc()
    # Continue without reconsideration data
```

#### Debug Logging

- Added detailed logging for debugging PDF generation
- Track number of reconsiderations found and processed
- Individual reconsideration processing confirmation
- Preview mode detection and handling

### 7. Backward Compatibility

#### Maintained Features

- ✅ Single `reconsideracion_data` for existing template logic
- ✅ Preview mode functionality for committee modal
- ✅ All existing context variables
- ✅ Error handling patterns
- ✅ Template structure unchanged

#### Enhanced Features

- ✅ Always retrieves ALL reconsiderations
- ✅ Chronological ordering
- ✅ Improved user name resolution
- ✅ Better error handling and logging

### 8. PDF Output Behavior

#### For Regular PDF Generation

- Shows complete historical timeline of all reconsiderations
- Displays them in chronological order (oldest to newest)
- Most recent reconsideration highlighted
- Complete information for each reconsideration

#### For Preview Mode

- Shows all historical reconsiderations
- Overlays preview data on the specific reconsideration being edited
- Preview indicators clearly marked
- Live preview values displayed when available

## Usage

### API Call Examples

#### Regular PDF Generation

```javascript
fetch("/api/pdf-resultado-consulta/170/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({}),
});
```

#### Preview Mode with Reconsideration

```javascript
fetch("/api/pdf-resultado-consulta/170/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    reconsideration_mode: true,
    reconsideration_id: 123,
    comentario_analisis: "Preview comment",
    decision_preview: "Preview decision",
    is_preview: true,
  }),
});
```

## Verification

To verify the update works correctly:

1. **Test PDF Generation**: Generate PDF for solicitud 170 (or any solicitud with reconsiderations)
2. **Check Console Output**: Look for log messages showing reconsiderations found and processed
3. **Verify PDF Content**: Ensure all reconsiderations appear in chronological order
4. **Test Preview Mode**: Use preview mode to verify preview data overlay works correctly

## Expected Behavior

✅ **All reconsiderations** associated with a solicitud will now appear in the PDF
✅ **Chronological ordering** from oldest to newest
✅ **Complete information** for each reconsideration (dates, users, status, comments)
✅ **Preview mode** continues to work with live preview data overlay
✅ **Backward compatibility** maintained for existing functionality

The API now ensures that no reconsideration data is missed and provides a complete historical view in the generated PDF documents.
