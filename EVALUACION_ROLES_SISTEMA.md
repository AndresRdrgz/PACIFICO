# Evaluación de Roles en el Sistema de Capacitaciones PACÍFICO

## Resumen Ejecutivo de Roles Identificados

Basado en el análisis del código fuente, el sistema de capacitaciones PACÍFICO maneja **3 roles principales** con diferentes niveles de acceso y funcionalidades.

## Roles Principales Identificados

### 1. **Usuario Regular (Usuario Estándar)**
- **Identificador**: `user.is_authenticated = True`, `user.is_staff = False`, `user.is_superuser = False`
- **Permisos**:
  - ✅ Acceso a cursos asignados personalmente
  - ✅ Acceso a cursos asignados por grupos
  - ✅ Visualización de progreso personal
  - ✅ Realización de quizzes y temas
  - ✅ Descarga de certificados
  - ✅ Evaluación de satisfacción
  - ❌ Sin acceso a funciones administrativas

### 2. **Administrador de Capacitaciones (Staff)**
- **Identificador**: `user.is_staff = True`
- **Permisos**:
  - ✅ Todas las funciones de Usuario Regular
  - ✅ Acceso al panel de asignación de cursos
  - ✅ Gestión de asignaciones usuario-curso
  - ✅ Gestión de grupos de usuarios
  - ✅ Visualización de reportes y estadísticas
  - ✅ Gestión masiva de asignaciones
  - ✅ Acceso al historial completo de asignaciones
  - ❌ Sin acceso completo al admin de Django

### 3. **Superadministrador (Superuser)**
- **Identificador**: `user.is_superuser = True`
- **Permisos**:
  - ✅ Todas las funciones de los roles anteriores
  - ✅ Acceso completo al admin de Django
  - ✅ Gestión completa de usuarios y permisos
  - ✅ Acceso a todas las configuraciones del sistema
  - ✅ Acceso a funciones especiales del sistema principal PACÍFICO

## Análisis Detallado por Archivos

### Decoradores de Autenticación Utilizados

#### `@login_required`
- **Uso**: 37+ instancias
- **Propósito**: Garantizar que el usuario esté autenticado
- **Aplicado en**: Todas las vistas principales

#### `@user_passes_test(lambda u: u.is_staff)`
- **Uso**: 11 instancias
- **Propósito**: Restringir acceso solo a usuarios staff
- **Aplicado en**: Vistas administrativas de capacitaciones

#### `@user_passes_test(lambda u: u.is_superuser)`
- **Uso**: 4 instancias
- **Propósito**: Acceso exclusivo para superusuarios
- **Aplicado en**: Funciones críticas del sistema principal

### Verificaciones Condicionales en Templates

#### `{% if user.is_staff %}`
- **Uso**: 11 instancias en templates
- **Propósito**: Mostrar elementos UI solo para staff
- **Contexto**: Menús, botones, indicadores especiales

#### `{% if user.is_superuser %}`
- **Uso**: 6 instancias en templates
- **Propósito**: Elementos exclusivos para superusuarios
- **Contexto**: Configuraciones avanzadas, herramientas especiales

### Lógica de Negocio por Roles

#### En `views_cursos.py`
```python
if not usuario.is_superuser:
    cursos = cursos.filter(Q(usuarios_asignados=usuario) | Q(grupos_asignados__usuarios_asignados=usuario))
```
- Los superusuarios ven todos los cursos
- Usuarios regulares solo ven cursos asignados

#### En `views_asignacion.py`
- Todas las vistas administrativas requieren `is_staff = True`
- Control granular de asignaciones y gestión de usuarios

## Grupos de Usuario de Django

**Nota importante**: El sistema **NO utiliza** los grupos nativos de Django (`django.contrib.auth.models.Group`) para control de permisos. En su lugar, utiliza un modelo personalizado `GrupoAsignacion` que sirve únicamente para agrupar usuarios para asignaciones masivas de cursos.

### Modelo `GrupoAsignacion`
- **Propósito**: Agrupar usuarios para asignaciones de cursos
- **No es**: Un sistema de permisos
- **Uso**: Facilitar asignaciones masivas por departamento/área

## Flujo de Permisos por Funcionalidad

### 📚 **Gestión de Cursos**
- **Ver cursos**: Usuario Regular + filtro por asignación
- **Ver todos los cursos**: Superusuario
- **Asignar cursos**: Staff

### 👥 **Gestión de Usuarios**
- **Ver perfil propio**: Usuario Regular
- **Gestionar asignaciones**: Staff
- **Administrar usuarios**: Superusuario

### 📊 **Reportes y Estadísticas**
- **Ver progreso personal**: Usuario Regular
- **Ver estadísticas generales**: Staff
- **Acceso completo a datos**: Superusuario

### 🛠️ **Administración**
- **Panel de capacitaciones**: Staff
- **Admin de Django**: Superusuario
- **Configuraciones del sistema**: Superusuario

## Recomendaciones

### ✅ **Aspectos Positivos**
1. **Jerarquía clara**: 3 niveles bien definidos
2. **Seguridad robusta**: Doble verificación en vistas y templates
3. **Separación de responsabilidades**: Cada rol tiene funciones específicas

### 🔄 **Posibles Mejoras**
1. **Grupos de Django**: Considerar implementar grupos nativos para mayor flexibilidad
2. **Permisos granulares**: Implementar permisos específicos por módulo
3. **Roles intermedios**: Considerar roles como "Instructor" o "Coordinador"

## Conclusión

El sistema maneja **3 roles principales** de manera efectiva:
- **Usuario Regular** (empleados)
- **Staff** (administradores de capacitaciones)
- **Superusuario** (administradores del sistema)

La implementación es sólida y sigue buenas prácticas de seguridad, aunque podría beneficiarse de una mayor granularidad en permisos específicos.

**Fecha de Análisis**: Junio 22, 2025
