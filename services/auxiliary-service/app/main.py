"""Auxiliary Service - Handles AWS interactions."""

import logging
import sys
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from app import __version__
from app.config import get_settings
from app.services.aws_service import aws_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'auxiliary_service_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'auxiliary_service_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)
AWS_API_CALLS = Counter(
    'auxiliary_service_aws_api_calls_total',
    'Total AWS API calls',
    ['service', 'operation', 'status']
)


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Auxiliary Service for AWS SDK interactions",
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Record metrics for each request."""
    method = request.method
    path = request.url.path
    
    with REQUEST_DURATION.labels(method=method, endpoint=path).time():
        response = await call_next(request)
    
    REQUEST_COUNT.labels(
        method=method,
        endpoint=path,
        status=response.status_code
    ).inc()
    
    return response


@app.on_event("startup")
async def startup_event():
    """Log startup information."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"AWS Region: {settings.aws_region}")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information."""
    logger.info(f"Shutting down {settings.app_name}")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    # Try to test AWS connectivity
    aws_healthy = True
    try:
        # Simple test: try to list buckets (doesn't need to succeed, just needs to connect)
        aws_service.s3_client.list_buckets()
    except Exception as e:
        logger.warning(f"AWS connectivity check failed: {e}")
        aws_healthy = False
    
    health_status = {
        "status": "healthy" if aws_healthy else "degraded",
        "version": settings.app_version,
        "aws_region": settings.aws_region,
        "aws_connectivity": aws_healthy,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    status_code = 200 if aws_healthy else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/version", tags=["Info"])
async def get_version():
    """Get service version information."""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "aws_region": settings.aws_region
    }


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )


@app.get("/aws/s3/buckets", tags=["AWS"])
async def list_s3_buckets():
    """
    List all S3 buckets in the AWS account.
    
    Returns:
        JSON response with list of S3 buckets
        
    Raises:
        HTTPException: If AWS API call fails
    """
    try:
        AWS_API_CALLS.labels(service='s3', operation='list_buckets', status='attempt').inc()
        result = aws_service.list_s3_buckets()
        AWS_API_CALLS.labels(service='s3', operation='list_buckets', status='success').inc()
        return result
    
    except Exception as e:
        AWS_API_CALLS.labels(service='s3', operation='list_buckets', status='error').inc()
        logger.error(f"Error listing S3 buckets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/aws/parameters", tags=["AWS"])
async def list_parameters(
    path_prefix: Optional[str] = Query(None, description="Filter parameters by path prefix")
):
    """
    List all parameters from AWS Systems Manager Parameter Store.
    
    Args:
        path_prefix: Optional filter to list parameters under a specific path
        
    Returns:
        JSON response with list of parameters
        
    Raises:
        HTTPException: If AWS API call fails
    """
    try:
        AWS_API_CALLS.labels(service='ssm', operation='describe_parameters', status='attempt').inc()
        result = aws_service.list_parameters(path_prefix)
        AWS_API_CALLS.labels(service='ssm', operation='describe_parameters', status='success').inc()
        return result
    
    except Exception as e:
        AWS_API_CALLS.labels(service='ssm', operation='describe_parameters', status='error').inc()
        logger.error(f"Error listing parameters: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/aws/parameters/value", tags=["AWS"])
async def get_parameter_value(
    name: str = Query(..., description="Name of the parameter to retrieve"),
    decrypt: bool = Query(True, description="Decrypt secure string parameters")
):
    """
    Get the value of a specific parameter from AWS Systems Manager Parameter Store.
    
    Args:
        name: Name of the parameter
        decrypt: Whether to decrypt SecureString parameters
        
    Returns:
        JSON response with parameter details
        
    Raises:
        HTTPException: If parameter not found or AWS API call fails
    """
    try:
        AWS_API_CALLS.labels(service='ssm', operation='get_parameter', status='attempt').inc()
        result = aws_service.get_parameter_value(name, decrypt)
        AWS_API_CALLS.labels(service='ssm', operation='get_parameter', status='success').inc()
        return result
    
    except Exception as e:
        AWS_API_CALLS.labels(service='ssm', operation='get_parameter', status='error').inc()
        logger.error(f"Error getting parameter value: {str(e)}")
        
        # Return 404 if parameter not found
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with service information."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
