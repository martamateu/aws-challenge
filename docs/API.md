# API Documentation

Complete documentation for Main API and Auxiliary Service endpoints.

## 📖 Table of Contents

- [Main API Endpoints](#main-api-endpoints)
- [Auxiliary Service Endpoints](#auxiliary-service-endpoints)
- [Versioning](#versioning)
- [Status Codes](#status-codes)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)

## 🚀 Main API Endpoints

Base URL: `http://localhost:8000` (local) or the LoadBalancer endpoint in Kubernetes.

### Health & Info

#### GET /health

Service health check and connectivity verification with Auxiliary Service.

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

Get service version information.

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

Root endpoint with API information.

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

List all S3 buckets in the AWS account.

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

**Possible errors:**
- `503 Service Unavailable` - Cannot connect to Auxiliary Service
- `500 Internal Server Error` - AWS SDK error

**Example with curl:**
```bash
curl http://localhost:8000/api/v1/s3/buckets | jq
```

**Example with httpie:**
```bash
http GET http://localhost:8000/api/v1/s3/buckets
```

#### GET /api/v1/parameters

List all parameters from AWS Systems Manager Parameter Store.

**Query Parameters:**
- `path_prefix` (optional): Filter parameters by path prefix

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

**With path filter:**
```bash
curl "http://localhost:8000/api/v1/parameters?path_prefix=/aws-challenge/dev/database" | jq
```

**Response with filter:**
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

Get the value of a specific parameter from Parameter Store.

**Query Parameters:**
- `name` (required): Parameter name
- `decrypt` (optional, default: true): Decrypt SecureString parameters

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

**Examples:**
```bash
# Get normal parameter
curl "http://localhost:8000/api/v1/parameters/value?name=/aws-challenge/dev/database/host" | jq

# Get SecureString (decrypted)
curl "http://localhost:8000/api/v1/parameters/value?name=/aws-challenge/dev/api/key&decrypt=true" | jq

# Get SecureString (without decryption)
curl "http://localhost:8000/api/v1/parameters/value?name=/aws-challenge/dev/api/key&decrypt=false" | jq
```

### Monitoring

#### GET /metrics

Prometheus metrics endpoint.

**Response (Prometheus format):**
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

**Example:**
```bash
curl http://localhost:8000/metrics
```

## 🔧 Auxiliary Service Endpoints

Base URL: `http://auxiliary-service.auxiliary-service.svc.cluster.local:8001` (internal) or `http://localhost:8001` (port-forward).

### Health & Info

#### GET /health

Health check with AWS connectivity verification.

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

Version information.

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

List S3 buckets directly using AWS SDK.

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

List Parameter Store parameters.

**Query Parameters:**
- `path_prefix` (optional): Filter by path

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

Get specific parameter value.

**Query Parameters:**
- `name` (required): Parameter name
- `decrypt` (optional, default: true): Decrypt SecureStrings

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

Prometheus metrics.

**Specific metrics:**
- `auxiliary_service_requests_total`: Total requests
- `auxiliary_service_request_duration_seconds`: Request duration
- `auxiliary_service_aws_api_calls_total`: Total AWS API calls

## 📊 Versioning

All Main API responses include version information:

### In the Body (JSON)

```json
{
  "main_api_version": "1.0.0",
  "auxiliary_service_version": "1.0.0",
  ...
}
```

### In the Headers

```http
X-Main-API-Version: 1.0.0
X-Auxiliary-Service-Version: 1.0.0
```

### Example

```bash
# View complete headers
curl -I http://localhost:8000/health

# Result:
HTTP/1.1 200 OK
X-Main-API-Version: 1.0.0
X-Auxiliary-Service-Version: 1.0.0
Content-Type: application/json
```

## 🔢 Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 404 | Not Found | Resource not found (e.g.: parameter) |
| 500 | Internal Server Error | Internal server error |
| 503 | Service Unavailable | Auxiliary Service not available |
| 504 | Gateway Timeout | Timeout calling Auxiliary Service |

## 🔐 Authentication

**Current version**: No authentication (development).

For production, recommended to implement:
- API Keys in headers
- JWT tokens
- OAuth 2.0
- mTLS (mutual TLS)

## ⏱️ Rate Limiting

**Current version**: No rate limiting.

For production, recommended:
- Rate limiting per IP
- Rate limiting per API key
- Use Nginx Ingress Controller with rate limiting
- Implement circuit breaker pattern

## 🧪 Complete Testing Examples

### Testing Script

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

## 📚 References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## 🎓 Interactive Documentation Access

FastAPI automatically generates interactive documentation:

### Swagger UI

Access `http://localhost:8000/docs` to view interactive documentation with Swagger UI.

Features:
- Test endpoints directly
- View request/response schemas
- Auto-generated from code

### ReDoc

Access `http://localhost:8000/redoc` to view documentation with ReDoc.

Features:
- Cleaner and more organized view
- Better for reading
- Download OpenAPI specification
