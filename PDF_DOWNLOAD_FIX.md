# PDF Download Fix for Historial Modal

## Problem

User reported error when clicking PDF button in historial modal: `{"error": "No Solicitud matches the given query."}`

## Root Cause Analysis

1. The PDF button in the modal was using the wrong URL pattern (`workflow:download_pdf_resultado_consulta` instead of `workflow:api_pdf_resultado_consulta`)
2. The link was trying to do a GET request to an endpoint that requires POST
3. The JavaScript was using `event.target` without properly defining the event parameter

## Solution Applied

### 1. Frontend Changes (`bandeja_comite.html`)

- **Fixed URL Pattern**: Changed from `workflow:download_pdf_resultado_consulta` to `workflow:api_pdf_resultado_consulta`
- **Changed from Links to Buttons**: Replaced `<a>` tags with `<button>` elements that call a JavaScript function
- **Updated JavaScript Function**: Created `descargarPDFResultado()` function that:
  - Sends proper POST request with JSON body
  - Uses fetch API to handle the response as a blob
  - Creates temporary download link for the PDF
  - Includes loading state and error handling
  - Properly manages button state during download

### 2. Function Implementation

```javascript
function descargarPDFResultado(solicitudId, buttonElement = null) {
  // Sends POST request to correct API endpoint
  // Handles response as blob for download
  // Includes error handling and loading states
}
```

### 3. Button Updates

- Desktop table buttons: `<button onclick="descargarPDFResultado(${solicitud.id}, this)">`
- Mobile card buttons: Same pattern with proper `this` parameter

## URL Patterns Confirmed

- ✅ Correct API endpoint: `/workflow/api/solicitudes/{id}/pdf-resultado-consulta/` (POST)
- ❌ Previous incorrect usage: `/workflow/comite/solicitud/{id}/pdf-resultado/` (GET)

## Testing Results

- ✅ PDF API working correctly with both existing and processed solicitudes
- ✅ Processed solicitudes API working correctly
- ✅ JavaScript function properly handles fetch requests and blob downloads

## Files Modified

1. `/workflow/templates/workflow/bandeja_comite.html`
   - Updated PDF button implementation in both desktop and mobile views
   - Added proper JavaScript function for PDF download
   - Fixed URL patterns and request methods

## Impact

- Users can now successfully download PDFs from the historial modal
- Proper error handling and loading states improve user experience
- Consistent API usage across the application
