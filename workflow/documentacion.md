# 🧠 Sistema de Gestión de Solicitudes con Flujos y Campos Dinámicos

Este sistema permite gestionar solicitudes en flujos personalizados, donde cada solicitud pertenece a un pipeline que define etapas, subestados, requisitos y campos configurables. Incluye manejo de bandejas grupales, permisos, y transiciones explícitas.

---

## ✅ Requerimientos Funcionales

### 1. **Gestión de Pipelines y Etapas**
- Cada **pipeline** define un flujo de etapas.
- Cada **etapa** tiene un orden (`orden`), un tiempo máximo de respuesta (`sla`) y puede ser:
  - **Bandeja grupal**: solicitudes visibles para todos los usuarios del grupo.
  - **Bandeja personal**: solicitud asignada a un único usuario.
- Las etapas pueden tener **subestados** definidos (ej. "Pendiente por asignar", "En revisión").

### 2. **Transiciones Explícitas**
- Desde cada etapa se definen **transiciones permitidas** hacia otras etapas del pipeline.
- Cada transición tiene un nombre visible (ej. "Aprobar", "Rechazar", "Solicitar Alternativa").
- Opcionalmente puede requerir permisos específicos del usuario.

### 3. **Permisos por Etapa**
- Cada etapa puede ser vista y/o asignada únicamente por ciertos **grupos de usuarios** (`django.contrib.auth.Group`).
- Esto permite construir bandejas por rol (Ej. Comité, Trámite, Legal).

### 4. **Bandejas de Trabajo**
- Las solicitudes se muestran en:
  - **Bandeja grupal**: si están en etapa grupal y sin asignación.
  - **Bandeja personal**: si están asignadas a un usuario específico.
- Un usuario puede **auto-asignarse** solicitudes en etapas grupales.

### 5. **Requisitos por Pipeline y Tipo de Solicitud**
- Cada combinación de **pipeline + tipo de solicitud** tiene un conjunto de **requisitos definidos** (ej. "Cédula", "Ficha CSS", "Cotización").
- Al crear una solicitud, se generan automáticamente los requisitos correspondientes.
- Los usuarios pueden subir archivos y marcar cada requisito como "cumplido".

### 6. **Campos Dinámicos Configurables**
- El administrador puede definir **campos personalizados** (texto, número, fecha, booleano, entero) para cada pipeline.
- Estos campos son visibles y requeridos al momento de llenar una solicitud de ese pipeline.
- Los valores de esos campos se guardan dinámicamente, sin necesidad de migraciones.

### 7. **Historial de Etapas**
- Cada movimiento entre etapas genera un registro de historial con:
  - Etapa anterior y nueva
  - Subestado (si aplica)
  - Usuario responsable
  - Fecha de entrada y salida
  - Validación automática de cumplimiento de SLA

---

## 🧩 Modelo de Solicitud

- Cada **solicitud** tiene:
  - Código único
  - Tipo de solicitud
  - Pipeline al que pertenece
  - Etapa actual y subestado
  - Usuario que la creó
  - Usuario asignado (si aplica)
  - Fecha de creación y última actualización

---

## 🚦 Validaciones y Reglas del Flujo

- **No se puede avanzar** una solicitud si no se cumplen:
  - Todos los requisitos obligatorios definidos para su pipeline/tipo
  - Todos los campos dinámicos requeridos
- Solo se permiten transiciones válidas definidas explícitamente.
- Solo usuarios con permisos para la etapa pueden ver o tomar una solicitud.

---

## ⚙️ Administración

- Los administradores pueden:
  - Crear y configurar pipelines
  - Definir etapas y su orden
  - Asignar grupos con acceso a cada etapa
  - Crear subestados
  - Configurar transiciones válidas
  - Crear requisitos para tipos de solicitud y pipelines
  - Definir campos personalizados sin modificar el modelo base

---

## 📁 Archivos generados por el sistema

- Archivos adjuntos a requisitos (`/media/requisitos/`)
- Registro automático de cada transición en el historial
- Datos de campos personalizados por solicitud en `ValorCampoSolicitud`

---

## 📌 Pendientes sugeridos (fuera de este modelo)

- Formularios dinámicos en el frontend (Django, DRF o React)
- Panel de administración avanzada para configuración visual de pipelines
- Exportación de historial de etapas
- Reporte de SLA vencidos

---

