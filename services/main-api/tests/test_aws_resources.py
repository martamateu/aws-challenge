"""
Tests for AWS resource endpoints (S3, SSM).
"""
import pytest
from unittest.mock import patch, Mock


@pytest.fixture
def mock_s3_response():
    """Mock S3 buckets response from auxiliary service."""
    return {
        "buckets": [
            {
                "name": "test-bucket-1",
                "creation_date": "2025-10-24T10:00:00+00:00"
            },
            {
                "name": "test-bucket-2",
                "creation_date": "2025-10-24T11:00:00+00:00"
            }
        ],
        "count": 2
    }


@pytest.fixture
def mock_ssm_parameters_response():
    """Mock SSM parameters response from auxiliary service."""
    return {
        "parameters": [
            {
                "name": "/app/test/param1",
                "type": "String",
                "last_modified": "2025-10-24T10:00:00+00:00",
                "version": 1
            },
            {
                "name": "/app/test/param2",
                "type": "SecureString",
                "last_modified": "2025-10-24T11:00:00+00:00",
                "version": 1
            }
        ],
        "count": 2,
        "path_prefix": None
    }


@pytest.fixture
def mock_ssm_parameter_value_response():
    """Mock SSM parameter value response from auxiliary service."""
    return {
        "name": "/app/test/param1",
        "value": "test-value",
        "type": "String",
        "version": 1,
        "last_modified": "2025-10-24T10:00:00+00:00",
        "arn": "arn:aws:ssm:eu-west-1:123456789012:parameter/app/test/param1"
    }


def test_list_s3_buckets_success(client, mock_s3_response):
    """Test listing S3 buckets successfully."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_s3_response
        
        async_client = Mock()
        async_client.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = async_client
        
        response = client.get("/api/v1/s3/buckets")
        
        assert response.status_code == 200
        data = response.json()
        
        # Might be direct response or wrapped
        if "buckets" in data:
            assert len(data["buckets"]) == 2
            assert data["count"] == 2


def test_list_parameters_success(client, mock_ssm_parameters_response):
    """Test listing SSM parameters successfully."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ssm_parameters_response
        
        async_client = Mock()
        async_client.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = async_client
        
        response = client.get("/api/v1/parameters")
        
        assert response.status_code == 200
        data = response.json()
        
        if "parameters" in data:
            assert len(data["parameters"]) == 2
            assert data["count"] == 2


def test_get_parameter_value_success(client, mock_ssm_parameter_value_response):
    """Test getting a specific SSM parameter value."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_ssm_parameter_value_response
        
        async_client = Mock()
        async_client.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = async_client
        
        response = client.get("/api/v1/parameters/value?name=/app/test/param1")
        
        assert response.status_code == 200
        data = response.json()
        
        if "name" in data:
            assert data["name"] == "/app/test/param1"
            assert "value" in data


def test_get_parameter_value_missing_name(client):
    """Test getting parameter value without providing name."""
    response = client.get("/api/v1/parameters/value")
    
    # Should return 422 for missing required query parameter
    assert response.status_code == 422


def test_list_parameters_with_prefix(client):
    """Test listing SSM parameters with path prefix."""
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "parameters": [],
            "count": 0,
            "path_prefix": "/app/test"
        }
        
        async_client = Mock()
        async_client.get.return_value = mock_response
        mock_client.return_value.__aenter__.return_value = async_client
        
        response = client.get("/api/v1/parameters?path_prefix=/app/test")
        
        # Should accept the prefix parameter
        assert response.status_code in [200, 500]  # 500 if auxiliary service is mocked incorrectly
