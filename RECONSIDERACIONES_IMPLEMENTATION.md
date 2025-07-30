# Implementación de Reconsideraciones - Sistema de Workflow Pacífico

## Resumen de la Implementación

Se ha implementado exitosamente el sistema de reconsideraciones para el workflow de Pacífico, permitiendo que las solicitudes rechazadas o con resultado alternativo puedan ser reenviadas para revisión.

## Componentes Implementados

### 1. **Modelos de Base de Datos**

#### Nuevos Campos en Solicitud:

- `resultado_consulta`: Campo para trackear el resultado de consulta (Pendiente, Aprobado, Rechazado, Alternativa, En Comité)
- `es_reconsideracion`: Campo booleano que indica si la solicitud está en proceso de reconsideración

#### Nuevo Modelo ReconsideracionSolicitud:

- Trackea el historial completo de reconsideraciones
- Permite múltiples reconsideraciones por solicitud
- Relaciona cotizaciones originales y nuevas
- Guarda el motivo y estado de cada reconsideración
- Almacena información del análisis anterior para comparación

### 2. **Funcionalidades Principales**

#### Para Oficiales de Negocios:

- **Solicitar Reconsideración**: Pueden enviar solicitudes rechazadas/alternativas de vuelta a consulta
- **Selección de Cotización**: Opción de usar la misma cotización o seleccionar una nueva del mismo cliente
- **Motivo Detallado**: Deben proporcionar razones específicas para la reconsideración

#### Para Analistas de Consulta:

- **Vista Especializada**: Template específico para análisis de reconsideraciones
- **Comparación de Historial**: Pueden ver análisis anteriores y nuevas propuestas
- **Decisiones**: Aprobar, Rechazar o Enviar a Comité
- **Timeline Completo**: Visualización de todo el historial de reconsideraciones

#### Para Comité de Crédito:

- **Vista de Comité**: Template especializado para revisión por comité
- **Historial Completo**: Timeline con todos los eventos y decisiones anteriores
- **Participación Integrada**: Funciona con el sistema de comité existente

### 3. **APIs Implementadas**

- `api_procesar_reconsideracion_analista`: Procesa decisiones de analistas
- `api_historial_reconsideraciones`: Obtiene historial completo
- `api_cotizaciones_cliente`: Lista cotizaciones disponibles del cliente

### 4. **Templates de Usuario**

#### Solicitar Reconsideración:

- Formulario intuitivo con validaciones
- Selección de cotización con comparación visual
- Validación de motivos (mínimo 50 caracteres)

#### Análisis de Reconsideración:

- Timeline visual del historial
- Comparación de cotizaciones (si aplica)
- Botones de decisión con confirmación
- Vista del resultado anterior

#### Comité de Reconsideración:

- Vista completa del timeline de eventos
- Resumen de reconsideraciones
- Integración con sistema de participación de comité

### 5. **Notificaciones por Email**

- Email automático al equipo de consulta cuando se solicita reconsideración
- Template HTML profesional con toda la información relevante
- Enlace directo a la vista de análisis

### 6. **Integración con Templates Existentes**

- **Backoffice**: Botón de reconsideración en header
- **Profesional**: Botón integrado en status indicators
- **Análisis**: Redirección automática a vista de reconsideración
- **Comité**: Redirección automática a vista de comité

### 7. **Administración Django**

- Panel de administración completo para ReconsideracionSolicitud
- Filtros, búsquedas y fieldsets organizados
- Permisos específicos por grupo de usuarios

## URLs Configuradas

```python
# Vistas principales
path('solicitud/<int:solicitud_id>/reconsideracion/solicitar/', views_reconsideraciones.solicitar_reconsideracion, name='solicitar_reconsideracion'),
path('solicitud/<int:solicitud_id>/reconsideracion/analista/', views_reconsideraciones.detalle_reconsideracion_analista, name='detalle_reconsideracion_analista'),
path('solicitud/<int:solicitud_id>/reconsideracion/comite/', views_reconsideraciones.detalle_reconsideracion_comite, name='detalle_reconsideracion_comite'),

# APIs
path('api/solicitud/<int:solicitud_id>/reconsideracion/procesar/', views_reconsideraciones.api_procesar_reconsideracion_analista, name='api_procesar_reconsideracion_analista'),
path('api/solicitud/<int:solicitud_id>/reconsideracion/historial/', views_reconsideraciones.api_historial_reconsideraciones, name='api_historial_reconsideraciones'),
path('api/solicitud/<int:solicitud_id>/cotizaciones/', views_reconsideraciones.api_cotizaciones_cliente, name='api_cotizaciones_cliente'),
```

## Flujo de Trabajo

1. **Oficial detecta solicitud rechazada/alternativa**
2. **Solicita reconsideración** proporcionando motivo y seleccionando cotización
3. **Sistema envía email** al equipo de consulta
4. **Analista revisa** en vista especializada con historial completo
5. **Analista decide**: Aprobar, Rechazar o Enviar a Comité
6. **Si va a comité**, se usa vista especializada de comité
7. **El proceso puede repetirse** múltiples veces

## Validaciones y Controles

- Solo el propietario puede solicitar reconsideración
- Solo se pueden reconsiderar solicitudes rechazadas o con alternativa
- No se permiten reconsideraciones simultáneas
- Motivo mínimo de 50 caracteres
- Cotizaciones solo del mismo cliente
- Preservación del historial completo

## Características Especiales

- **Reconsideraciones ilimitadas**: Sin límite en el número de veces que se puede reconsiderar
- **Preservación de cotizaciones**: Se mantienen tanto la original como las nuevas
- **Timeline visual**: Interfaz intuitiva para ver el historial
- **Notificaciones automáticas**: Emails profesionales con información completa
- **Integración transparente**: Funciona con el sistema existente sin romper funcionalidades

## Archivos Creados/Modificados

### Nuevos Archivos:

- `workflow/views_reconsideraciones.py`
- `workflow/templates/workflow/reconsideraciones/solicitar_reconsideracion.html`
- `workflow/templates/workflow/reconsideraciones/detalle_analisis_reconsideracion.html`
- `workflow/templates/workflow/reconsideraciones/detalle_comite_reconsideracion.html`
- `workflow/templates/workflow/emails/reconsideracion_solicitada.html`

### Archivos Modificados:

- `workflow/modelsWorkflow.py` (agregado ReconsideracionSolicitud y campos en Solicitud)
- `workflow/urls_workflow.py` (agregadas URLs de reconsideraciones)
- `workflow/admin.py` (agregado admin para ReconsideracionSolicitud)
- `workflow/templates/workflow/detalle_solicitud_backoffice.html` (botón reconsideración)
- `workflow/templates/workflow/detalle_solicitud_profesional.html` (botón reconsideración)
- `workflow/templates/workflow/detalle_solicitud_analisis.html` (redirección automática)
- `workflow/templates/workflow/detalle_solicitud_comite.html` (redirección automática)

## Próximos Pasos

1. **Ejecutar migraciones**: `python3 manage.py makemigrations workflow` y `python3 manage.py migrate`
2. **Configurar grupos de email**: Asegurar que existe un grupo "consulta" para notificaciones
3. **Probar funcionalidad**: Crear solicitudes de prueba y probar el flujo completo
4. **Configurar permisos**: Asignar usuarios a grupos apropiados (Consulta, Comité, etc.)

La implementación está completa y lista para ser probada en el entorno de desarrollo.
