# 🔧 Fix: Correo del Comité de Crédito

## Problema Identificado
El correo del comité se estaba enviando para **TODAS** las etapas de bandeja grupal, incluyendo la etapa "Consulta". Esto era incorrecto ya que el correo del comité debería enviarse únicamente cuando una solicitud llegue específicamente a la etapa "Comité de Crédito".

## Causa del Problema
La lógica anterior en `workflow/views_workflow.py` función `api_cambiar_etapa` tenía:

```python
# ❌ LÓGICA INCORRECTA:
if nueva_etapa.es_bandeja_grupal:
    enviar_correo_bandeja_grupal(solicitud, nueva_etapa)  # Se enviaba para TODAS las bandejas grupales
    
if nueva_etapa.nombre.lower() == "comité de crédito":
    enviar_correo_comite_credito(solicitud, nueva_etapa)  # Se enviaba ADICIONAL para comité
```

**Problema**: `enviar_correo_bandeja_grupal` enviaba correos a jacastillo@fpacifico.com y arodriguez@fpacifico.com para todas las etapas grupales, incluyendo "Consulta", "Análisis", etc.

## Solución Implementada
Cambié la lógica para usar `if-elif` en lugar de `if-if`:

```python
# ✅ LÓGICA CORREGIDA:
if nueva_etapa.nombre.lower() == "comité de crédito":
    enviar_correo_comite_credito(solicitud, nueva_etapa)  # Solo para comité
elif nueva_etapa.es_bandeja_grupal:
    enviar_correo_bandeja_grupal(solicitud, nueva_etapa)  # Para otras bandejas grupales
else:
    # No se envía correo
```

## Comportamiento Correcto Ahora

| Etapa | Tipo | Correo Enviado |
|-------|------|----------------|
| Consulta | Bandeja Grupal | `enviar_correo_bandeja_grupal` |
| Comité de Crédito | Bandeja Grupal | `enviar_correo_comite_credito` |
| Análisis | Individual | Ninguno |
| Aprobación | Individual | Ninguno |

## Destinatarios

- **Correo del Comité**: jacastillo@fpacifico.com, arodriguez@fpacifico.com
- **Correo Bandeja Grupal**: jacastillo@fpacifico.com, arodriguez@fpacifico.com

## Validación
Se creó comando de prueba `test_correo_fix.py` que confirma:
- ✅ Etapa "Consulta" → Correo bandeja grupal
- ✅ Etapa "Comité de Crédito" → Correo específico del comité
- ✅ Correo real del comité se envía correctamente

## Archivos Modificados
- `workflow/views_workflow.py` → Función `api_cambiar_etapa` líneas 3076-3085
- `workflow/management/commands/test_correo_fix.py` → Comando de prueba (nuevo)

## Status
✅ **CORREGIDO Y VALIDADO** - El correo del comité ahora se envía únicamente cuando una solicitud avanza a la etapa "Comité de Crédito". 