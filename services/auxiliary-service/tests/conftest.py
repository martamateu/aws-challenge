"""
Test configuration and fixtures for Auxiliary Service tests.
"""
import pytest
from fastapi.testclient import TestClient
from moto import mock_s3, mock_ssm
import boto3
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
def aws_credentials():
    """Mock AWS Credentials for moto."""
    import os
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-1'


@pytest.fixture
def s3_client(aws_credentials):
    """Create mocked S3 client with test buckets."""
    with mock_s3():
        s3 = boto3.client('s3', region_name='eu-west-1')
        
        # Create test buckets
        s3.create_bucket(
            Bucket='test-bucket-1',
            CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}
        )
        s3.create_bucket(
            Bucket='test-bucket-2',
            CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}
        )
        
        yield s3


@pytest.fixture
def ssm_client(aws_credentials):
    """Create mocked SSM client with test parameters."""
    with mock_ssm():
        ssm = boto3.client('ssm', region_name='eu-west-1')
        
        # Create test parameters
        ssm.put_parameter(
            Name='/app/test/param1',
            Value='value1',
            Type='String',
            Description='Test parameter 1'
        )
        ssm.put_parameter(
            Name='/app/test/param2',
            Value='secret-value',
            Type='SecureString',
            Description='Test parameter 2'
        )
        ssm.put_parameter(
            Name='/app/test/database/host',
            Value='localhost',
            Type='String',
            Description='Database host'
        )
        
        yield ssm
