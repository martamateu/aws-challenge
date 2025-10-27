"""
Tests for auxiliary service main endpoints (health, version, metrics).
"""
import pytest


def test_health_endpoint(client):
    """Test health endpoint."""
    response = client.get("/health")
    
    # May return 200 or 503 depending on AWS connectivity
    assert response.status_code in [200, 503]
    data = response.json()
    
    assert "status" in data
    # Service field is optional and depends on health status
    if "service" in data:
        assert data["service"] in ["auxiliary-service", "Auxiliary Service"]


def test_version_endpoint(client):
    """Test version endpoint."""
    response = client.get("/version")
    
    assert response.status_code == 200
    data = response.json()
    
    # Accept both formats
    assert data["service"] in ["auxiliary-service", "Auxiliary Service"]
    assert "version" in data
    assert "environment" in data
    # timestamp is optional
    assert "aws_region" in data or "timestamp" in data


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
    assert data["info"]["title"] == "Auxiliary Service"
