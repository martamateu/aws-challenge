"""Main API application - Entry point."""

import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict

import httpx
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

from app import __version__
from app.config import get_settings

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
    'main_api_requests_total',
    'Total request count',
    ['method', 'endpoint', 'status']
)
REQUEST_DURATION = Histogram(
    'main_api_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Auxiliary Service URL: {settings.auxiliary_service_url}")
    
    # Startup: Create HTTP client
    app.state.http_client = httpx.AsyncClient(
        timeout=settings.auxiliary_service_timeout,
        follow_redirects=True
    )
    
    yield
    
    # Shutdown: Close HTTP client
    await app.state.http_client.aclose()
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Main API for AWS resources management via Auxiliary Service",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_version_headers(request: Request, call_next):
    """Add version information to all responses."""
    response = await call_next(request)
    response.headers["X-Main-API-Version"] = settings.app_version
    
    # Try to get auxiliary service version
    try:
        aux_version = await get_auxiliary_version()
        response.headers["X-Auxiliary-Service-Version"] = aux_version
    except Exception as e:
        logger.warning(f"Could not retrieve auxiliary service version: {e}")
        response.headers["X-Auxiliary-Service-Version"] = "unknown"
    
    return response


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


async def get_auxiliary_version() -> str:
    """Get version from auxiliary service."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.auxiliary_service_url}/version")
            if response.status_code == 200:
                data = response.json()
                return data.get("version", "unknown")
    except Exception as e:
        logger.error(f"Error getting auxiliary service version: {e}")
    return "unknown"


async def add_version_info(data: Dict) -> Dict:
    """Add version information to response data."""
    aux_version = await get_auxiliary_version()
    
    return {
        **data,
        "main_api_version": settings.app_version,
        "auxiliary_service_version": aux_version
    }


# Include routers (imported here to avoid circular import)
from app.routers import aws_resources

app.include_router(
    aws_resources.router,
    prefix=settings.api_prefix,
    tags=["AWS Resources"]
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    aux_version = await get_auxiliary_version()
    
    # Check connectivity to auxiliary service
    auxiliary_healthy = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.auxiliary_service_url}/health")
            auxiliary_healthy = response.status_code == 200
    except Exception as e:
        logger.error(f"Auxiliary service health check failed: {e}")
    
    health_status = {
        "status": "healthy" if auxiliary_healthy else "degraded",
        "main_api_version": settings.app_version,
        "auxiliary_service_version": aux_version,
        "auxiliary_service_healthy": auxiliary_healthy,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    status_code = 200 if auxiliary_healthy else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/version", tags=["Info"])
async def get_version():
    """Get API version information."""
    return await add_version_info({
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    })


@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information."""
    return await add_version_info({
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
