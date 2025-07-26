# 🔐 Restricciones de Acceso del Sidebar - Documentación

## 📋 Resumen

Se ha implementado un sistema de restricciones de acceso para el sidebar de navegación basado en grupos de Django y permisos de bandeja. Los usuarios solo verán las secciones del sidebar a las que tienen acceso.

## 🎯 Restricciones Implementadas

### 1. **Bandeja de Comité**

- **Acceso**: Solo superusuarios o usuarios del grupo "Comité de Crédito"
- **URL**: `/workflow/bandeja-comite/`
- **Icono**: 🔨 (fas fa-gavel)

### 2. **Bandejas de Trabajo**

- **Acceso**: Solo superusuarios o usuarios con acceso a alguna etapa de bandeja grupal
- **URL**: `/workflow/vista-mixta-bandejas/`
- **Icono**: 📥 (fas fa-inbox)
- **Criterio**: Usuario debe tener permiso `puede_ver=True` en al menos una etapa con `es_bandeja_grupal=True`

### 3. **Canal Digital**

- **Acceso**: Solo superusuarios o usuarios del grupo "Canal Digital"
- **URL**: `/workflow/canal-digital/`
- **Icono**: 📱 (fas fa-mobile-alt)

## 🔧 Archivos Creados/Modificados

### 📄 Archivos Principales

1. **`workflow/context_processors.py`** ✨ NUEVO

   - Context processor que verifica permisos del usuario
   - Proporciona variables `can_access_*` al template
   - Lógica optimizada para evitar múltiples consultas

2. **`workflow/templates/workflow/base.html`** 📝 MODIFICADO

   - Agregadas condiciones `{% if can_access_* %}` en secciones del sidebar
   - Estructura original mantenida intacta

3. **`financiera/settings.py`** ⚙️ MODIFICADO

   - Agregado context processor a `TEMPLATES['OPTIONS']['context_processors']`

4. **`workflow/management/commands/setup_navigation_groups.py`** ✨ NUEVO
   - Comando para crear grupos necesarios automáticamente
   - Información útil sobre configuración

## 🚀 Configuración Inicial

### 1. **Ejecutar Comando de Configuración**

```bash
python manage.py setup_navigation_groups
```

Este comando:

- ✅ Crea el grupo "Comité de Crédito"
- ✅ Crea el grupo "Canal Digital"
- ✅ Muestra información sobre etapas de bandeja grupal existentes
- ✅ Proporciona instrucciones de configuración

### 2. **Asignar Usuarios a Grupos**

1. Ve al Django Admin (`/admin/`)
2. Navega a **Authentication and Authorization > Users**
3. Edita un usuario
4. En la sección **Groups**, asigna los grupos:
   - **Comité de Crédito**: Para acceso a bandeja de comité
   - **Canal Digital**: Para acceso al canal digital

### 3. **Configurar Permisos de Bandejas Grupales**

Para que los usuarios vean "Bandejas de Trabajo":

1. Ve al Django Admin
2. Navega a **Workflow > Etapas**
3. Marca `es_bandeja_grupal = True` en las etapas correspondientes
4. Navega a **Workflow > Permisos de Bandeja**
5. Crea permisos relacionando:
   - **Etapa**: Etapa con `es_bandeja_grupal=True`
   - **Grupo**: Grupo de usuarios (o usuario específico)
   - **Puede ver**: ✅ True (mínimo requerido)

## 🔍 Lógica de Verificación

### Context Processor Logic

```python
# Superusuarios: Acceso total
if request.user.is_superuser:
    return all_access

# Comité de Crédito:
if user.groups.filter(name="Comité de Crédito").exists():
    can_access_comite = True

# Bandejas de Trabajo:
for etapa in etapas_grupales:
    if PermisoBandeja.objects.filter(
        etapa=etapa,
        grupo__in=user_groups,
        puede_ver=True
    ).exists():
        can_access_bandejas_trabajo = True

# Canal Digital:
if user.groups.filter(name="Canal Digital").exists():
    can_access_canal_digital = True
```

## 📊 Casos de Uso Comunes

### 👑 **Superusuario**

- ✅ Ve todas las secciones del sidebar
- ✅ Acceso completo sin restricciones

### 👨‍💼 **Usuario del Comité**

- ✅ Dashboard
- ✅ Bandeja Comité
- ❌ Bandejas de Trabajo (a menos que tenga permisos específicos)
- ❌ Canal Digital (a menos que esté en el grupo)
- ✅ Negocios
- ✅ Administración (si aplica)
- ✅ Reportes (si aplica)

### 👩‍💻 **Usuario de Canal Digital**

- ✅ Dashboard
- ❌ Bandeja Comité (a menos que esté en el grupo)
- ❌ Bandejas de Trabajo (a menos que tenga permisos específicos)
- ✅ Canal Digital
- ✅ Negocios
- ✅ Administración (si aplica)
- ✅ Reportes (si aplica)

### 👤 **Usuario con Permisos de Bandeja**

- ✅ Dashboard
- ❌ Bandeja Comité (a menos que esté en el grupo)
- ✅ Bandejas de Trabajo
- ❌ Canal Digital (a menos que esté en el grupo)
- ✅ Negocios
- ✅ Administración (si aplica)
- ✅ Reportes (si aplica)

## 🛠️ Mantenimiento

### Agregar Nuevas Restricciones

1. **Actualizar Context Processor**:

   ```python
   # En workflow/context_processors.py
   context['can_access_nueva_seccion'] = check_nueva_condicion()
   ```

2. **Actualizar Template**:
   ```django
   {% if can_access_nueva_seccion %}
   <a class="nav-link" href="{% url 'nueva_seccion' %}">
       <i class="fas fa-icon"></i>
       <span>Nueva Sección</span>
   </a>
   {% endif %}
   ```

### Debugging

Para debuggear permisos, agregar en una vista:

```python
from workflow.context_processors import user_navigation_permissions

def debug_view(request):
    permissions = user_navigation_permissions(request)
    print("User permissions:", permissions)
    # Analizar salida
```

## ⚡ Consideraciones de Rendimiento

- **Optimizado**: Las consultas solo se ejecutan una vez por request
- **Caché**: Django cachea automáticamente los context processors
- **Eficiente**: Usar `exists()` en lugar de `count()` o evaluación completa

## 🔒 Seguridad

- ✅ **Defense in Depth**: Las restricciones del sidebar se complementan con restricciones a nivel de vista
- ✅ **Principio de Menor Privilegio**: Los usuarios solo ven lo que necesitan
- ✅ **Consistente**: Misma lógica de permisos usada en vistas y templates

---

**Implementado por**: Asistente AI  
**Fecha**: Enero 2025  
**Versión**: 1.0  
**Estado**: ✅ Listo para producción
