# INSTRUCCIONES PARA TESTING - SISTEMA DE BANDEJAS

## 1. ACTIVAR EL SERVIDOR

```bash
# En Windows PowerShell
cd C:\Users\jacastillo\Documents\GitHub\PACIFICO
venv\Scripts\activate.bat
python manage.py runserver
```

## 2. ABRIR LA APLICACIÓN

1. Abrir navegador
2. Ir a: http://127.0.0.1:8000/workflow/bandeja-mixta/
3. Abrir consola del navegador (F12)

## 3. VERIFICAR ESTADO DEL SISTEMA

En la consola del navegador ejecutar:
```javascript
debugearEstado()
```

Deberías ver:
- CSRF Token presente
- Bandeja grupal y personal con datos
- Recarga automática activa
- Tiempo hasta próxima recarga

## 4. PROBAR FUNCIONALIDAD

### Tomar Solicitud:
1. Hacer clic en botón "Tomar" de bandeja grupal
2. Observar logs en consola:
   - "🔵 === INICIANDO PROCESO DE TOMAR SOLICITUD ==="
   - "✅ Solicitud tomada exitosamente, recargando página..."
   - "🔄 Recargando página para reflejar cambios..."
3. La página debe recargarse automáticamente en 1-2 segundos
4. La solicitud debe aparecer en "Mis Tareas"

### Devolver Solicitud:
1. Hacer clic en botón "Devolver" de bandeja personal
2. Confirmar en el diálogo
3. Observar logs similares
4. La página debe recargarse automáticamente
5. La solicitud debe volver a "Bandeja Grupal"

## 5. VERIFICAR RECARGA AUTOMÁTICA

1. Esperar 30 segundos sin hacer nada
2. Observar log: "🔄 Recarga automática programada - actualizando página..."
3. La página debe recargarse automáticamente

## 6. TROUBLESHOOTING

### Si no funciona el botón:
1. Verificar que el servidor esté ejecutándose
2. Verificar CSRF token con `debugearEstado()`
3. Revisar errores en consola
4. Verificar que la URL sea correcta

### Si no recarga automáticamente:
1. Verificar logs de JavaScript
2. Probar manualmente: `window.location.reload()`
3. Verificar que no haya errores de JavaScript

### Si aparece "Error al tomar la solicitud":
1. Verificar que el servidor Django esté funcionando
2. Verificar que las URLs estén configuradas correctamente
3. Revisar logs del servidor Django
4. Verificar permisos de usuario

## 7. LOGS IMPORTANTES

Buscar estos logs en la consola:
- ✅ "Sistema de recarga automática iniciado"
- 🔵 "INICIANDO PROCESO DE TOMAR SOLICITUD"
- ✅ "Solicitud tomada exitosamente"
- 🔄 "Recargando página para reflejar cambios"
- 🔄 "Recarga automática programada" 