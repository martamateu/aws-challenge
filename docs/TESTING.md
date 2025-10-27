# Testing Documentation

Esta guía explica cómo ejecutar y escribir tests para los microservicios.

## 📋 Tabla de Contenidos

- [Ejecutar Tests](#ejecutar-tests)
- [Estructura de Tests](#estructura-de-tests)
- [Cobertura de Tests](#cobertura-de-tests)
- [Escribir Nuevos Tests](#escribir-nuevos-tests)
- [CI/CD](#cicd)

## 🧪 Ejecutar Tests

### Main API

```bash
cd services/main-api

# Instalar dependencias de test
pip install -r requirements-test.txt

# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=app --cov-report=html

# Ejecutar un archivo específico
pytest tests/test_main.py

# Ejecutar un test específico
pytest tests/test_main.py::test_health_endpoint_healthy

# Ver cobertura en el navegador
open htmlcov/index.html
```

### Auxiliary Service

```bash
cd services/auxiliary-service

# Instalar dependencias de test
pip install -r requirements-test.txt

# Ejecutar todos los tests
pytest

# Ejecutar con cobertura
pytest --cov=app --cov-report=html

# Ejecutar tests que usan AWS mocks
pytest tests/test_aws_operations.py -v

# Ver cobertura en el navegador
open htmlcov/index.html
```

## 📂 Estructura de Tests

### Main API Tests

```
services/main-api/tests/
├── __init__.py
├── conftest.py              # Fixtures compartidos
├── test_main.py             # Tests de endpoints principales
└── test_aws_resources.py    # Tests de endpoints AWS
```

**test_main.py** - Tests de:
- ✅ Health endpoint (healthy y degraded)
- ✅ Version endpoint
- ✅ Metrics (Prometheus)
- ✅ OpenAPI docs
- ✅ Middleware de versión
- ✅ CORS headers

**test_aws_resources.py** - Tests de:
- ✅ Listar buckets S3
- ✅ Listar parámetros SSM
- ✅ Obtener valor de parámetro
- ✅ Manejo de errores

### Auxiliary Service Tests

```
services/auxiliary-service/tests/
├── __init__.py
├── conftest.py              # Fixtures con mocks de AWS
├── test_main.py             # Tests de endpoints principales
└── test_aws_operations.py   # Tests de operaciones AWS
```

**test_main.py** - Tests de:
- ✅ Health endpoint
- ✅ Version endpoint
- ✅ Metrics (Prometheus)
- ✅ OpenAPI docs

**test_aws_operations.py** - Tests de:
- ✅ S3: Listar buckets (con moto)
- ✅ SSM: Listar parámetros (con moto)
- ✅ SSM: Obtener valor de parámetro
- ✅ SSM: Parámetros SecureString
- ✅ Manejo de errores y edge cases

## 📊 Cobertura de Tests

### Objetivos de Cobertura

- **Mínimo aceptable**: 70%
- **Objetivo**: 80%+
- **Ideal**: 90%+

### Ver Reporte de Cobertura

```bash
# Generar reporte HTML
pytest --cov=app --cov-report=html

# Generar reporte en terminal
pytest --cov=app --cov-report=term-missing

# Generar reporte XML (para CI/CD)
pytest --cov=app --cov-report=xml
```

### Archivos Excluidos de Cobertura

Los siguientes archivos están excluidos del análisis de cobertura:
- `__init__.py`
- Tests themselves
- Configuración y settings

## ✍️ Escribir Nuevos Tests

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

### Test Template - Auxiliary Service (con AWS Mocks)

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

### Buenas Prácticas

1. **Nombre descriptivo**: `test_what_when_expected`
   ```python
   def test_health_endpoint_when_service_down_returns_degraded()
   ```

2. **Arrange-Act-Assert**: Estructura clara
   ```python
   def test_example():
       # Arrange
       expected = "value"
       
       # Act
       result = function()
       
       # Assert
       assert result == expected
   ```

3. **Un concepto por test**: No mezclar múltiples validaciones

4. **Tests independientes**: No depender del orden de ejecución

5. **Mocks apropiados**: Usar fixtures para servicios externos

## 🔄 CI/CD

### GitHub Actions

Los tests se ejecutan automáticamente en cada push y pull request:

```yaml
- Run tests
- Generate coverage report
- Upload to Codecov (opcional)
```

### Workflow Local

Antes de hacer push:

```bash
# 1. Ejecutar tests
pytest

# 2. Verificar cobertura
pytest --cov=app --cov-report=term

# 3. Verificar linting (opcional)
flake8 app/ tests/

# 4. Si todo pasa, hacer commit
git add .
git commit -m "feat: New feature with tests"
git push
```

## 🐛 Debugging Tests

### Modo Verbose

```bash
pytest -v                    # Verbose
pytest -vv                   # Very verbose
pytest -s                    # Sin capturar output (ver prints)
pytest -x                    # Parar en primer fallo
pytest --lf                  # Re-run last failed
pytest --tb=short           # Traceback corto
```

### Debug con pdb

```python
def test_something():
    import pdb; pdb.set_trace()  # Breakpoint
    # Your test code
```

O usar pytest con pdb:

```bash
pytest --pdb                 # Drop to pdb on failure
pytest --trace              # Start pdb at test start
```

## 📚 Recursos

- [Pytest Documentation](https://docs.pytest.org/)
- [Moto Documentation](https://docs.getmoto.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Coverage.py](https://coverage.readthedocs.io/)

## ❓ FAQs

### ¿Por qué fallan los tests en CI pero pasan localmente?

- Verifica las versiones de dependencias
- Asegúrate de tener los mismos requirements
- Revisa variables de entorno

### ¿Cómo mockear AWS services?

Usa `moto` para mockear servicios AWS:

```python
from moto import mock_s3

@mock_s3
def test_with_s3():
    # Your test code
    pass
```

### ¿Cómo testear endpoints async?

Usa `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_async_endpoint():
    # Your async test
    pass
```
