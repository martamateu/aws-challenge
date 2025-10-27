"""
Test configuration and fixtures for Main API tests.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add parent directory to path to import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


@pytest.fixture
def client():
    """FastAPI test client fixture."""
    return TestClient(app)


@pytest.fixture
def mock_auxiliary_service():
    """Mock auxiliary service responses."""
    with patch('app.main.httpx.AsyncClient') as mock:
        async_client = Mock()
        mock.return_value.__aenter__.return_value = async_client
        
        # Mock version endpoint
        version_response = Mock()
        version_response.status_code = 200
        version_response.json.return_value = {
            "service": "auxiliary-service",
            "version": "1.0.0",
            "environment": "test"
        }
        
        # Mock health endpoint
        health_response = Mock()
        health_response.status_code = 200
        health_response.json.return_value = {"status": "healthy"}
        
        async def mock_get(url):
            if "version" in url:
                return version_response
            elif "health" in url:
                return health_response
            return Mock(status_code=404)
        
        async_client.get.side_effect = mock_get
        
        yield async_client


@pytest.fixture
def mock_auxiliary_service_down():
    """Mock auxiliary service being down."""
    with patch('app.main.httpx.AsyncClient') as mock:
        async_client = Mock()
        mock.return_value.__aenter__.return_value = async_client
        
        async def mock_get_error(url):
            raise Exception("Connection refused")
        
        async_client.get.side_effect = mock_get_error
        
        yield async_client
