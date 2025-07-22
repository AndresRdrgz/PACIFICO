# Solicitud Codigo Generation Update

## Overview

The solicitud `codigo` generation system has been updated from a randomized UUID-based format to a sequential format using the actual solicitud ID. This provides better readability, tracking, and consistency.

## Changes Made

### 1. Model Updates (`workflow/modelsWorkflow.py`)

- **Modified `codigo` field**: Changed from `unique=True` to `unique=True, blank=True, null=True` to allow automatic generation
- **Added `generar_codigo()` method**: Generates sequential codes using the format `{PIPELINE_PREFIX}-{ID}`
- **Added `post_save` signal**: Automatically generates the code after solicitud creation
- **Enhanced `save()` method**: Handles code generation for existing records

### 2. View Updates (`workflow/views_workflow.py`)

- **Removed UUID generation**: Eliminated the random UUID-based code generation
- **Simplified solicitud creation**: The code is now generated automatically via the signal
- **Updated response messages**: Now uses the generated code from the solicitud object

### 3. Migration (`workflow/migrations/0024_update_codigo_generation.py`)

- **Schema migration**: Updated the `codigo` field to allow null/blank values
- **Data migration**: Converts existing solicitudes to use the new sequential format
- **Backward compatibility**: Handles existing codes gracefully

### 4. Setup Script Updates (`workflow/setup_workflow.py`)

- **Removed hardcoded codes**: No longer generates specific codes in setup
- **Updated requisito creation**: Uses the current model structure
- **Cleaned up references**: Removed unused TipoSolicitud references

## New Code Format

### Format: `{PIPELINE_PREFIX}-{ID}`

- **PIPELINE_PREFIX**: First 3 letters of the pipeline name (cleaned of special characters)
- **ID**: The actual database ID of the solicitud

### Examples:

- Pipeline: "Préstamo Personal" → Code: "PRS-123"
- Pipeline: "Auto Loan" → Code: "AUT-456"
- Pipeline: "Test Pipeline" → Code: "TES-789"

### Special Character Handling:

- Spaces, accents, and special characters are removed
- Only alphanumeric characters are used for the prefix
- If less than 3 characters remain, the full cleaned name is used

## Benefits

1. **Sequential and Predictable**: Codes follow a logical sequence
2. **Easy to Track**: Direct correlation between code and database ID
3. **Human Readable**: Much easier to read and understand than random UUIDs
4. **Consistent**: Same format across all pipelines
5. **Database Efficient**: Uses existing auto-incrementing ID

## Technical Implementation

### Signal-Based Generation

```python
@receiver(post_save, sender=Solicitud)
def generar_codigo_solicitud(sender, instance, created, **kwargs):
    if created and not instance.codigo:
        instance.codigo = instance.generar_codigo()
        Solicitud.objects.filter(id=instance.id).update(codigo=instance.codigo)
```

### Code Generation Logic

```python
def generar_codigo(self):
    pipeline_clean = re.sub(r'[^a-zA-Z0-9]', '', self.pipeline.nombre)
    pipeline_prefix = pipeline_clean[:3].upper()
    return f"{pipeline_prefix}-{self.id}"
```

## Migration Process

1. **Schema Update**: Field allows null/blank values
2. **Data Migration**: Existing codes are converted to new format
3. **Signal Activation**: New solicitudes get automatic code generation

## Testing

The implementation has been tested with:
- ✅ Basic sequential generation
- ✅ Special character handling
- ✅ Multiple pipeline types
- ✅ Existing data migration
- ✅ Signal-based automation

## Backward Compatibility

- Existing solicitudes are automatically migrated
- No data loss during the transition
- All existing functionality remains intact
- API responses continue to work as expected 