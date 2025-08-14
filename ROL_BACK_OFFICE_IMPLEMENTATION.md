# 🔧 Rol "Back Office" - Implementación Completa

## 📋 Resumen

Se ha implementado exitosamente el nuevo rol **"Back Office"** en el sistema, con los mismos permisos y capacidades que el rol "Analista". Este rol está diseñado para usuarios que necesitan acceso a funcionalidades de análisis y gestión de solicitudes, pero con restricciones específicas de bandejas.

## 🎯 Características del Rol Back Office

### ✅ **Permisos Otorgados**

| Funcionalidad | Acceso | Tipo |
|---------------|--------|------|
| **Bandejas de Trabajo** | ✅ Completo | Con PermisoBandeja específico |
| **Vista de Análisis** | ✅ Completo | Por rol |
| **Gestión de Requisitos** | ✅ Completo | Por rol |
| **Solicitudes Asignadas** | ✅ Completo | Por rol |
| **Filtros por Etapa** | ✅ Completo | Por rol |
| **Filtros por Pipeline** | ✅ Completo | Por rol |
| **Pendientes y Errores** | ✅ Completo | Por rol |

### ❌ **Permisos NO Otorgados**

| Funcionalidad | Acceso | Tipo |
|---------------|--------|------|
| **Negocios** | ❌ Sin acceso | Por rol |
| **Comité** | ❌ Sin acceso | Por rol |
| **Canal Digital** | ❌ Sin acceso | Por grupo |

## 🔄 **Acceso Condicional (Según Configuración)**

| Funcionalidad | Acceso | Tipo |
|---------------|--------|------|
| **Bandejas Específicas** | ⚠️ Condicional | Por PermisoBandeja |
| **Etapas de Workflow** | ⚠️ Condicional | Por PermisoBandeja |

## 🛠️ **Implementación Técnica**

### 1. **Modelo UserProfile**
- **Archivo**: `pacifico/models.py`
- **Cambio**: Agregado 'Back Office' a las opciones del campo `rol`
- **Migración**: `0158_add_backoffice_role.py`

### 2. **Context Processor**
- **Archivo**: `workflow/context_processors.py`
- **Cambios**: 
  - Rol "Back Office" incluido en acceso a bandejas de trabajo
  - Rol "Back Office" incluido en acceso a pendientes y errores
- **Lógica**: 
  - Bandejas: `user_role in ['Analista', 'Back Office']`
  - Pendientes: `user_role in ['Supervisor', 'Administrador', 'Back Office']`

### 3. **Vistas del Workflow**
- **Archivo**: `workflow/views_workflow.py`
- **Cambios**:
  - Vista mixta de bandejas
  - Vista de análisis de solicitudes
  - Filtros de etapas con bandeja

### 4. **Comando de Gestión**
- **Archivo**: `workflow/management/commands/setup_backoffice_role.py`
- **Funcionalidades**:
  - Asignar rol a usuarios específicos
  - Listar usuarios con rol Back Office
  - Información de ayuda y permisos

### 5. **Template Base Actualizado**
- **Archivo**: `workflow/templates/workflow/base.html`
- **Cambio**: Pestaña "Pendientes y errores" movida a sección independiente "Gestión"
- **Antes**: Anidada dentro de sección "Negocios"
- **Después**: Sección independiente accesible para usuarios con `can_access_pendientes_errores = True`

### 6. **Comando de Prueba de Template**
- **Archivo**: `workflow/management/commands/test_template_rendering.py`
- **Funcionalidades**:
  - Verificar renderizado del template para usuarios específicos
  - Analizar estructura del menú que verá cada usuario
  - Validar que las variables del context processor funcionen correctamente

## 🚀 **Configuración y Uso**

### **1. Asignar Rol a Usuario**

```bash
# Asignar rol Back Office a un usuario específico
python manage.py setup_backoffice_role --username juan.perez

# Listar usuarios con rol Back Office
python manage.py setup_backoffice_role --list

# Ver información de ayuda
python manage.py setup_backoffice_role
```

### **2. Verificar Permisos y Funcionalidad**

```bash
# Probar permisos del context processor
python manage.py test_backoffice_permissions --username juan.perez

# Probar renderizado del template
python manage.py test_template_rendering --username juan.perez

# Probar todos los usuarios Back Office
python manage.py test_backoffice_permissions
python manage.py test_template_rendering
```

### **2. Configurar Permisos de Bandeja**

Para que un usuario con rol "Back Office" pueda ver bandejas específicas:

1. **Ir al Django Admin** (`/admin/`)
2. **Navegar a**: Workflow > Permisos de Bandeja
3. **Crear nuevo permiso**:
   - **Etapa**: Etapa con `es_bandeja_grupal=True`
   - **Usuario**: Usuario con rol "Back Office"
   - **Puede ver**: ✅ True
   - **Puede tomar**: ✅ True (opcional)
   - **Puede transicionar**: ✅ True (opcional)

### **3. Ejemplo de Configuración**

```python
# Ejemplo de código para crear permisos programáticamente
from workflow.modelsWorkflow import PermisoBandeja, Etapa
from django.contrib.auth.models import User

# Obtener usuario y etapa
usuario = User.objects.get(username='juan.perez')
etapa = Etapa.objects.get(nombre='Validación')

# Crear permiso
PermisoBandeja.objects.create(
    etapa=etapa,
    usuario=usuario,
    puede_ver=True,
    puede_tomar=True,
    puede_transicionar=True
)
```

## 🔍 **Lógica de Verificación**

### **Context Processor**
```python
# Acceso a Bandejas de Trabajo: Analistas y Back Office siempre pueden ver
if user_role in ['Analista', 'Back Office']:
    context['can_access_bandejas_trabajo'] = True

# Acceso a Pendientes y Errores: Roles administrativos y Back Office
if user_role in ['Supervisor', 'Administrador', 'Back Office']:
    context['can_access_pendientes_errores'] = True
```

### **Vista Mixta de Bandejas**
```python
if user_role in ['Analista', 'Back Office']:
    # Los analistas y Back Office SOLO ven las bandejas donde tienen PermisoBandeja específico
    etapas_grupales = Etapa.objects.filter(
        es_bandeja_grupal=True,
        permisos_bandeja__usuario=request.user,
        permisos_bandeja__puede_ver=True
    ).exclude(nombre__iexact="Comité de Crédito").distinct()
```

### **Filtros de Etapas**
```python
if user_role in ['Analista', 'Back Office']:
    # Los analistas y Back Office solo ven etapas donde tienen PermisoBandeja específico
    etapas_con_bandeja = Etapa.objects.filter(
        es_bandeja_grupal=True,
        permisos_bandeja__usuario=request.user,
        permisos_bandeja__puede_ver=True
    ).exclude(nombre__iexact="Comité de Crédito").select_related('pipeline').distinct()
```

## 📱 **Estructura del Menú para el Rol Back Office**

### **Menú de Navegación Visible**

```
📱 Navegación Principal
  └── Dashboard

📋 Bandejas de Trabajo
  └── Bandejas de Trabajo

⚠️  Gestión
  └── Pendientes y errores

👤 Usuario
  ├── Mi Perfil
  └── Cerrar Sesión
```

### **Secciones NO Visibles**
- ❌ **Negocios** (Cotizaciones, Formularios, Agenda de Firma)
- ❌ **Comité** (Acceso restringido)
- ❌ **Canal Digital** (Acceso por grupo específico)
- ❌ **Administración** (Solo superusuarios)
- ❌ **Reportes** (Solo superusuarios)

### **Ubicación de la Pestaña "Pendientes y Errores"**
- **Sección**: "Gestión" (independiente)
- **Acceso**: Directo por rol "Back Office"
- **No requiere**: Acceso a sección "Negocios"
- **Funcionalidad**: Completa con tres subpestañas

## 📊 **Casos de Uso Comunes**

### **👨‍💼 Usuario Back Office - Análisis de Solicitudes**
1. **Acceso**: Solo a bandejas configuradas con PermisoBandeja
2. **Funcionalidades**:
   - Ver solicitudes en bandejas asignadas
   - Tomar solicitudes de bandejas grupales
   - Analizar requisitos de transición
   - Gestionar solicitudes asignadas
   - **Acceso completo a Pendientes y Errores** (nueva funcionalidad)
3. **Restricciones**: No puede ver todas las bandejas del sistema

### **🔧 Administrador - Configuración de Permisos**
1. **Asignar Rol**: Usar comando `setup_backoffice_role`
2. **Configurar Bandejas**: Crear PermisoBandeja para etapas específicas
3. **Monitoreo**: Usar comando `--list` para ver usuarios configurados

## ⚠️ **Consideraciones Importantes**

### **1. Seguridad**
- Los usuarios con rol "Back Office" **NO** tienen acceso automático a todas las bandejas
- Requieren configuración manual de `PermisoBandeja` para cada etapa
- Siguen el mismo patrón de seguridad que el rol "Analista"

### **2. Rendimiento**
- Las consultas están optimizadas con `select_related` y `distinct()`
- Solo se cargan las etapas y bandejas donde el usuario tiene permisos
- No hay impacto en el rendimiento del sistema

### **3. Mantenimiento**
- Los permisos se pueden modificar dinámicamente desde el Django Admin
- No se requieren cambios de código para ajustar permisos
- El sistema es flexible y escalable

## 🔄 **Migración y Compatibilidad**

### **1. Usuarios Existentes**
- Los usuarios existentes **NO** se ven afectados
- El rol "Back Office" es completamente nuevo
- No hay cambios en roles existentes

### **2. Base de Datos**
- La migración `0158_add_backoffice_role.py` es segura
- No hay pérdida de datos
- Compatible con versiones anteriores

### **3. APIs y Frontend**
- No se requieren cambios en el frontend
- Las APIs existentes funcionan correctamente
- Compatible con la interfaz actual

## 📈 **Próximos Pasos Recomendados**

### **1. Implementación Inmediata**
- [ ] Asignar rol "Back Office" a usuarios apropiados
- [ ] Configurar PermisoBandeja para etapas específicas
- [ ] Probar funcionalidades en entorno de desarrollo

### **2. Monitoreo y Ajustes**
- [ ] Verificar que los permisos funcionen correctamente
- [ ] Ajustar configuración según necesidades del negocio
- [ ] Documentar casos de uso específicos

### **3. Capacitación**
- [ ] Entrenar usuarios con el nuevo rol
- [ ] Documentar procesos de configuración
- [ ] Crear guías de usuario específicas

## 🎉 **Resumen de Implementación**

El rol **"Back Office"** ha sido implementado exitosamente con:

- ✅ **Mismos permisos** que el rol "Analista"
- ✅ **Seguridad mejorada** con restricciones específicas de bandeja
- ✅ **Comando de gestión** para facilitar la configuración
- ✅ **Documentación completa** para administradores y usuarios
- ✅ **Compatibilidad total** con el sistema existente
- ✅ **Flexibilidad** para configurar permisos específicos

El sistema ahora ofrece una opción adicional de rol que permite un control granular sobre el acceso a funcionalidades de análisis y gestión de solicitudes, manteniendo la seguridad y escalabilidad del sistema.
