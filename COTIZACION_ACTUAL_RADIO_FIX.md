# Fix: "Usar Cotización Actual" Radio Button Issue

## Problem Description

When clicking "Enviar Reconsideración" with the "Usar cotización actual" radio button selected, the system was showing the warning message: **"Por favor, selecciona una cotización."**

## Root Cause Analysis

### Issues Found:

1. **Incorrect Radio Button Names**: The validation function was looking for `input[name="cotizacion_id"]` but the actual radio buttons are named `cotizacion_opcion`
2. **Missing Cotización ID Logic**: When "usar cotización actual" was selected, the system wasn't properly identifying or using the current cotización
3. **Validation Logic Mismatch**: The validation function wasn't correctly checking the nueva cotización selection method

## Solutions Applied

### 1. **Fixed `enviarReconsideracion()` Function**

- **Before**: Was looking for `document.querySelector('input[name="cotizacion_id"]:checked')`
- **After**: Now properly checks `cotizacionActual` and `cotizacionNueva` radio buttons by ID
- **Improvement**: Added fallback logic to use `'actual'` as cotización ID when current cotización data isn't available

```javascript
// Old logic (broken)
const cotizacionSelected = document.querySelector(
  'input[name="cotizacion_id"]:checked'
);

// New logic (fixed)
if (cotizacionActualSelected) {
  cotizacionId = currentData?.cotizacion?.id || "actual";
} else if (cotizacionNuevaSelected) {
  cotizacionId = document.getElementById("nuevaCotizacionId").value;
}
```

### 2. **Fixed `validarFormularioReconsideracion()` Function**

- **Before**: Was checking for non-existent `input[name="cotizacion_id"]` radio buttons
- **After**: Now properly validates based on the correct radio button structure
- **Improvement**: Added check for `nuevaCotizacionId` hidden field when nueva cotización is selected

```javascript
// Old logic (broken)
cotizacionSelected = Array.from(cotizacionRadios).some(
  (radio) => radio.checked
);

// New logic (fixed)
if (cotizacionNuevaSelected) {
  const nuevaCotizacionIdField = document.getElementById("nuevaCotizacionId");
  cotizacionSelected = nuevaCotizacionIdField && nuevaCotizacionIdField.value;
}
```

### 3. **Enhanced Radio Button Event Handlers**

- **Added**: Clear nueva cotización ID when switching to "usar cotización actual"
- **Improved**: Better validation triggering on radio button changes
- **Added**: Event listener for `nuevaCotizacionId` field changes

## Form Structure Clarification

### Radio Button Structure:

```html
<!-- Main cotización option selection -->
<input
  type="radio"
  name="cotizacion_opcion"
  id="cotizacionActual"
  value="actual"
  checked
/>
<input
  type="radio"
  name="cotizacion_opcion"
  id="cotizacionNueva"
  value="nueva"
/>

<!-- Hidden field for selected nueva cotización -->
<input type="hidden" name="nueva_cotizacion_id" id="nuevaCotizacionId" />
```

### Validation Logic Flow:

1. **Usar Cotización Actual**: ✅ Always valid when selected (uses current cotización)
2. **Usar Nueva Cotización**: ✅ Valid only when a specific cotización has been selected from the list

## Testing Scenarios

### ✅ **Should Work Now:**

1. Select "Usar cotización actual" → Enter motivo (50+ chars) → Click "Enviar" ✅
2. Select "Usar una cotización diferente" → Choose specific cotización → Enter motivo → Click "Enviar" ✅
3. Switch between options without validation errors ✅

### 🚫 **Should Still Show Validation:**

1. Select "Usar una cotización diferente" but don't choose specific cotización → ❌ "Selecciona una cotización específica"
2. Don't enter motivo or enter less than 50 characters → ❌ "Proporciona un motivo válido"
3. Don't select any radio option → ❌ "Selecciona una opción de cotización"

## Files Modified

- `/workflow/templates/workflow/partials/modalSolicitud.html`
  - Fixed `enviarReconsideracion()` function
  - Fixed `validarFormularioReconsideracion()` function
  - Enhanced radio button event handlers
  - Improved validation logic

## Backend Considerations

The backend should now receive either:

- A numeric cotización ID (when nueva cotización is selected)
- The string `'actual'` (when usar cotización actual is selected)

The backend should handle the `'actual'` value by using the solicitud's current cotización.
