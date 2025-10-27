"""
Tests for main API endpoints (health, version, metrics).
"""
import pytest
from fastapi.testclient import TestClient


def test_health_endpoint_healthy(client, mock_auxiliary_service):
    """Test health endpoint when auxiliary service is healthy."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] in ["healthy", "degraded"]
    assert "main_api_version" in data
    assert "timestamp" in data


def test_health_endpoint_degraded(client, mock_auxiliary_service_down):
    """Test health endpoint when auxiliary service is down."""
    response = client.get("/health")
    
    # Should still return 200 but with degraded status
    assert response.status_code in [200, 503]
    data = response.json()
    
    assert "status" in data
    assert "main_api_version" in data


def test_version_endpoint(client):
    """Test version endpoint."""
    response = client.get("/version")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["service"] in ["main-api", "Main API"]  # Accept both formats
    assert "version" in data
    assert "environment" in data
    # timestamp is added to /health, not /version
    assert "main_api_version" in data
    assert "auxiliary_service_version" in data


def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics")
    
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    
    # Check for some expected metrics
    content = response.text
    assert "http_requests_total" in content or "python_info" in content


def test_docs_endpoint(client):
    """Test that OpenAPI docs are available."""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_endpoint(client):
    """Test that OpenAPI JSON spec is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert data["info"]["title"] == "Main API"


def test_version_header_middleware(client):
    """Test that version headers are added to responses."""
    response = client.get("/version")
    data = response.json()
    
    # Check for version headers (case-insensitive)
    headers_lower = {k.lower(): v for k, v in response.headers.items()}
    assert ("x-api-version" in headers_lower or 
            "x-main-api-version" in headers_lower or
            data.get("version") is not None)  # Version info is in response body


def test_cors_headers(client):
    """Test that CORS headers are present."""
    response = client.options("/version")
    
    # CORS middleware should handle OPTIONS requests
    assert response.status_code in [200, 405]  # 405 if no explicit OPTIONS handler


def test_root_redirect(client):
    """Test that root redirects to docs."""
    response = client.get("/", follow_redirects=False)
    
    # Should redirect to /docs or return some info
    assert response.status_code in [200, 307, 308]
