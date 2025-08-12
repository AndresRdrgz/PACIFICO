# API Externa para Crear Solicitudes

Esta documentación describe cómo usar la API externa para crear y gestionar solicitudes desde aplicaciones externas.

## Endpoints Disponibles

### 1. Crear Solicitud Externa
**POST** `/workflow/api/externa/solicitudes/crear/`

Crea una nueva solicitud desde una aplicación externa.

#### Parámetros Requeridos (JSON):
- `pipeline_id` (int): ID del pipeline a usar
- `api_source` (string): Identificador de la aplicación externa

#### Parámetros Opcionales (JSON):
- `cliente_nombre` (string): Nombre completo del cliente
- `cliente_cedula` (string): Cédula del cliente
- `cliente_telefono` (string): Teléfono del cliente
- `cliente_email` (string): Email del cliente
- `producto_solicitado` (string): Producto de interés
- `monto_solicitado` (decimal): Monto solicitado
- `sector` (string): Sector laboral del cliente
- `motivo_consulta` (string): Motivo de la consulta
- `como_se_entero` (string): Cómo se enteró del servicio
- `observaciones` (string): Observaciones adicionales
- `propietario_username` (string): Username del usuario propietario

#### Ejemplo de Request:
```json
{
    "pipeline_id": 1,
    "api_source": "app_movil_pacifico",
    "cliente_nombre": "Juan Pérez",
    "cliente_cedula": "8-123-456",
    "cliente_telefono": "6234-5678",
    "cliente_email": "juan.perez@email.com",
    "producto_solicitado": "Préstamo Personal",
    "monto_solicitado": 5000.00,
    "sector": "Sector Público",
    "motivo_consulta": "Consolidación de deudas",
    "como_se_entero": "Promoción",
    "observaciones": "Cliente con buen historial crediticio"
}
```

#### Ejemplo de Response (Éxito):
```json
{
    "success": true,
    "message": "Solicitud creada exitosamente",
    "solicitud": {
        "id": 123,
        "codigo": "PLN-ABC12345",
        "pipeline": "Préstamos",
        "etapa_actual": "Ingreso",
        "creada_via_api": true,
        "api_source": "app_movil_pacifico",
        "fecha_creacion": "2024-01-15T10:30:00Z",
        "cliente_nombre": "Juan Pérez",
        "cliente_cedula": "8-123-456",
        "producto_solicitado": "Préstamo Personal",
        "monto_solicitado": "5000.00"
    }
}
```

### 2. Listar Solicitudes Externas
**GET** `/workflow/api/externa/solicitudes/`

Lista las solicitudes creadas vía API externa con filtros opcionales.

#### Parámetros de Consulta:
- `api_source` (string): Filtrar por aplicación externa específica
- `page` (int): Número de página (default: 1)
- `page_size` (int): Tamaño de página (default: 20, máximo: 100)
- `fecha_desde` (string): Fecha desde (formato: YYYY-MM-DD)
- `fecha_hasta` (string): Fecha hasta (formato: YYYY-MM-DD)

#### Ejemplo de Request:
```
GET /workflow/api/externa/solicitudes/?api_source=app_movil_pacifico&page=1&page_size=10
```

### 3. Detalle de Solicitud Externa
**GET** `/workflow/api/externa/solicitudes/{solicitud_id}/`

Obtiene el detalle completo de una solicitud específica creada vía API externa.

#### Ejemplo de Request:
```
GET /workflow/api/externa/solicitudes/123/
```

### 4. Estadísticas de Solicitudes Externas
**GET** `/workflow/api/externa/solicitudes/estadisticas/`

Obtiene estadísticas de las solicitudes creadas vía API externa.

#### Parámetros de Consulta:
- `api_source` (string): Filtrar por aplicación externa específica
- `fecha_desde` (string): Fecha desde (formato: YYYY-MM-DD)
- `fecha_hasta` (string): Fecha hasta (formato: YYYY-MM-DD)

## Identificación de Solicitudes API

Las solicitudes creadas vía API externa se pueden identificar de las siguientes maneras:

1. **Campo `creada_via_api`**: Valor `true` en todas las solicitudes API
2. **Campo `api_source`**: Contiene el identificador de la aplicación externa
3. **Campo `origen`**: Se establece automáticamente como "API Externa"

## Ejemplos de Uso

### Python (requests)
```python
import requests
import json

# Crear solicitud
url = "http://localhost:8000/workflow/api/externa/solicitudes/crear/"
data = {
    "pipeline_id": 1,
    "api_source": "mi_app_externa",
    "cliente_nombre": "María García",
    "cliente_cedula": "8-987-654",
    "producto_solicitado": "Préstamo Auto",
    "monto_solicitado": 15000.00
}

response = requests.post(url, json=data)
if response.status_code == 201:
    solicitud = response.json()['solicitud']
    print(f"Solicitud creada: {solicitud['codigo']}")
else:
    print(f"Error: {response.json()}")

# Listar solicitudes
url = "http://localhost:8000/workflow/api/externa/solicitudes/"
params = {"api_source": "mi_app_externa"}
response = requests.get(url, params=params)
if response.status_code == 200:
    data = response.json()
    print(f"Total solicitudes: {data['pagination']['total_count']}")
    for solicitud in data['solicitudes']:
        print(f"- {solicitud['codigo']}: {solicitud['cliente_nombre']}")
```

### cURL
```bash
# Crear solicitud
curl -X POST http://localhost:8000/workflow/api/externa/solicitudes/crear/ \
  -H "Content-Type: application/json" \
  -d '{
    "pipeline_id": 1,
    "api_source": "mi_app_externa",
    "cliente_nombre": "Carlos López",
    "cliente_cedula": "8-555-123",
    "producto_solicitado": "Préstamo Personal",
    "monto_solicitado": 3000.00
  }'

# Listar solicitudes
curl "http://localhost:8000/workflow/api/externa/solicitudes/?api_source=mi_app_externa"

# Obtener detalle
curl "http://localhost:8000/workflow/api/externa/solicitudes/123/"

# Estadísticas
curl "http://localhost:8000/workflow/api/externa/solicitudes/estadisticas/?api_source=mi_app_externa"
```

## Códigos de Error

- **400 Bad Request**: Datos JSON inválidos o campos requeridos faltantes
- **404 Not Found**: Pipeline no encontrado, usuario no encontrado, o solicitud no encontrada
- **405 Method Not Allowed**: Método HTTP no permitido
- **500 Internal Server Error**: Error interno del servidor

## Notas Importantes

1. **Seguridad**: Estos endpoints están marcados con `@csrf_exempt` para facilitar la integración. En producción, considere implementar autenticación por token.

2. **Permisos**: Las solicitudes creadas vía API son asignadas automáticamente al primer superusuario disponible como propietario, a menos que se especifique un `propietario_username`.

3. **Pipeline**: Asegúrese de que el pipeline especificado existe y tiene al menos una etapa configurada.

4. **Identificación**: Use el campo `api_source` para identificar y filtrar solicitudes de su aplicación específica.

5. **Requisitos**: Los requisitos del pipeline se crean automáticamente para cada solicitud nueva.
