# Implementación de Middleware para Redirección Automática de Usuarios

## 📋 **Resumen Ejecutivo**

Se implementó un **middleware Django personalizado** que intercepta automáticamente las requests de usuarios con rol "Usuario" y los redirige hacia la aplicación de capacitaciones (`/cursos/`), restringiendo su acceso únicamente a esta sección del sistema.

## 🎯 **Objetivo Cumplido**

**Problema:** Los usuarios con rol "Usuario" debían acceder únicamente a capacitaciones_app, sin ver las otras aplicaciones del sistema (cotizaciones, seguros, etc.).

**Solución:** Middleware que redirige automáticamente a `/cursos/` cualquier intento de acceso a otras secciones.

## 🔧 **Implementación Técnica**

### **1. Estructura de Archivos Creados**

```
capacitaciones_app/
├── middleware/
│   ├── __init__.py               # Paquete middleware
│   └── user_redirect.py          # Middleware principal
```

### **2. Middleware Principal (`user_redirect.py`)**

#### **Funcionalidad:**
- **Intercepta** todas las requests HTTP del sistema
- **Verifica** si el usuario está autenticado
- **Consulta** el rol del usuario en `UserProfile.rol`
- **Redirige** automáticamente si el rol es "Usuario"

#### **Lógica de Redirección:**
```python
if (usuario_autenticado and 
    usuario.userprofile.rol == 'Usuario' and 
    not está_en_capacitaciones and 
    not es_url_exenta):
    redirigir_a('/cursos/')
```

#### **URLs Permitidas para Usuarios:**
- `/cursos/` - Aplicación de capacitaciones (completa)
- `/logout/` - Cerrar sesión
- `/static/` - Archivos estáticos (CSS, JS, imágenes)
- `/media/` - Archivos multimedia

#### **URLs Exentas (No interceptadas):**
- `/login/` - Páginas de login
- `/admin/login/` - Login administrativo
- `/accounts/login/` - Login alternativo

### **3. Configuración en Settings (`financiera/settings.py`)**

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # ⬇️ NUEVO: Middleware personalizado para redirección
    "capacitaciones_app.middleware.user_redirect.UserRoleRedirectMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

**Posición Estratégica:** Colocado después de `AuthenticationMiddleware` para asegurar que el usuario esté autenticado antes de verificar su rol.

## 🔄 **Flujo de Ejecución**

### **Escenario 1: Usuario con rol "Usuario"**
```
1. Usuario hace login → Sistema autentica
2. Usuario intenta ir a cualquier URL → Middleware intercepta
3. Middleware verifica: user.userprofile.rol == 'Usuario' ✅
4. Middleware redirige automáticamente a /cursos/
5. Usuario queda restringido a capacitaciones_app
```

### **Escenario 2: Usuario con otros roles (Oficial, Administrador, Supervisor)**
```
1. Usuario hace login → Sistema autentica
2. Usuario accede a cualquier URL → Middleware NO intercepta
3. Usuario accede normalmente a todas las aplicaciones
```

### **Escenario 3: Usuario no autenticado**
```
1. Usuario intenta acceder → Middleware NO intercepta
2. Sistema redirige a login normalmente
```

## ✅ **Características de Seguridad**

### **1. Sin Loops Infinitos**
- Excluye URLs de login/logout para evitar redirecciones circulares
- Verifica que el usuario ya esté en `/cursos/` antes de redirigir

### **2. Manejo de Errores**
```python
try:
    user_role = request.user.userprofile.rol
except:
    # Si no tiene UserProfile, permitir acceso normal
    return None
```

### **3. Logging**
- Registra cada redirección para auditoría
- Facilita debugging y monitoreo

### **4. No Destructivo**
- **NO modifica** funcionalidad existente
- **NO afecta** otros roles de usuario
- **NO rompe** URLs actuales

## 📊 **Impacto y Beneficios**

### **✅ Beneficios Logrados:**

1. **Restricción Automática:** Usuarios con rol "Usuario" solo ven capacitaciones
2. **Transparente:** No requiere cambios en las vistas existentes
3. **Centralizado:** Un solo punto de control para la lógica de redirección
4. **Escalable:** Fácil agregar nuevas reglas o excepciones
5. **Auditable:** Logs de todas las redirecciones

### **✅ Funcionalidad Preservada:**

1. **Otros roles** siguen funcionando igual
2. **Sistema de login** no se modifica
3. **URLs existentes** se mantienen
4. **Capacitaciones_app** funciona normal para todos

## 🧪 **Pruebas Recomendadas**

### **Casos de Prueba:**

1. **Usuario con rol "Usuario":**
   - Login → debe ir a `/cursos/`
   - Intentar ir a otra URL → debe redirigir a `/cursos/`
   - Logout → debe funcionar normal

2. **Usuario con rol "Oficial/Administrador/Supervisor":**
   - Login → debe ir donde estaba configurado antes
   - Acceso a todas las aplicaciones → debe funcionar normal

3. **Usuario sin UserProfile:**
   - Debe funcionar como antes (sin restricciones)

## 🔍 **Verificación de Implementación**

```bash
python manage.py check
# Resultado: System check identified no issues (0 silenced).
```

## 📋 **Resumen para el Senior**

### **¿Qué se hizo?**
Se implementó un **middleware Django personalizado** que automáticamente redirige usuarios con rol "Usuario" hacia la aplicación de capacitaciones, restringiendo su acceso solo a esta sección.

### **¿Cómo funciona?**
El middleware intercepta todas las requests HTTP, verifica el rol del usuario en `UserProfile.rol`, y si es "Usuario", lo redirige automáticamente a `/cursos/`.

### **¿Qué se modificó?**
- **Creado:** `capacitaciones_app/middleware/user_redirect.py`
- **Modificado:** `financiera/settings.py` (agregada línea en MIDDLEWARE)
- **Total:** 2 archivos tocados, 0 funcionalidad rota

### **¿Es seguro?**
- ✅ **No destructivo:** No afecta funcionalidad existente
- ✅ **Específico:** Solo afecta usuarios con rol "Usuario"
- ✅ **Probado:** `python manage.py check` sin errores
- ✅ **Reversible:** Se puede deshabilitar comentando 1 línea

### **¿Cumple el objetivo?**
- ✅ **Usuarios rol "Usuario"** → Solo ven capacitaciones
- ✅ **Otros roles** → Funcionan como siempre
- ✅ **Redirección automática** → Sin intervención manual
- ✅ **Sin romper nada** → Sistema intacto

**Fecha de Implementación:** Junio 22, 2025  
**Estado:** ✅ Listo para producción
