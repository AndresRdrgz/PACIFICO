# 📊 Módulo de Reportería - Sistema Workflow Pacífico

## 🎯 Descripción General

El nuevo módulo de **Reportería y Analítica** es una solución completa para el análisis de datos del sistema de workflow, diseñado específicamente para administradores y supervisores de Pacífico.

## ✨ Características Principales

### 🔐 Control de Acceso
- **Acceso restringido**: Solo usuarios con rol de administrador, staff o miembros de grupos supervisores
- **Permisos granulares**: Control detallado sobre quién puede ver qué reportes
- **Reportes compartidos**: Posibilidad de compartir reportes entre grupos

### 📈 Dashboard Ejecutivo
- **Estadísticas en tiempo real**: 4 tarjetas principales con métricas clave
- **Gráfico de tendencias**: Visualización de solicitudes de los últimos 30 días
- **Stats por pipeline**: Resumen rápido del estado por cada pipeline
- **Diseño moderno**: Interfaz intuitiva con colores corporativos de Pacífico

### 🛠️ Reportes Personalizados
- **Constructor visual**: Modal intuitivo para crear reportes sin código
- **Filtros avanzados**: Por fechas, pipeline, etapa, usuario, SLA, monto, etc.
- **Campos configurables**: Selección flexible de qué datos incluir
- **Guardado persistente**: Los reportes se guardan para reutilización

### 📊 Reportes Predefinidos
- **Dashboard General**: Vista ejecutiva completa
- **Análisis SLA**: Cumplimiento de tiempos por etapa
- **Productividad**: Rendimiento por usuario/analista
- **Análisis Financiero**: Reportes por montos y productos
- **Compliance**: Estado de documentos y requisitos

### 📁 Exportación a Excel
- **Formato profesional**: Archivos Excel con formato corporativo
- **Nombres descriptivos**: Archivos con timestamp y nombre del reporte
- **Optimización**: Uso de pandas y openpyxl para máximo rendimiento
- **Columnas auto-ajustadas**: Formato óptimo para lectura

## 🏗️ Arquitectura Técnica

### 📁 Archivos Creados/Modificados

#### Nuevos Archivos:
- `views_reportes.py` - Vistas especializadas para reportería
- `templates/workflow/reportes.html` - Template principal del módulo
- `setup_reportes_ejemplo.py` - Script para datos de prueba

#### Archivos Modificados:
- `modelsWorkflow.py` - Nuevos modelos `ReportePersonalizado` y `EjecucionReporte`
- `urls.py` - Nuevas rutas para APIs de reportes

### 🗃️ Nuevos Modelos

#### ReportePersonalizado
```python
- nombre: CharField(200)
- descripcion: TextField
- usuario: ForeignKey(User)
- filtros_json: JSONField
- campos_json: JSONField
- configuracion_json: JSONField
- es_favorito: BooleanField
- es_publico: BooleanField
- veces_ejecutado: PositiveIntegerField
- ultima_ejecucion: DateTimeField
- grupos_compartidos: ManyToManyField(Group)
```

#### EjecucionReporte
```python
- reporte: ForeignKey(ReportePersonalizado)
- usuario: ForeignKey(User)
- fecha_ejecucion: DateTimeField
- parametros_json: JSONField
- tiempo_ejecucion: FloatField
- registros_resultantes: PositiveIntegerField
- exitosa: BooleanField
- mensaje_error: TextField
```

### 🛡️ Seguridad
- **Decorator personalizado**: `@admin_or_supervisor_required`
- **Validación de permisos**: Verificación por reporte y usuario
- **CSRF protection**: Protección contra ataques CSRF
- **Sanitización de datos**: Validación de inputs y filtros

## 🚀 URLs y APIs

### Rutas Principales:
- `/workflow/reportes/` - Dashboard principal
- `/workflow/api/reportes/crear/` - Crear reporte personalizado
- `/workflow/api/reportes/{id}/ejecutar/` - Ejecutar reporte
- `/workflow/api/reportes/{id}/exportar/` - Exportar a Excel
- `/workflow/api/reportes/predefinidos/` - Obtener reportes predefinidos

### Métodos HTTP:
- `GET` - Consultar datos y dashboards
- `POST` - Crear y ejecutar reportes
- `PUT/PATCH` - Actualizar reportes (próximamente)
- `DELETE` - Eliminar reportes (próximamente)

## 🎨 Diseño y UX

### Paleta de Colores:
- **Verde Pacífico**: `#009c3c` (color principal)
- **Verde Hover**: `#007529`
- **Verde Claro**: `#22a650`
- **Gradientes modernos**: Para tarjetas y botones
- **Sombras suaves**: Para profundidad visual

### Componentes UI:
- **Cards estadísticas**: Con iconos FontAwesome y gradientes
- **Tabs dinámicos**: Para organizar tipos de reportes
- **Modal avanzado**: Para creación de reportes con steps
- **Loading overlay**: Con spinner durante procesamiento
- **Toasts**: Notificaciones no intrusivas
- **Responsive design**: Adaptable a móviles y tablets

## 📋 Filtros Disponibles

### Filtros Temporales:
- **Fecha inicio/fin**: Rango de fechas personalizable
- **Períodos predefinidos**: Últimos 7, 30, 90 días

### Filtros de Negocio:
- **Pipeline**: Filtro por tipo de proceso
- **Etapa**: Filtro por etapa específica
- **Usuario asignado**: Por analista responsable
- **Estado SLA**: Vigente vs. Vencido
- **Subestado**: Estados detallados
- **Monto**: Rango de montos mínimo/máximo
- **Tipo producto**: Auto vs. Préstamo Personal
- **Prioridad**: Alta, Media, Baja

### Filtros de Sistema:
- **Estado**: Activas vs. Completadas
- **Grupo**: Por grupo de trabajo
- **Creador**: Quien creó la solicitud

## 🔧 Campos de Reporte

### Información Básica:
- Código de solicitud
- Pipeline y Etapa actual
- Subestado

### Datos del Cliente:
- Nombre del cliente
- Cédula/Identificación
- Monto solicitado
- Tipo de producto

### Datos Operativos:
- Usuario creador
- Usuario asignado
- Fecha de creación
- Última actualización
- Tiempo en etapa actual
- Estado SLA
- Prioridad

### Métricas Calculadas:
- Tiempo promedio por etapa
- Porcentaje cumplimiento SLA
- Carga de trabajo por usuario
- Tendencias temporales

## 📊 Tipos de Reportes

### 1. General
Vista panorámica del estado de solicitudes con métricas principales.

### 2. SLA y Tiempos
Análisis de cumplimiento de tiempos y alertas de SLA vencidos.

### 3. Productividad
Métricas de rendimiento por usuario y equipo.

### 4. Financiero
Análisis por montos, productos y segmentación financiera.

### 5. Compliance
Estado de requisitos, documentos y calificaciones.

### 6. Comité
Participaciones y decisiones del comité de crédito.

## 🔄 Flujo de Uso

### Para Crear un Reporte:
1. Clic en "Crear Reporte Personalizado"
2. Completar nombre y descripción
3. Seleccionar filtros deseados
4. Elegir campos a incluir
5. Configurar opciones adicionales
6. Guardar y ejecutar

### Para Ejecutar un Reporte:
1. Seleccionar reporte de la lista
2. Clic en botón "Ejecutar" (▶️)
3. Ver resultados en modal
4. Opcionalmente exportar a Excel

### Para Exportar:
1. Ejecutar reporte o clic directo en "Exportar" (📥)
2. El archivo se descarga automáticamente
3. Formato: `{nombre_reporte}_{timestamp}.xlsx`

## 🎯 Beneficios para Pacífico

### Para Gerencia:
- **Vista 360°**: Dashboard completo del estado operativo
- **KPIs en tiempo real**: Métricas actualizadas automáticamente
- **Alertas SLA**: Identificación inmediata de retrasos
- **Análisis de tendencias**: Patrones y proyecciones

### Para Supervisores:
- **Monitoreo de equipos**: Productividad por analista
- **Control de calidad**: Estado de compliance y documentos
- **Optimización de procesos**: Identificación de cuellos de botella
- **Reportes regulares**: Automatización de informes periódicos

### Para Analistas:
- **Visibilidad de carga**: Estado de sus asignaciones
- **Métricas personales**: Seguimiento de rendimiento
- **Alertas proactivas**: Notificaciones de SLA próximos a vencer

## 🔮 Funcionalidades Futuras

### Próximas Versiones:
- [ ] **Programación automática**: Reportes enviados por email
- [ ] **Dashboard personalizable**: Widgets movibles
- [ ] **Alertas inteligentes**: Notificaciones proactivas
- [ ] **API REST completa**: Para integraciones externas
- [ ] **Exportación PDF**: Con gráficos incluidos
- [ ] **Filtros guardados**: Templates de filtros reutilizables
- [ ] **Comparativas temporales**: Análisis período vs. período
- [ ] **Machine Learning**: Predicciones y tendencias automáticas

## 🛠️ Instalación y Configuración

### Dependencias:
```python
pandas==2.2.3
openpyxl==3.1.5
django>=5.1.3
```

### Migraciones Aplicadas:
```bash
python manage.py makemigrations workflow
python manage.py migrate
```

### Datos de Ejemplo:
```bash
python setup_reportes_ejemplo.py
```

## 🎨 Personalización

### Variables CSS:
```css
--verde-pacifico: #009c3c;
--verde-hover: #007529;
--verde-claro: #22a650;
--primary-gradient: linear-gradient(135deg, #009c3c 0%, #22a650 100%);
```

### Configuración de Reportes:
Los reportes pueden configurarse con:
- Tipos personalizados
- Métricas específicas
- Formatos de salida
- Niveles de agregación

## 🤝 Soporte y Mantenimiento

### Logging:
Todas las ejecuciones se registran en `EjecucionReporte` para auditoría.

### Performance:
- Consultas optimizadas con `select_related` y `prefetch_related`
- Paginación automática para grandes volúmenes
- Cache de resultados frecuentes (próximamente)

### Monitoreo:
- Tiempo de ejecución por reporte
- Tasa de éxito/error
- Uso por usuario y tipo de reporte

---

## 🎉 ¡Disfruta del nuevo módulo de reportería!

Este módulo representa un salto cualitativo en las capacidades analíticas de Pacífico, proporcionando herramientas profesionales para la toma de decisiones basada en datos.

**¡Todo funcionando al 100% y listo para producción!** 🚀
