# API Documentation

Documentación completa de los endpoints de la Main API y Auxiliary Service.

## 📖 Tabla de Contenidos

- [Main API Endpoints](#main-api-endpoints)
- [Auxiliary Service Endpoints](#auxiliary-service-endpoints)
- [Versionado](#versionado)
- [Códigos de Estado](#códigos-de-estado)
- [Autenticación](#autenticación)
- [Rate Limiting](#rate-limiting)

## 🚀 Main API Endpoints

Base URL: `http://localhost:8000` (local) o el endpoint del LoadBalancer en Kubernetes.

### Health & Info

#### GET /health

Health check del servicio y verificación de conectividad con Auxiliary Service.

**Response 200 - Healthy:**
```json
{
  "status": "healthy",
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0",
  "auxiliary_service_healthy": true,
  "timestamp": "2025-10-24T10:30:00Z"
}
```

**Response 503 - Degraded:**
```json
{
  "status": "degraded",
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "unknown",
  "auxiliary_service_healthy": false,
  "timestamp": "2025-10-24T10:30:00Z"
}
```

#### GET /version

Obtiene información de versión del servicio.

**Response:**
```json
{
  "service": "Main API",
  "version": "1.0.0",
  "environment": "development",
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0"
}
```

#### GET /

Endpoint raíz con información del API.

**Response:**
```json
{
  "message": "Welcome to Main API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health",
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0"
}
```

### AWS Resources

#### GET /api/v1/s3/buckets

Lista todos los buckets de S3 en la cuenta de AWS.

**Headers:**
```
X-Main-API-Version: 1.0.0
X-Auxiliary-Service-Version: 1.0.0
```

**Response 200:**
```json
{
  "buckets": [
    {
      "name": "aws-challenge-data-dev-123456789012",
      "creation_date": "2025-10-24T08:00:00+00:00"
    },
    {
      "name": "aws-challenge-logs-dev-123456789012",
      "creation_date": "2025-10-24T08:00:00+00:00"
    },
    {
      "name": "aws-challenge-backups-dev-123456789012",
      "creation_date": "2025-10-24T08:00:00+00:00"
    }
  ],
  "count": 3,
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0"
}
```

**Errores posibles:**
- `503 Service Unavailable` - No se puede conectar con Auxiliary Service
- `500 Internal Server Error` - Error en AWS SDK

**Ejemplo con curl:**
```bash
curl http://localhost:8000/api/v1/s3/buckets | jq
```

**Ejemplo con httpie:**
```bash
http GET http://localhost:8000/api/v1/s3/buckets
```

#### GET /api/v1/parameters

Lista todos los parámetros de AWS Systems Manager Parameter Store.

**Query Parameters:**
- `path_prefix` (opcional): Filtrar parámetros por prefijo de path

**Response 200:**
```json
{
  "parameters": [
    {
      "name": "/aws-challenge/dev/database/host",
      "type": "String",
      "last_modified": "2025-10-24T08:00:00+00:00",
      "version": 1
    },
    {
      "name": "/aws-challenge/dev/database/port",
      "type": "String",
      "last_modified": "2025-10-24T08:00:00+00:00",
      "version": 1
    },
    {
      "name": "/aws-challenge/dev/api/key",
      "type": "SecureString",
      "last_modified": "2025-10-24T08:00:00+00:00",
      "version": 1
    }
  ],
  "count": 3,
  "path_prefix": null,
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0"
}
```

**Con filtro de path:**
```bash
curl "http://localhost:8000/api/v1/parameters?path_prefix=/aws-challenge/dev/database" | jq
```

**Response con filtro:**
```json
{
  "parameters": [
    {
      "name": "/aws-challenge/dev/database/host",
      "type": "String",
      "last_modified": "2025-10-24T08:00:00+00:00",
      "version": 1
    },
    {
      "name": "/aws-challenge/dev/database/port",
      "type": "String",
      "last_modified": "2025-10-24T08:00:00+00:00",
      "version": 1
    }
  ],
  "count": 2,
  "path_prefix": "/aws-challenge/dev/database",
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0"
}
```

#### GET /api/v1/parameters/value

Obtiene el valor de un parámetro específico del Parameter Store.

**Query Parameters:**
- `name` (requerido): Nombre del parámetro
- `decrypt` (opcional, default: true): Descifrar SecureString parameters

**Response 200:**
```json
{
  "name": "/aws-challenge/dev/database/host",
  "value": "db.dev.example.com",
  "type": "String",
  "version": 1,
  "last_modified": "2025-10-24T08:00:00+00:00",
  "arn": "arn:aws:ssm:us-east-1:123456789012:parameter/aws-challenge/dev/database/host",
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0"
}
```

**Response 404 - Parameter Not Found:**
```json
{
  "detail": "Parameter '/aws-challenge/dev/nonexistent' not found"
}
```

**Ejemplos:**
```bash
# Obtener parámetro normal
curl "http://localhost:8000/api/v1/parameters/value?name=/aws-challenge/dev/database/host" | jq

# Obtener SecureString (descifrado)
curl "http://localhost:8000/api/v1/parameters/value?name=/aws-challenge/dev/api/key&decrypt=true" | jq

# Obtener SecureString (sin descifrar)
curl "http://localhost:8000/api/v1/parameters/value?name=/aws-challenge/dev/api/key&decrypt=false" | jq
```

### Monitoring

#### GET /metrics

Endpoint de métricas Prometheus.

**Response (formato Prometheus):**
```
# HELP main_api_requests_total Total request count
# TYPE main_api_requests_total counter
main_api_requests_total{endpoint="/health",method="GET",status="200"} 42.0

# HELP main_api_request_duration_seconds Request duration in seconds
# TYPE main_api_request_duration_seconds histogram
main_api_request_duration_seconds_bucket{endpoint="/health",method="GET",le="0.005"} 35.0
main_api_request_duration_seconds_bucket{endpoint="/health",method="GET",le="0.01"} 40.0
...
```

**Ejemplo:**
```bash
curl http://localhost:8000/metrics
```

## 🔧 Auxiliary Service Endpoints

Base URL: `http://auxiliary-service.auxiliary-service.svc.cluster.local:8001` (interno) o `http://localhost:8001` (port-forward).

### Health & Info

#### GET /health

Health check con verificación de conectividad AWS.

**Response 200:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "aws_region": "us-east-1",
  "aws_connectivity": true,
  "timestamp": "2025-10-24T10:30:00Z"
}
```

**Response 503:**
```json
{
  "status": "degraded",
  "version": "1.0.0",
  "aws_region": "us-east-1",
  "aws_connectivity": false,
  "timestamp": "2025-10-24T10:30:00Z"
}
```

#### GET /version

Información de versión.

**Response:**
```json
{
  "service": "Auxiliary Service",
  "version": "1.0.0",
  "environment": "development",
  "aws_region": "us-east-1"
}
```

### AWS Operations

#### GET /aws/s3/buckets

Lista buckets de S3 directamente usando AWS SDK.

**Response 200:**
```json
{
  "buckets": [
    {
      "name": "aws-challenge-data-dev-123456789012",
      "creation_date": "2025-10-24T08:00:00+00:00"
    }
  ],
  "count": 1
}
```

**Response 500:**
```json
{
  "detail": "AWS Error: AccessDenied - User: ... is not authorized to perform: s3:ListAllMyBuckets"
}
```

#### GET /aws/parameters

Lista parámetros del Parameter Store.

**Query Parameters:**
- `path_prefix` (opcional): Filtrar por path

**Response 200:**
```json
{
  "parameters": [
    {
      "name": "/aws-challenge/dev/database/host",
      "type": "String",
      "last_modified": "2025-10-24T08:00:00+00:00",
      "version": 1
    }
  ],
  "count": 1,
  "path_prefix": null
}
```

#### GET /aws/parameters/value

Obtiene valor de parámetro específico.

**Query Parameters:**
- `name` (requerido): Nombre del parámetro
- `decrypt` (opcional, default: true): Descifrar SecureStrings

**Response 200:**
```json
{
  "name": "/aws-challenge/dev/database/host",
  "value": "db.dev.example.com",
  "type": "String",
  "version": 1,
  "last_modified": "2025-10-24T08:00:00+00:00",
  "arn": "arn:aws:ssm:us-east-1:123456789012:parameter/aws-challenge/dev/database/host"
}
```

**Response 404:**
```json
{
  "detail": "Parameter '/nonexistent' not found"
}
```

#### GET /metrics

Métricas Prometheus.

**Métricas específicas:**
- `auxiliary_service_requests_total`: Total de requests
- `auxiliary_service_request_duration_seconds`: Duración de requests
- `auxiliary_service_aws_api_calls_total`: Total de llamadas a AWS API

## 📊 Versionado

Todas las respuestas de la Main API incluyen información de versión:

### En el Body (JSON)

```json
{
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0",
  ...
}
```

### En los Headers

```http
X-Main-API-Version: 1.0.0
X-Auxiliary-Service-Version: 1.0.0
```

### Ejemplo

```bash
# Ver headers completos
curl -I http://localhost:8000/health

# Resultado:
HTTP/1.1 200 OK
X-Main-API-Version: 1.0.0
X-Auxiliary-Service-Version: 1.0.0
Content-Type: application/json
```

## 🔢 Códigos de Estado

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Request exitoso |
| 404 | Not Found | Recurso no encontrado (ej: parámetro) |
| 500 | Internal Server Error | Error interno del servidor |
| 503 | Service Unavailable | Auxiliary Service no disponible |
| 504 | Gateway Timeout | Timeout llamando a Auxiliary Service |

## 🔐 Autenticación

**Versión actual**: Sin autenticación (desarrollo).

Para producción, se recomienda implementar:
- API Keys en headers
- JWT tokens
- OAuth 2.0
- mTLS (mutual TLS)

## ⏱️ Rate Limiting

**Versión actual**: Sin rate limiting.

Para producción, se recomienda:
- Rate limiting por IP
- Rate limiting por API key
- Usar Nginx Ingress Controller con rate limiting
- Implementar circuit breaker pattern

## 🧪 Ejemplos de Testing Completo

### Script de Testing

```bash
#!/bin/bash

API_URL="http://localhost:8000"

echo "Testing Main API..."

# Health check
echo "1. Health check:"
curl -s $API_URL/health | jq '.status'

# Version
echo "2. Version:"
curl -s $API_URL/version | jq '.version'

# S3 Buckets
echo "3. S3 Buckets:"
curl -s $API_URL/api/v1/s3/buckets | jq '.count'

# Parameters
echo "4. Parameters:"
curl -s $API_URL/api/v1/parameters | jq '.count'

# Specific parameter
echo "5. Specific parameter:"
curl -s "$API_URL/api/v1/parameters/value?name=/aws-challenge/dev/database/host" | jq '.value'

echo "Done!"
```

### Python Testing

```python
import requests

API_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{API_URL}/health")
assert response.status_code == 200
assert response.json()["status"] == "healthy"

# S3 Buckets
response = requests.get(f"{API_URL}/api/v1/s3/buckets")
assert response.status_code == 200
buckets = response.json()["buckets"]
assert len(buckets) > 0

# Parameters
response = requests.get(f"{API_URL}/api/v1/parameters")
assert response.status_code == 200
params = response.json()["parameters"]
assert len(params) > 0

# Specific parameter
response = requests.get(
    f"{API_URL}/api/v1/parameters/value",
    params={"name": "/aws-challenge/dev/database/host"}
)
assert response.status_code == 200
assert "value" in response.json()

# Check version headers
assert "X-Main-API-Version" in response.headers
assert "X-Auxiliary-Service-Version" in response.headers

print("All tests passed!")
```

## 📚 Referencias

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## 🎓 Acceso a Documentación Interactiva

FastAPI genera automáticamente documentación interactiva:

### Swagger UI

Accede a `http://localhost:8000/docs` para ver la documentación interactiva con Swagger UI.

Características:
- Probar endpoints directamente
- Ver schemas de request/response
- Autogenerada desde el código

### ReDoc

Accede a `http://localhost:8000/redoc` para ver la documentación con ReDoc.

Características:
- Vista más limpia y organizada
- Mejor para lectura
- Descarga de especificación OpenAPI
