## Drawer Cliente Auto-Population Fix Summary

### Issues Found and Fixed:

1. **Missing URL patterns**: Added drawer-specific API endpoints to `urls_workflow.py`
2. **Missing auto-population call**: Added `autoPopulateClienteFromCotizacion(item)` call in `selectItem` function
3. **Incorrect API endpoints**: Fixed JavaScript to use correct drawer-specific endpoints

### Changes Made:

#### 1. urls_workflow.py
```python
# Added drawer-specific API endpoints
path('api/buscar-clientes-drawer/', views_workflow.api_buscar_clientes_drawer, name='api_buscar_clientes_drawer'),
path('api/buscar-cotizaciones-drawer/', views_workflow.api_buscar_cotizaciones_drawer, name='api_buscar_cotizaciones_drawer'),
```

#### 2. negocios.html - selectItem function
```javascript
// Added auto-population call for cotización selection
if (type === 'cotizacion') {
    // ... existing code ...
    
    // Auto-populate cliente from cotización
    autoPopulateClienteFromCotizacion(item);
}
```

### How It Should Work Now:

1. User types in cotización search field
2. JavaScript calls `/workflow/api/buscar-cotizaciones-drawer/` endpoint
3. Results are displayed, user selects a cotización
4. `selectItem('cotizacion', item)` is called
5. Cotización data is populated in the form
6. `autoPopulateClienteFromCotizacion(item)` is called
7. This function searches for a matching cliente by cédula using `/workflow/api/buscar-clientes-drawer/`
8. If found, `selectClienteAutomatically(cliente)` populates the cliente section
9. Cliente section shows with auto-populated indicator

### Testing:
- All backend API functions exist and return proper data format
- JavaScript logic is in place
- URL patterns are correctly configured
- Auto-population indicator is added to show it came from cotización

The cliente section should now automatically populate when a cotización is selected in the drawer.
