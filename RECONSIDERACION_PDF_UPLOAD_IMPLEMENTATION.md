# Implementación de Upload de Archivos PDF en Reconsideraciones

## Resumen de la Implementación

Se ha agregado la funcionalidad para subir archivos PDF como adjuntos cuando se selecciona una cotización para reconsideración en el sistema de workflow.

## Cambios Realizados

### 1. **Backend (Django)**

#### Modelo ReconsideracionSolicitud
- ✅ Agregado campo `archivo_adjunto` de tipo `FileField`
- ✅ Upload path: `reconsideraciones/`
- ✅ Campo opcional (null=True, blank=True)

#### Vista api_solicitar_reconsideracion
- ✅ Modificada para manejar tanto JSON como FormData
- ✅ Validación de archivos PDF (extensión y tamaño máx 10MB)
- ✅ Almacenamiento del archivo en el modelo ReconsideracionSolicitud

### 2. **Frontend (HTML/CSS/JavaScript)**

#### HTML Template
- ✅ Agregada sección de upload de archivos en modal de reconsideración
- ✅ Drag & drop área con estilos modernos
- ✅ Preview del archivo seleccionado
- ✅ Botón para remover archivo

#### CSS Styles
- ✅ Estilos para upload area con hover y drag states
- ✅ Preview card con información del archivo
- ✅ Responsive design consistente con el diseño existente

#### JavaScript Functions
- ✅ `setupArchivoUploadHandlers()` - Inicializa event listeners
- ✅ `handleFileSelection()` - Valida y procesa archivos
- ✅ `showFilePreview()` - Muestra preview del archivo
- ✅ `removeArchivoReconsideracion()` - Remueve archivo seleccionado
- ✅ `formatFileSize()` - Formatea tamaño de archivo

### 3. **Validaciones Implementadas**

#### Frontend
- ✅ Solo archivos PDF (.pdf)
- ✅ Tamaño máximo 10MB
- ✅ Drag & drop funcional
- ✅ Preview visual del archivo

#### Backend
- ✅ Validación de extensión PDF
- ✅ Validación de tamaño máximo (10MB)
- ✅ Manejo de errores con mensajes descriptivos

## Flujo de Usuario

1. **Usuario abre modal de reconsideración**
2. **Selecciona cotización diferente** (si aplica)
3. **Arrastra archivo PDF o hace click para seleccionar**
4. **Ve preview del archivo seleccionado**
5. **Puede remover archivo si cambia de opinión**
6. **Envía reconsideración** - el archivo se incluye automáticamente

## Tecnologías Utilizadas

- **Backend**: Django FileField, FormData handling
- **Frontend**: Vanilla JavaScript, Bootstrap 5 styling
- **Validación**: Cliente + Servidor
- **Storage**: Django default file storage

## Archivos Modificados

1. `workflow/modelsWorkflow.py` - Modelo ReconsideracionSolicitud
2. `workflow/views_reconsideraciones.py` - API solicitar reconsideración
3. `workflow/templates/workflow/partials/modalSolicitud.html` - Frontend completo
4. `workflow/migrations/0070_add_archivo_adjunto_reconsideracion.py` - Migración BD

## Estados del Upload

- **Initial**: Área de upload visible, sin archivo
- **Drag Over**: Área resaltada cuando se arrastra archivo
- **File Selected**: Preview visible, área de upload oculta
- **Uploading**: Incluido en FormData al enviar reconsideración

## Características Técnicas

- ✅ **Graceful degradation**: Funciona sin JS (upload básico)
- ✅ **Progressive enhancement**: Mejora UX con JS habilitado
- ✅ **Responsive**: Se adapta a diferentes tamaños de pantalla
- ✅ **Accessible**: Labels y ARIA attributes apropiados
- ✅ **Error handling**: Mensajes de error descriptivos

## Testing Recomendado

1. **Subir archivo PDF válido** - Debería mostrar preview y enviarse
2. **Intentar subir archivo no-PDF** - Debería mostrar error
3. **Intentar subir archivo > 10MB** - Debería mostrar error
4. **Drag & drop funcionalidad** - Debería funcionar igual que click
5. **Remover archivo** - Debería limpiar preview y input
6. **Enviar sin archivo** - Debería funcionar normalmente (opcional)

## Notas Importantes

- El archivo se guarda en `media/reconsideraciones/`
- Es completamente opcional - las reconsideraciones funcionan sin archivo
- Compatible con la funcionalidad existente de selección de cotizaciones
- Mantiene toda la lógica previa intacta

---

**Status**: ✅ **IMPLEMENTACIÓN COMPLETA** - Lista para testing y deployment
