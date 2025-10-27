# Testing Documentation

This guide explains how to run and write tests for the microservices.

## 📋 Table of Contents

- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Test Coverage](#test-coverage)
- [Writing New Tests](#writing-new-tests)
- [CI/CD](#cicd)

## 🧪 Running Tests

### Main API

```bash
cd services/main-api

# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific file
pytest tests/test_main.py

# Run specific test
pytest tests/test_main.py::test_health_endpoint_healthy

# View coverage in browser
open htmlcov/index.html
```

### Auxiliary Service

```bash
cd services/auxiliary-service

# Install test dependencies
pip install -r requirements-test.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run tests using AWS mocks
pytest tests/test_aws_operations.py -v

# View coverage in browser
open htmlcov/index.html
```

## 📂 Test Structure

### Main API Tests

```
services/main-api/tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_main.py             # Main endpoint tests
└── test_aws_resources.py    # AWS endpoint tests
```

**test_main.py** - Tests for:
- ✅ Health endpoint (healthy and degraded)
- ✅ Version endpoint
- ✅ Metrics (Prometheus)
- ✅ OpenAPI docs
- ✅ Version middleware
- ✅ CORS headers

**test_aws_resources.py** - Tests for:
- ✅ List S3 buckets
- ✅ List SSM parameters
- ✅ Get parameter value
- ✅ Error handling

### Auxiliary Service Tests

```
services/auxiliary-service/tests/
├── __init__.py
├── conftest.py              # Fixtures with AWS mocks
├── test_main.py             # Main endpoint tests
└── test_aws_operations.py   # AWS operations tests
```

**test_main.py** - Tests for:
- ✅ Health endpoint
- ✅ Version endpoint
- ✅ Metrics (Prometheus)
- ✅ OpenAPI docs

**test_aws_operations.py** - Tests for:
- ✅ S3: List buckets (with moto)
- ✅ SSM: List parameters (with moto)
- ✅ SSM: Get parameter value
- ✅ SSM: SecureString parameters
- ✅ Error handling and edge cases

## 📊 Test Coverage

### Coverage Goals

- **Minimum acceptable**: 70%
- **Target**: 80%+
- **Ideal**: 90%+

### View Coverage Report

```bash
# Generate HTML report
pytest --cov=app --cov-report=html

# Generate terminal report
pytest --cov=app --cov-report=term-missing

# Generate XML report (for CI/CD)
pytest --cov=app --cov-report=xml
```

### Files Excluded from Coverage

The following files are excluded from coverage analysis:
- `__init__.py`
- Tests themselves
- Configuration and settings

## ✍️ Writing New Tests

### Test Template - Main API

```python
"""
Tests for new feature.
"""
import pytest


def test_new_feature(client):
    """Test description."""
    # Arrange
    expected_result = {"status": "ok"}
    
    # Act
    response = client.get("/new-endpoint")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == expected_result


@pytest.mark.asyncio
async def test_async_feature(client):
    """Test async functionality."""
    # Your async test code here
    pass
```

### Test Template - Auxiliary Service (with AWS Mocks)

```python
"""
Tests for AWS operations.
"""
import pytest
from moto import mock_s3, mock_ssm
import boto3


@mock_s3
def test_s3_operation(client, aws_credentials):
    """Test S3 operation with moto."""
    # Create mock S3 resource
    s3 = boto3.client('s3', region_name='eu-west-1')
    s3.create_bucket(
        Bucket='test-bucket',
        CreateBucketConfiguration={'LocationConstraint': 'eu-west-1'}
    )
    
    # Test your endpoint
    response = client.get("/aws/s3/buckets")
    
    assert response.status_code == 200
    data = response.json()
    assert 'test-bucket' in [b['name'] for b in data['buckets']]


@mock_ssm
def test_ssm_operation(client, aws_credentials):
    """Test SSM operation with moto."""
    # Create mock SSM parameter
    ssm = boto3.client('ssm', region_name='eu-west-1')
    ssm.put_parameter(
        Name='/app/test/param',
        Value='test-value',
        Type='String'
    )
    
    # Test your endpoint
    response = client.get("/aws/ssm/parameter?name=/app/test/param")
    
    assert response.status_code == 200
    data = response.json()
    assert data['value'] == 'test-value'
```

### Best Practices

1. **Descriptive name**: `test_what_when_expected`
   ```python
   def test_health_endpoint_when_service_down_returns_degraded()
   ```

2. **Arrange-Act-Assert**: Clear structure
   ```python
   def test_example():
       # Arrange
       expected = "value"
       
       # Act
       result = function()
       
       # Assert
       assert result == expected
   ```

3. **One concept per test**: Don't mix multiple validations

4. **Independent tests**: Don't depend on execution order

5. **Appropriate mocks**: Use fixtures for external services

## 🔄 CI/CD

### GitHub Actions

Tests run automatically on every push and pull request:

```yaml
- Run tests
- Generate coverage report
- Upload to Codecov (optional)
```

### Local Workflow

Before pushing:

```bash
# 1. Run tests
pytest

# 2. Check coverage
pytest --cov=app --cov-report=term

# 3. Check linting (optional)
flake8 app/ tests/

# 4. If everything passes, commit
git add .
git commit -m "feat: New feature with tests"
git push
```

## 🐛 Debugging Tests

### Verbose Mode

```bash
pytest -v                    # Verbose
pytest -vv                   # Very verbose
pytest -s                    # Don't capture output (see prints)
pytest -x                    # Stop on first failure
pytest --lf                  # Re-run last failed
pytest --tb=short           # Short traceback
```

### Debug with pdb

```python
def test_something():
    import pdb; pdb.set_trace()  # Breakpoint
    # Your test code
```

Or use pytest with pdb:

```bash
pytest --pdb                 # Drop to pdb on failure
pytest --trace              # Start pdb at test start
```

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Moto Documentation](https://docs.getmoto.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)

## ❓ FAQs

### Why do tests fail in CI but pass locally?

- Check dependency versions
- Ensure you have the same requirements
- Review environment variables

### How to mock AWS services?

Use `moto` to mock AWS services:

```python
from moto import mock_s3

@mock_s3
def test_with_s3():
    # Your test code
    pass
```

### How to test async endpoints?

Use `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_async_endpoint():
    # Your async test
    pass
```
