# Bandeja Comité - Solicitudes Procesadas Implementation

## Overview

This implementation adds a new section to the "Bandeja del Comité de Crédito" that allows users to view, search, and download PDF results for solicitudes that have been processed by the comité de crédito.

## Features Implemented

### 1. Backend API Endpoints

#### New Views in `views_comite.py`:

1. **`api_solicitudes_procesadas_comite`**

   - URL: `/api/comite/solicitudes-procesadas/`
   - Method: GET
   - Purpose: Returns paginated list of solicitudes processed by the comité
   - Features:
     - Search by client name, cedula, or solicitud code
     - Pagination (10 items per page by default)
     - Filters only solicitudes with committee participation
     - Permission checking (same as bandeja_comite)

2. **`download_pdf_resultado_consulta`**
   - URL: `/comite/solicitud/<solicitud_id>/pdf-resultado/`
   - Method: GET
   - Purpose: Downloads PDF resultado de consulta for a specific solicitud
   - Features:
     - Uses the existing `pdf_resultado_consulta_simple.html` template
     - Includes committee participations and decisions
     - Permission checking
     - Falls back to HTML if xhtml2pdf is not available

### 2. Frontend Implementation

#### New Template Section in `bandeja_comite.html`:

1. **Header Section**

   - Displays total count of processed solicitudes
   - Refresh button
   - Consistent styling with existing sections

2. **Search Functionality**

   - Real-time search with debouncing (500ms delay)
   - Searches client name, cedula, and solicitud code

3. **Desktop Table View**

   - Columns: Cliente, Monto, Producto, Decisión Comité, Etapa Actual, Fecha Procesado, Código, Acciones
   - Actions: View details, Download PDF
   - Decision badges with color coding (Aprobado, Rechazado, Observaciones, Pendiente)

4. **Mobile Card View**

   - Responsive cards for mobile devices
   - Same information as table but optimized for smaller screens

5. **Pagination**

   - Previous/Next buttons
   - Page numbers
   - Row count display

6. **Loading and Empty States**
   - Loading spinner while fetching data
   - Empty state when no processed solicitudes exist

### 3. CSS Styling

#### New CSS Classes:

- `.decision-badge` with variants for different decision types
- `.btn-download-pdf` and `.btn-view-procesada` for action buttons
- `.loading-spinner` for loading animations
- Responsive design considerations

### 4. JavaScript Functionality

#### Key Functions:

- `cargarSolicitudesProcesadas()` - Main function to load processed solicitudes
- `renderizarSolicitudesProcesadas()` - Renders table and mobile cards
- `renderizarPaginacionProcesadas()` - Handles pagination display
- Search debouncing and event handling
- State management for loading/empty states

## URLs Added

```python
# In urls_workflow.py
path('api/comite/solicitudes-procesadas/', views_comite.api_solicitudes_procesadas_comite, name='api_solicitudes_procesadas_comite'),
path('comite/solicitud/<int:solicitud_id>/pdf-resultado/', views_comite.download_pdf_resultado_consulta, name='download_pdf_resultado_consulta'),
```

## How to Test

### 1. Access the Bandeja Comité

1. Navigate to `/workflow/comite/`
2. Scroll down to see the new "Solicitudes Procesadas por el Comité" section

### 2. Test Search Functionality

1. Type in the search box to filter processed solicitudes
2. Search works on client name, cedula, and solicitud code

### 3. Test Pagination

1. If there are more than 10 processed solicitudes, use pagination controls
2. Navigate between pages to see all results

### 4. Test PDF Download

1. Click the "PDF" button next to any processed solicitud
2. The PDF should download with committee participation details

### 5. Test Responsive Design

1. Resize browser window or use mobile device
2. Table should switch to card view on smaller screens

## Prerequisites

### Database Requirements:

- Solicitudes must have `ParticipacionComite` records to appear in processed list
- Comité de Crédito etapa must exist
- Users must have appropriate permissions (PermisoBandeja)

### Optional Dependencies:

- `xhtml2pdf` for PDF generation (falls back to HTML if not available)

## Permission System

The new functionality uses the same permission system as the existing bandeja_comite:

- Superusers have full access
- Regular users need `PermisoBandeja` for "Comité de Crédito" etapa
- Permissions can be assigned directly to users or through groups

## Data Fields Displayed

### For each processed solicitud:

- **Cliente**: Name and cedula from Cliente or Cotizacion
- **Monto**: Amount from Cotizacion.montoSolicitado
- **Producto**: Type from Cotizacion.tipoPrestamo
- **Decisión Comité**: Latest ParticipacionComite.resultado
- **Etapa Actual**: Current stage of the solicitud
- **Fecha Procesado**: Last modification date
- **Código**: Solicitud code

## Error Handling

- Graceful degradation if API fails
- Permission checks with appropriate error messages
- Loading states and empty states
- Console logging for debugging

## Future Enhancements

Possible improvements:

1. Advanced filters (date range, decision type, amount range)
2. Export functionality for the processed solicitudes list
3. Bulk operations on processed solicitudes
4. Integration with notification system for new processed solicitudes
