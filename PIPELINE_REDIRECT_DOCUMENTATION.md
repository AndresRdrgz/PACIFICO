# Funcionalidad de Redirección Automática de Pipeline en Negocios

## 📋 Descripción

Se ha implementado una nueva funcionalidad que permite a los usuarios ser redirigidos automáticamente al último pipeline seleccionado cuando acceden a la vista de Negocios (`/workflow/negocios/`).

## 🚀 Funcionamiento

### Comportamiento del Usuario

1. **Selección de Pipeline**: Cuando un usuario visita `/workflow/negocios/?pipeline=123`, el sistema:

   - Guarda el ID del pipeline en la sesión del usuario
   - Muestra una notificación indicando que el pipeline se guardó como preferencia
   - Funciona normalmente mostrando las solicitudes del pipeline seleccionado

2. **Redirección Automática**: Cuando el usuario accede posteriormente a `/workflow/negocios/` (sin parámetros):

   - El sistema verifica si hay un pipeline guardado en la sesión
   - Valida que el pipeline aún existe y el usuario tiene permisos para accederlo
   - Redirige automáticamente a `/workflow/negocios/?pipeline=123`

3. **Limpiar Preferencia**: Los usuarios pueden:
   - Hacer clic en el ícono "×" junto al indicador "Pipeline guardado como preferencia" en el header
   - Usar la función JavaScript `clearSavedPipeline()` para eliminar la preferencia

### Validaciones de Seguridad

- ✅ **Permisos**: Solo redirige si el usuario aún tiene acceso al pipeline guardado
- ✅ **Existencia**: Verifica que el pipeline aún exista en la base de datos
- ✅ **Limpieza Automática**: Elimina automáticamente preferencias inválidas

## 🔧 Implementación Técnica

### Backend (views_negocios.py)

```python
# Clave de sesión única por usuario
session_key = f'negocios_last_pipeline_{request.user.id}'

# Guardar pipeline cuando se accede con filtro
if pipeline_filter:
    request.session[session_key] = pipeline_filter

# Redirigir cuando se accede sin filtros
elif not any([search_query, etapa_filter, estado_filter, page != '1']) and session_key in request.session:
    last_pipeline = request.session[session_key]
    # Validar permisos y existencia...
    if pipeline_exists:
        redirect_url = f"{reverse('workflow:negocios')}?pipeline={last_pipeline}"
        return redirect(redirect_url)
```

### APIs Nuevas

1. **Limpiar Pipeline Guardado**

   ```
   POST /workflow/api/negocios/clear-saved-pipeline/
   ```

2. **Obtener Pipeline Guardado**
   ```
   GET /workflow/api/negocios/get-saved-pipeline/
   ```

### Frontend (negocios.html)

- **Notificación**: Informa al usuario cuando se guarda un pipeline como preferencia
- **Indicador Visual**: Muestra en el header cuando hay un pipeline guardado
- **Botón de Limpiar**: Permite eliminar la preferencia fácilmente

## 🎯 Casos de Uso

### Escenario 1: Usuario Regular

```
1. Usuario visita: /workflow/negocios/?pipeline=5 (Flujo de Consulta de Auto)
2. Sistema guarda pipeline 5 en sesión
3. Usuario cierra navegador o va a otra página
4. Usuario vuelve a: /workflow/negocios/
5. Sistema redirige automáticamente a: /workflow/negocios/?pipeline=5
```

### Escenario 2: Pipeline Sin Acceso

```
1. Usuario tenía pipeline 5 guardado
2. Admin revoca permisos del usuario al pipeline 5
3. Usuario accede a: /workflow/negocios/
4. Sistema detecta falta de permisos
5. Limpia la sesión automáticamente
6. No redirige, muestra vista normal
```

### Escenario 3: Pipeline Eliminado

```
1. Usuario tenía pipeline 5 guardado
2. Admin elimina el pipeline 5
3. Usuario accede a: /workflow/negocios/
4. Sistema detecta que pipeline no existe
5. Limpia la sesión automáticamente
6. No redirige, muestra vista normal
```

## 🛡️ Consideraciones de Seguridad

- **Aislamiento por Usuario**: Cada usuario tiene su propia clave de sesión
- **Validación de Permisos**: Siempre verifica permisos antes de redirigir
- **Limpieza Automática**: Elimina automáticamente referencias inválidas
- **No Interferencia**: No afecta otros filtros (búsqueda, etapa, estado)

## 📊 Ventajas

1. **Experiencia de Usuario Mejorada**: Los usuarios vuelven automáticamente a su pipeline de trabajo
2. **Productividad**: Reduce clics y navegación repetitiva
3. **Memoria Contextual**: El sistema "recuerda" dónde estaba trabajando el usuario
4. **No Intrusivo**: Solo actúa cuando el usuario accede sin filtros específicos

## 🔄 Casos Donde NO Se Aplica la Redirección

- Cuando hay parámetros de búsqueda (`?search=...`)
- Cuando hay filtros de etapa (`?etapa=...`)
- Cuando hay filtros de estado (`?estado=...`)
- Cuando se accede a una página específica (`?page=2`)
- Cuando no hay pipeline guardado en sesión
- Cuando el pipeline guardado ya no es válido

## 🧪 Testing

El archivo `test_pipeline_redirect.py` incluye pruebas para:

- ✅ Guardado de pipeline en sesión
- ✅ Redirección automática
- ✅ Limpieza de preferencias
- ✅ Validación de permisos
- ✅ Manejo de pipelines inexistentes

## 📝 Notas de Desarrollo

- La funcionalidad usa sesiones de Django para persistencia
- Compatible con usuarios regulares y superusuarios
- No requiere cambios en la base de datos
- Totalmente opcional - funciona como enhacement no breaking
