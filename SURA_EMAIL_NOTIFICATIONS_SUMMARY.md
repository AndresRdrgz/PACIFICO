# SURA Email Notifications Implementation Summary

## Overview
Implemented email notifications for SURA cotización status updates similar to the existing APC notification system.

## New Functions Added to `views_workflow.py`

### 1. `enviar_correo_sura_completado(solicitud)`
- Sends email when SURA cotización is completed
- Notifies the user who created the solicitud and assigned user (if different)
- Includes client info, vehicle details, and download link for the cotización file

### 2. `enviar_correo_sura_iniciado(solicitud)`
- Sends email when SURA cotización process starts (status: in_progress)
- Provides status update to keep users informed of progress

### 3. `enviar_correo_sura_error(solicitud, mensaje_error)`
- Sends email when there's an error in the SURA cotización process
- Includes error details and recommended actions

## Updated Webhook Functions in `api_sura.py`

### 1. `api_sura_webhook_status(request, codigo)`
- Now calls appropriate email functions based on status changes:
  - `in_progress` → `enviar_correo_sura_iniciado()`
  - `completed` → `enviar_correo_sura_completado()`
  - `error` → `enviar_correo_sura_error()`

### 2. `api_sura_webhook_upload(request, codigo)`
- Calls `enviar_correo_sura_completado()` when file is uploaded
- Automatically marks solicitud as completed

## Test Functions Added

### Testing URLs (for superusers only):
- `/workflow/test/sura-completado-email/` - Test completion email
- `/workflow/test/sura-iniciado-email/` - Test in-progress email  
- `/workflow/test/sura-error-email/` - Test error email

## Email Content

Each email includes:
- Solicitud details (code, client, pipeline)
- SURA-specific client information (names, document)
- Vehicle information (value, year, make, model)
- Timestamps and status updates
- Links to view the solicitud in the system
- Professional formatting with error handling

## Integration Points

### Makito RPA Integration:
1. **Start Process**: POST to `/workflow/api/sura/update-status/{codigo}/`
   ```json
   {"status": "in_progress", "observaciones": "Starting SURA processing"}
   ```

2. **Complete with File**: POST to `/workflow/api/sura/upload-file/{codigo}/`
   - Upload PDF file as `sura_file`
   - Automatically triggers completion email

3. **Report Error**: POST to `/workflow/api/sura/update-status/{codigo}/`
   ```json
   {"status": "error", "observaciones": "Error description"}
   ```

## Email Recipients
- Primary: User who created the solicitud (`solicitud.creada_por`)
- Secondary: User assigned to the solicitud (if different from creator)
- Fallback: No email sent if no valid email addresses found

## Error Handling
- SSL certificate issues handled with fallback context
- Email sending failures don't break the main workflow
- Detailed logging for debugging

## Security
- All email functions include error handling
- Test functions restricted to superusers only
- Webhook endpoints include proper validation

## Usage Example

```python
# When Makito RPA completes a SURA cotización:
solicitud.sura_status = 'completed'
solicitud.sura_fecha_completado = timezone.now()
solicitud.save()

# This automatically triggers:
enviar_correo_sura_completado(solicitud)
```

The implementation follows the same patterns as the existing APC email system, ensuring consistency and maintainability.
