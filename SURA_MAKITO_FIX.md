# SURA Makito API Fix

## Problem

The SURA Makito API endpoint (`/workflow/api/solicitar-sura-makito/{id}/`) was throwing a 500 Internal Server Error with the message:

```
'Cliente' object has no attribute 'cedula'
```

## Root Cause

The `api_solicitar_sura_makito` function in `workflow/views_workflow.py` was trying to access the `cedula` attribute on the `Cliente` model, but the actual field name in the `Cliente` model is `cedulaCliente`.

Additionally, the function was trying to access `primer_nombre` and `primer_apellido` fields that don't exist in the `Cliente` model. The actual field is `nombreCliente` which contains the full name and needs to be parsed.

## Fields Fixed

1. `solicitud.cliente.cedula` → `solicitud.cliente.cedulaCliente`
2. `solicitud.cliente.ruc` → Removed (doesn't exist in Cliente model)
3. `solicitud.cliente.primer_nombre` → Parsed from `solicitud.cliente.nombreCliente`
4. `solicitud.cliente.primer_apellido` → Parsed from `solicitud.cliente.nombreCliente`
5. `solicitud.cotizacion.cedula` → `solicitud.cotizacion.cedulaCliente`
6. `solicitud.cotizacion.cliente_nombre` → `solicitud.cotizacion.nombreCliente`

## Code Changes

Updated the client information extraction logic in `api_solicitar_sura_makito` function (lines ~7365-7380) to:

```python
if hasattr(solicitud, 'cliente') and solicitud.cliente:
    documento_cliente = solicitud.cliente.cedulaCliente
    # Intentar extraer nombres del campo nombreCliente
    if solicitud.cliente.nombreCliente:
        nombres = solicitud.cliente.nombreCliente.split()
        if len(nombres) >= 2:
            primer_nombre = nombres[0]
            primer_apellido = nombres[-1]
        elif len(nombres) == 1:
            primer_nombre = nombres[0]
elif hasattr(solicitud, 'cotizacion') and solicitud.cotizacion:
    documento_cliente = solicitud.cotizacion.cedulaCliente
    # Intentar extraer nombres de la cotización si están disponibles
    if solicitud.cotizacion.nombreCliente:
        nombres = solicitud.cotizacion.nombreCliente.split()
        if len(nombres) >= 2:
            primer_nombre = nombres[0]
            primer_apellido = nombres[-1]
```

## Verification

- ✅ Cliente model has `cedulaCliente` field (not `cedula`)
- ✅ Cliente model has `nombreCliente` field (not `primer_nombre`/`primer_apellido`)
- ✅ Cotizacion model has `cedulaCliente` field (not `cedula`)
- ✅ Cotizacion model has `nombreCliente` field (not `cliente_nombre`)

## Test Results

Tested with solicitud FLU-130:

- Cliente cedulaCliente: 151610697
- Cliente nombreCliente: Andres Rodriguez
- Parsed primer_nombre: Andres
- Parsed primer_apellido: Rodriguez

The fix ensures proper field access and name parsing for SURA Makito requests.
