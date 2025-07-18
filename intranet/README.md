# Aplicación Intranet - Sistema de Reservas de Salas

## Descripción

La aplicación **Intranet** es un sistema completo de gestión de reservas de salas de trabajo para la Financiera Pacífico. Permite a los usuarios reservar salas, invitar participantes, gestionar conflictos de horarios y recibir notificaciones por email.

## Características Principales

### 🏢 Gestión de Salas
- **Creación y administración de salas** con información detallada
- **Fotos de referencia** para cada sala
- **Estados de sala**: Activa, Inactiva, En Mantenimiento
- **Información de equipamiento** disponible
- **Capacidad y ubicación** de cada sala

### 📅 Sistema de Reservas
- **Calendario interactivo** con FullCalendar.js
- **Reservas con validación** de conflictos de horario
- **Duración flexible** de las reuniones
- **Descripción y detalles** de cada reserva
- **Estados de reserva**: Activa, Cancelada, Completada

### 👥 Gestión de Participantes
- **Invitaciones por email** automáticas
- **Confirmación/declinación** de asistencia
- **Estados de participación**: Pendiente, Confirmado, Declinado, Asistió, No Asistió
- **Notificaciones** de cambios y cancelaciones

### 📧 Sistema de Notificaciones
- **Emails automáticos** para invitaciones
- **Notificaciones de cancelación**
- **Plantillas HTML y texto plano**
- **Tracking de envíos** y errores

### 🎨 Interfaz de Usuario
- **Diseño responsive** con Tailwind CSS
- **Funcional en móviles y escritorio**
- **Navegación intuitiva**
- **Modales y confirmaciones**
- **Indicadores visuales** de estados

## Estructura del Proyecto

```
intranet/
├── models.py              # Modelos de base de datos
├── views.py               # Vistas principales
├── api.py                 # Endpoints API
├── admin.py               # Configuración del admin
├── urls.py                # URLs de la aplicación
├── templates/
│   └── intranet/
│       ├── base.html              # Plantilla base
│       ├── dashboard.html         # Dashboard principal
│       ├── calendario.html        # Vista de calendario
│       ├── nueva_reserva.html     # Formulario de nueva reserva
│       ├── mis_reservas.html      # Lista de reservas del usuario
│       ├── detalle_reserva.html   # Detalles de una reserva
│       ├── gestion_salas.html     # Gestión de salas (admin)
│       └── emails/
│           ├── invitacion.html    # Email de invitación (HTML)
│           ├── invitacion.txt     # Email de invitación (texto)
│           ├── cancelacion.html   # Email de cancelación (HTML)
│           └── cancelacion.txt    # Email de cancelación (texto)
└── README.md              # Esta documentación
```

## Modelos de Base de Datos

### Sala
```python
class Sala(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=200)
    capacidad = models.PositiveIntegerField()
    foto = models.ImageField(upload_to='intranet/salas/')
    estado = models.CharField(choices=ESTADO_CHOICES, default='activa')
    descripcion = models.TextField(blank=True)
    equipamiento = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Reserva
```python
class Reserva(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    usuario_creador = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    estado = models.CharField(choices=ESTADO_CHOICES, default='activa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Participante
```python
class Participante(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estado_asistencia = models.CharField(choices=ESTADO_CHOICES, default='pendiente')
    fecha_invitacion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
```

### Notificacion
```python
class Notificacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    tipo = models.CharField(choices=TIPO_CHOICES)
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE)
    email_enviado = models.EmailField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(choices=ESTADO_CHOICES, default='pendiente')
    error_mensaje = models.TextField(blank=True)
```

## URLs Disponibles

### Vistas Principales
- `/intranet/` - Dashboard principal
- `/intranet/calendario/` - Calendario de reservas
- `/intranet/nueva-reserva/` - Crear nueva reserva
- `/intranet/mis-reservas/` - Mis reservas y participaciones
- `/intranet/reserva/<id>/` - Detalles de una reserva
- `/intranet/gestion-salas/` - Gestión de salas (solo admin)

### Endpoints API
- `/intranet/api/salas/` - Obtener salas disponibles
- `/intranet/api/reservas/` - Obtener reservas
- `/intranet/api/reservas/crear/` - Crear nueva reserva
- `/intranet/api/reservas/cancelar/` - Cancelar reserva
- `/intranet/api/reservas/confirmar-asistencia/` - Confirmar/declinar asistencia
- `/intranet/api/usuarios/` - Obtener usuarios disponibles

## Configuración de Email

La aplicación utiliza la configuración de email existente en `settings.py`:

```python
EMAIL_BACKEND = 'workflow.email_backend.CustomSMTPEmailBackend'
EMAIL_HOST = 'mail.fpacifico.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'makito@fpacifico.com'
EMAIL_HOST_PASSWORD = 'aFihr73B'
DEFAULT_FROM_EMAIL = 'workflow@fpacifico.com'
```

## Funcionalidades por Rol

### Usuario Regular
- Ver calendario de reservas
- Crear nuevas reservas
- Invitar participantes
- Confirmar/declinar invitaciones
- Ver detalles de reservas
- Cancelar sus propias reservas

### Administrador
- Todas las funcionalidades de usuario regular
- Gestión completa de salas
- Ver todas las reservas
- Acceso al panel de administración de Django

## Tecnologías Utilizadas

### Backend
- **Django 4.x** - Framework web
- **SQLite/PostgreSQL** - Base de datos
- **Django Admin** - Panel de administración

### Frontend
- **Tailwind CSS** - Framework de estilos
- **FullCalendar.js** - Calendario interactivo
- **Font Awesome** - Iconos
- **JavaScript ES6+** - Funcionalidad interactiva

### Email
- **Django Email Backend** - Envío de emails
- **Plantillas HTML y texto plano** - Formato de emails

## Instalación y Configuración

### 1. Migraciones
```bash
python manage.py makemigrations intranet
python manage.py migrate
```

### 2. Crear Superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 3. Crear Salas Iniciales
Acceder al admin de Django (`/admin/`) y crear las salas necesarias.

### 4. Configurar Permisos
Los usuarios necesitan estar autenticados para acceder a la aplicación.

## Uso de la Aplicación

### Crear una Nueva Reserva
1. Ir a "Nueva Reserva"
2. Seleccionar sala
3. Elegir fecha y hora
4. Agregar título y descripción
5. Invitar participantes
6. Confirmar la reserva

### Ver Calendario
1. Ir a "Calendario"
2. Usar filtros para buscar reservas específicas
3. Hacer clic en eventos para ver detalles
4. Seleccionar fechas para crear nuevas reservas

### Gestionar Participaciones
1. Ir a "Mis Reservas"
2. Ver reservas creadas y participaciones
3. Confirmar o declinar invitaciones
4. Cancelar reservas propias

## Validaciones y Reglas de Negocio

### Reservas
- No se pueden crear reservas en el pasado
- La fecha de fin debe ser posterior a la de inicio
- No se pueden crear reservas que se solapen con otras existentes
- Solo el creador puede cancelar una reserva

### Salas
- Solo las salas activas aparecen en las opciones de reserva
- Las salas en mantenimiento muestran mensaje especial
- Las salas inactivas no son visibles para reservas

### Participantes
- El creador de la reserva es automáticamente participante
- Los participantes pueden confirmar o declinar asistencia
- Se envían notificaciones automáticas por email

## Mantenimiento y Soporte

### Logs
Los errores de email se registran en el modelo `Notificacion` con el campo `error_mensaje`.

### Backup
Se recomienda hacer backup regular de la base de datos, especialmente de las tablas:
- `intranet_sala`
- `intranet_reserva`
- `intranet_participante`
- `intranet_notificacion`

### Monitoreo
- Revisar regularmente las notificaciones fallidas
- Verificar el estado de las salas
- Monitorear el uso del sistema

## Personalización

### Colores y Estilos
Los colores se pueden personalizar modificando las clases de Tailwind CSS en las plantillas.

### Configuración de Email
Modificar las plantillas en `templates/intranet/emails/` para personalizar los emails.

### Horarios de Trabajo
Ajustar `slotMinTime` y `slotMaxTime` en el calendario para definir horarios de trabajo.

## Troubleshooting

### Problemas Comunes

1. **Emails no se envían**
   - Verificar configuración SMTP en settings.py
   - Revisar logs de error en modelo Notificacion

2. **Conflictos de horario no detectados**
   - Verificar zona horaria en settings.py
   - Revisar validaciones en modelo Reserva

3. **Calendario no carga**
   - Verificar conexión a internet para CDN de FullCalendar
   - Revisar consola del navegador para errores JavaScript

### Contacto
Para soporte técnico, contactar al equipo de desarrollo de Financiera Pacífico.

---

**Versión**: 1.0.0  
**Fecha**: Julio 2025  
**Desarrollado por**: Equipo de Desarrollo - Financiera Pacífico 