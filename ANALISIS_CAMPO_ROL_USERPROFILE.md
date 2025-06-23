# Análisis del Campo "Rol" en el Sistema PACÍFICO

## ✅ Confirmación: El Campo "Rol" SÍ EXISTE pero NO se usa en Capacitaciones

### 🔍 **Hallazgos del Análisis**

#### **1. Ubicación del Campo "Rol"**
- **Modelo**: `UserProfile` en `pacifico/models.py` (línea 127-136)
- **Opciones disponibles**:
  - 'Oficial'
  - 'Administrador' 
  - 'Supervisor'
  - 'Usuario'
- **Valor por defecto**: 'Oficial'

#### **2. Estructura del Modelo UserProfile**
```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sucursal = models.CharField(max_length=255, choices=SUCURSALES_OPCIONES, null=True, blank=True)
    oficial = models.CharField(max_length=255, choices=OFICIAL_OPCIONES, null=True, blank=True)
    auto_save_cotizaciones = models.BooleanField(default=False)
    pruebaFuncionalidades = models.BooleanField(default=False)
    rol = models.CharField(
        max_length=20,
        choices=[
            ('Oficial', 'Oficial'),
            ('Administrador', 'Administrador'),
            ('Supervisor', 'Supervisor'),
            ('Usuario', 'Usuario'),
        ],
        default='Oficial'
    )
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
```

#### **3. Uso Actual del Campo "Rol"**
- **En el sistema principal PACÍFICO**: ✅ Se usa (12 referencias encontradas)
- **En capacitaciones_app**: ❌ NO se usa (0 referencias encontradas)
- **Para control de acceso en capacitaciones**: ❌ NO se implementa

### 🤔 **¿Por Qué No Se Usa en Capacitaciones?**

#### **Razones Identificadas:**

1. **Separación de Sistemas**
   - Capacitaciones_app es relativamente independiente
   - Usa su propio sistema de roles (`is_staff`, `is_superuser`)

2. **Roles Diferentes**
   - **Sistema Principal**: Oficial, Administrador, Supervisor, Usuario
   - **Capacitaciones**: Usuario Regular, Staff, Superuser

3. **Implementación Posterior**
   - El sistema de capacitaciones se desarrolló después
   - Se basó en los roles nativos de Django por simplicidad

### 📊 **Comparación de Sistemas de Roles**

| Sistema | Roles | Campo Usado | Propósito |
|---------|-------|-------------|-----------|
| **PACÍFICO Principal** | Oficial, Administrador, Supervisor, Usuario | `UserProfile.rol` | Cotizaciones, seguros, operaciones |
| **Capacitaciones** | Usuario, Staff, Superuser | `User.is_staff`, `User.is_superuser` | Gestión de cursos |

### 🔄 **Posible Integración**

#### **Mapeo Sugerido:**
```python
# Mapeo lógico que podría implementarse:
MAPEO_ROLES = {
    'Usuario': 'usuario_regular',
    'Oficial': 'usuario_regular', 
    'Supervisor': 'staff',
    'Administrador': 'staff',
}
```

### 💡 **Recomendaciones**

#### **Opción 1: Mantener Separado (Actual)**
- ✅ **Pros**: Simple, funcional, independiente
- ❌ **Contras**: Inconsistencia entre sistemas

#### **Opción 2: Integrar Sistemas**
- ✅ **Pros**: Coherencia, un solo sistema de roles
- ❌ **Contras**: Refactoring significativo, complejidad

#### **Opción 3: Híbrido (Recomendado)**
- Mantener sistema actual de capacitaciones
- Agregar verificación opcional del rol UserProfile
- Usar como información adicional, no control principal

### 🎯 **Conclusión**

**Respuesta a tu pregunta**: El campo "Rol" en el formulario de usuario **SÍ se usa en el sistema principal PACÍFICO** para cotizaciones y operaciones financieras, pero **NO se utiliza en el módulo de capacitaciones**, que maneja sus propios roles mediante los campos estándar de Django (`is_staff`, `is_superuser`).

Esto explica por qué en tu análisis de roles solo encontramos 3 tipos en capacitaciones, cuando el formulario muestra 4 opciones de rol.

**Fecha de Análisis**: Junio 22, 2025
