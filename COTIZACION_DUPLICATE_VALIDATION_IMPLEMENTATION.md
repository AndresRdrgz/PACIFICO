# Cotización Duplicate Validation Implementation

## Summary

This implementation adds validation to prevent creating duplicate solicitudes with the same cotización in the drawer.html form.

## Changes Made

### 1. Frontend Validation (drawer.html)

#### Added HTML Elements:

- Warning alert section to display duplicate cotización messages
- Visual feedback elements with appropriate styling

#### Added CSS Styles:

- `.alert` and `.alert-warning` classes for warning messages
- `.form-control.is-invalid` and `.form-control.is-valid` for form validation feedback

#### Added JavaScript Functions:

- `validateCotizacionDuplicate(cotizacionId, pipelineId)` - Calls API to check for duplicates
- `showCotizacionDuplicateWarning(existingSolicitudData)` - Shows warning with existing solicitud info
- `hideCotizacionDuplicateWarning()` - Hides warning and shows valid state
- `checkCotizacionBeforeSubmit()` - Pre-submission validation with user confirmation

### 2. Integration in negocios.html

#### Modified Functions:

- `selectItem()` - Now calls validation when a cotización is selected
- `validateCotizacionSelection()` - New function to validate on selection
- `submitSolicitud()` - Added pre-submission validation with user confirmation
- `proceedWithFormSubmission()` - Extracted form submission logic for cleaner code

### 3. Backend API (api.py)

#### New API Endpoint:

- `api_validate_cotizacion_duplicate()` - Validates if cotización exists in pipeline
- Returns detailed information about existing solicitudes
- Handles error cases gracefully

#### API Response Format:

```json
{
    "success": true,
    "isDuplicate": false/true,
    "existingSolicitud": {
        "id": 123,
        "codigo": "SOL-2024-001",
        "etapa_actual": "Análise de Crédito",
        "fecha_creacion": "30/07/2025 14:30",
        "creada_por": "Juan Pérez"
    },
    "totalDuplicates": 1,
    "message": "Description message"
}
```

### 4. URL Configuration (urls_workflow.py)

#### Added Route:

- `api/validate-cotizacion-duplicate/` - Maps to the validation endpoint

### 5. Server-side Validation (views_workflow.py)

#### Note:

Server-side validation was planned but not implemented due to multiple duplicate functions in the codebase. This should be added for complete security:

```python
# In nueva_solicitud function, before Solicitud.objects.create():
if cotizacion:
    existing_solicitudes = Solicitud.objects.filter(
        cotizacion=cotizacion,
        pipeline=pipeline
    ).exists()

    if existing_solicitudes:
        # Return error or redirect with message
```

## User Experience Flow

1. **Cotización Selection**: User selects a cotización from the search dropdown
2. **Automatic Validation**: System checks if cotización is already used in the pipeline
3. **Visual Feedback**: If duplicate found, warning message appears with existing solicitud details
4. **Form Submission**: Before submission, system performs final validation
5. **User Confirmation**: If duplicate detected, user gets confirmation dialog
6. **Prevention**: User can choose to cancel or proceed with duplicate creation

## Features

- **Real-time Validation**: Checks duplicates as soon as cotización is selected
- **Visual Indicators**: Clear warning messages and form validation states
- **User Choice**: Allows informed decision-making with confirmation dialogs
- **Detailed Information**: Shows existing solicitud details for context
- **Error Handling**: Graceful fallback if validation API fails
- **Server-side Protection**: API endpoint provides backend validation

## Testing

A test HTML file was created at `/test_validation.html` to verify the API endpoint functionality.

## Security Considerations

- Client-side validation provides user experience
- Server-side validation (recommended to be added) provides security
- API endpoint requires authentication (@login_required)
- Error handling prevents information leakage

## Files Modified

1. `/workflow/templates/workflow/partials/drawer.html` - Frontend validation UI and logic
2. `/workflow/templates/workflow/negocios.html` - Integration with form submission
3. `/workflow/api.py` - Backend validation API endpoint
4. `/workflow/urls_workflow.py` - URL routing for API endpoint
5. `/test_validation.html` - Test file for validation functionality

## Next Steps

1. Add server-side validation to `views_workflow.py` in the `nueva_solicitud` function
2. Test the complete implementation in a development environment
3. Consider adding configuration options for strict vs. warning-only validation
4. Add logging for duplicate detection analytics
