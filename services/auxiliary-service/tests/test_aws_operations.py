"""
Tests for AWS SDK operations (S3, SSM).
"""
import pytest
from moto import mock_s3, mock_ssm
import boto3


@mock_s3
def test_list_s3_buckets_endpoint(client, aws_credentials):
    """Test listing S3 buckets through the endpoint."""
    # Create test buckets directly
    s3 = boto3.client('s3', region_name='eu-west-1')
    s3.create_bucket(
        Bucket='test-bucket-1',
        CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}
    )
    s3.create_bucket(
        Bucket='test-bucket-2',
        CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}
    )
    
    response = client.get("/aws/s3/buckets")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "buckets" in data
    assert "count" in data
    assert data["count"] >= 2
    
    bucket_names = [b["name"] for b in data["buckets"]]
    assert "test-bucket-1" in bucket_names
    assert "test-bucket-2" in bucket_names


@mock_s3
def test_list_s3_buckets_empty(client, aws_credentials):
    """Test listing S3 buckets when there are none."""
    response = client.get("/aws/s3/buckets")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "buckets" in data
    assert "count" in data
    assert data["count"] == 0
    assert data["buckets"] == []


@mock_ssm
def test_list_ssm_parameters_endpoint(client, aws_credentials):
    """Test listing SSM parameters through the endpoint."""
    # Create test parameters directly
    ssm = boto3.client('ssm', region_name='eu-west-1')
    ssm.put_parameter(Name='/app/test/param1', Value='value1', Type='String')
    ssm.put_parameter(Name='/app/test/param2', Value='value2', Type='String')
    
    response = client.get("/aws/ssm/parameters")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "parameters" in data
    assert "count" in data
    assert data["count"] >= 2


@mock_ssm
def test_list_ssm_parameters_with_prefix(client, aws_credentials):
    """Test listing SSM parameters with path prefix."""
    # Create test parameters directly
    ssm = boto3.client('ssm', region_name='eu-west-1')
    ssm.put_parameter(Name='/app/test/param1', Value='value1', Type='String')
    ssm.put_parameter(Name='/app/other/param2', Value='value2', Type='String')
    
    response = client.get("/aws/ssm/parameters?path_prefix=/app/test")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "parameters" in data
    assert data["path_prefix"] == "/app/test"
    
    # Should only return parameters with /app/test prefix
    for param in data["parameters"]:
        assert param["name"].startswith("/app/test")


@mock_ssm
def test_get_ssm_parameter_value_endpoint(client, aws_credentials):
    """Test getting a specific SSM parameter value."""
    # Create test parameter directly
    ssm = boto3.client('ssm', region_name='eu-west-1')
    ssm.put_parameter(
        Name='/app/test/param1',
        Value='test-value-123',
        Type='String',
        Description='Test parameter'
    )
    
    response = client.get("/aws/ssm/parameter?name=/app/test/param1")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "/app/test/param1"
    assert data["value"] == "test-value-123"
    assert data["type"] == "String"
    assert "version" in data
    assert "arn" in data


@mock_ssm
def test_get_ssm_parameter_not_found(client, aws_credentials):
    """Test getting a non-existent SSM parameter."""
    response = client.get("/aws/ssm/parameter?name=/app/test/nonexistent")
    
    # Should return 404 or error response
    assert response.status_code in [404, 500]


@mock_ssm
def test_get_ssm_parameter_secure_string(client, aws_credentials):
    """Test getting a SecureString SSM parameter."""
    # Create secure parameter
    ssm = boto3.client('ssm', region_name='eu-west-1')
    ssm.put_parameter(
        Name='/app/test/secret',
        Value='super-secret',
        Type='SecureString',
        Description='Secret parameter'
    )
    
    response = client.get("/aws/ssm/parameter?name=/app/test/secret")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "/app/test/secret"
    assert data["type"] == "SecureString"
    # Value should be decrypted
    assert "value" in data


def test_get_ssm_parameter_missing_name(client):
    """Test getting parameter without providing name."""
    response = client.get("/aws/ssm/parameter")
    
    # Should return 422 for missing required query parameter
    assert response.status_code == 422
