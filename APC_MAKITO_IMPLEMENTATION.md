# APC Makito Functionality Implementation

## Overview
Successfully implemented the "Descargar APC con Makito" functionality that allows users to request APC downloads through the workflow system with automatic email notifications.

## Implementation Details

### 1. Database Changes (modelsWorkflow.py)
Added new fields to the Solicitud model:

```python
# APC con Makito fields
TIPO_DOCUMENTO_CHOICES = [
    ('cedula', 'Cédula'),
    ('pasaporte', 'Pasaporte'),
]

descargar_apc_makito = models.BooleanField(default=False, help_text="Indica si se debe descargar APC con Makito")
apc_no_cedula = models.CharField(max_length=50, null=True, blank=True, help_text="Número de cédula o pasaporte para APC")
apc_tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES, null=True, blank=True, help_text="Tipo de documento para APC")
```

### 2. Frontend Changes (drawer.html)
Added new section to the drawer panel:

- **Toggle Section**: "Descargar APC con Makito" with checkbox
- **Conditional Fields**: When checkbox is enabled, shows:
  - Type of document dropdown (Cédula/Pasaporte)
  - Document number input field
- **Proper Form Validation**: Fields are required when checkbox is enabled

### 3. JavaScript Functionality (negocios.html)
Implemented comprehensive JavaScript functionality:

- **Section Visibility**: APC section appears when cotización is selected
- **Toggle Logic**: Checkbox controls visibility of additional fields
- **Form Reset**: Properly resets APC fields when form is cleared
- **Validation**: Client-side validation for required APC fields
- **Event Handlers**: Proper event listeners for checkbox changes

### 4. Backend Processing (views_workflow.py)
Enhanced nueva_solicitud function:

- **Form Processing**: Extracts APC fields from form data
- **Database Storage**: Saves APC fields to solicitud model
- **Email Trigger**: Calls email function when APC is requested
- **Validation**: Server-side validation for APC fields

### 5. Email Functionality (views_workflow.py)
Created `enviar_correo_apc_makito` function:

- **Recipient**: arodriguez@fpacifico.com
- **Subject Format**: "workflowAPC - [Cliente Name] - [Document Number]"
- **Content**: Includes all solicitud and APC details
- **Error Handling**: Comprehensive error handling with SSL fallback

## Email Details

### Subject Format
```
workflowAPC - [Cliente Name] - [Document Number]
```

### Email Body Content
- Solicitud code and details
- Client information
- Document type and number
- Pipeline information
- User who created the request
- Creation timestamp

### Example Email
```
Subject: workflowAPC - Juan Pérez - 8-123-456

Body:
Solicitud de Descarga APC con Makito

Se ha solicitado la descarga del APC para la siguiente solicitud:

• Código de Solicitud: FLU-ABC12345
• Cliente: Juan Pérez
• Tipo de Documento: Cédula
• Número de Documento: 8-123-456
• Pipeline: Flujo de Consulta de Auto
• Solicitado por: Usuario Test
• Fecha de Solicitud: 21/07/2025 15:30

Información para APC:
Tipo de documento: Cédula
noCedula: 8-123-456
```

## User Flow

1. User opens drawer to create new negocio
2. User selects cotización (APC section appears)
3. User checks "Descargar APC con Makito" checkbox
4. Additional fields appear for document type and number
5. User fills in required APC information
6. User submits form
7. System validates APC fields
8. Solicitud is created with APC data
9. Email is automatically sent to arodriguez@fpacifico.com
10. Success confirmation shown to user

## Testing

### Automated Tests
- ✅ Model field validation
- ✅ Form submission with APC data
- ✅ Email function execution
- ✅ Database integration
- ✅ Frontend validation

### Test Results
- Database migration: ✅ Successful
- Form submission: ✅ Working
- Email sending: ✅ Functional
- Frontend validation: ✅ Active
- Backend processing: ✅ Complete

## Files Modified

1. **workflow/modelsWorkflow.py**: Added APC fields to Solicitud model
2. **workflow/templates/workflow/partials/drawer.html**: Added APC section
3. **workflow/templates/workflow/negocios.html**: Added JavaScript functionality
4. **workflow/views_workflow.py**: Added backend processing and email function

## Database Migration
Migration created and applied successfully for new APC fields.

## Production Ready
✅ All functionality implemented and tested
✅ Error handling in place
✅ Proper validation (frontend and backend)
✅ Email notifications working
✅ Database schema updated
✅ User interface integrated

The APC Makito functionality is fully implemented and ready for production use!
