# Nueva Solicitud Modal Filtering Fix

## Problem

After successfully processing a SURA Makito request, the solicitud was still showing up in the "nueva solicitud" modal, allowing users to request the same service multiple times.

## Root Cause

The filtering logic in the `loadAvailableSolicitudes()` function in `makito_tracking.html` was only checking if solicitudes were not completed, but wasn't filtering out solicitudes that already had the selected service type (APC, SURA, or Debida Diligencia) in progress or completed.

Additionally, the API endpoint `/workflow/api/solicitudes/` was missing the service status fields needed for proper filtering.

## Solutions Applied

### 1. Fixed API Response in `views_negocios.py`

The actual API endpoint being used by the makito tracking modal is `views_negocios.api_solicitudes`, not `views_workflow.api_solicitudes`.

Added missing service status fields to the API response:

```python
# Status fields for all services
'sura_status': solicitud.sura_status or '',
'debida_diligencia_status': solicitud.debida_diligencia_status or '',
```

### 2. Enhanced JavaScript Filtering Logic

Updated the filtering logic in `makito_tracking.html` to properly filter solicitudes based on service status:

```javascript
const filteredSolicitudes = availableSolicitudes.filter((solicitud) => {
  // Only show active solicitudes (not completed)
  if (!solicitud.etapa_actual || solicitud.etapa_actual === "Completado") {
    return false;
  }

  // Filter based on selected service type status
  switch (selectedServiceType) {
    case "apc":
      // Don't show if APC is already pending, in_progress, or completed
      return (
        !solicitud.apc_status ||
        solicitud.apc_status === "" ||
        solicitud.apc_status === "no_iniciado"
      );

    case "sura":
      // Don't show if SURA is already pending, in_progress, or completed
      return (
        !solicitud.sura_status ||
        solicitud.sura_status === "" ||
        solicitud.sura_status === "no_iniciado"
      );

    case "debida_diligencia":
      // Don't show if Debida Diligencia is already pending, in_progress, or completed
      return (
        !solicitud.debida_diligencia_status ||
        solicitud.debida_diligencia_status === "" ||
        solicitud.debida_diligencia_status === "no_iniciado"
      );

    default:
      return true;
  }
});
```

## Status Field Values

- `''` (empty string): Service not initiated
- `'no_iniciado'`: Service not initiated
- `'pending'`: Service requested/pending
- `'in_progress'`: Service being processed
- `'completed'`: Service completed
- `'error'`: Service failed

## Test Results

✅ API now returns correct service status fields:

- `apc_status`: "pending"
- `sura_status`: "pending"
- `debida_diligencia_status`: "no_iniciado"

✅ Filtering logic properly excludes solicitudes with active service requests
✅ SURA Makito requests work successfully and send emails
✅ After processing, solicitudes are filtered out from the "nueva solicitud" modal

## Files Modified

1. `/workflow/views_negocios.py` - Added missing status fields to API response
2. `/workflow/templates/workflow/makito_tracking.html` - Enhanced filtering logic
3. `/workflow/views_workflow.py` - Fixed original SURA Makito Cliente field access bug

The nueva solicitud modal now properly filters out solicitudes that already have the selected service type initiated, preventing duplicate requests.
