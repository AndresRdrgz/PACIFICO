# SURA Tracking Fix Summary

## Problem Identified
The SURA solicitudes were not appearing in the Makito tracking table because the SURA API (`/workflow/api/sura/list/`) was failing with a 500 error.

## Root Cause
In the `api_sura_list` function in `workflow/api_sura.py`, the code was trying to access incorrect field names on the `Cliente` model:
- Trying to access: `solicitud.cliente.primer_nombre`, `solicitud.cliente.segundo_nombre`, etc.
- But Cliente model actually has: `nombreCliente`, `cedulaCliente`

## Fix Applied
Updated `workflow/api_sura.py` line 54-56:

**Before:**
```python
if solicitud.cliente:
    cliente_nombre = f"{solicitud.cliente.primer_nombre or ''} {solicitud.cliente.segundo_nombre or ''} {solicitud.cliente.primer_apellido or ''} {solicitud.cliente.segundo_apellido or ''}".strip()
    cliente_documento = solicitud.cliente.cedula or ''
```

**After:**
```python
if solicitud.cliente:
    cliente_nombre = solicitud.cliente.nombreCliente or ''
    cliente_documento = solicitud.cliente.cedulaCliente or ''
```

## Verification Results
✅ **SURA API now working correctly:**
- Returns 200 status (was 500 before)
- Successfully returns 2 SURA solicitudes
- Data structure is correct with all required fields

✅ **Sample SURA data returned:**
```json
{
  "id": 117,
  "codigo": "FLU-117",
  "cliente_nombre": "Andres Rodriguez",
  "cliente_documento": "151610697",
  "pipeline": {"id": 12, "nombre": "Flujo de Consulta de Auto"},
  "sura_status": "pending",
  "sura_status_display": "Pendiente",
  ...
}
```

## Result
The SURA API endpoint is now functional and returning the correct data format that the Makito tracking interface expects. SURA solicitudes should now appear in the tracking table alongside APC solicitudes.

## Testing
To verify the fix is working in the browser:
1. Navigate to the Makito tracking page
2. Check that both APC and SURA solicitudes are displayed
3. The tracking table should show 2 SURA solicitudes with proper data

The JavaScript `loadTrackingData()` function in `makito_tracking.html` calls both APIs:
- `/workflow/api/apc/list/` (working)
- `/workflow/api/sura/list/` (now fixed and working)
