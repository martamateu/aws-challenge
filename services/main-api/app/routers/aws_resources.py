"""AWS Resources router - Handles all AWS-related endpoints."""

import logging
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Request, Query

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter()


async def call_auxiliary_service(request: Request, endpoint: str, params: dict = None) -> dict:
    """
    Call the auxiliary service and return the response.
    
    Args:
        request: FastAPI request object (to access http_client)
        endpoint: Endpoint path on auxiliary service
        params: Query parameters
    
    Returns:
        Response data from auxiliary service
    
    Raises:
        HTTPException: If auxiliary service call fails
    """
    url = f"{settings.auxiliary_service_url}{endpoint}"
    
    try:
        logger.info(f"Calling auxiliary service: {url}")
        client = request.app.state.http_client
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    except httpx.TimeoutException:
        logger.error(f"Timeout calling auxiliary service: {url}")
        raise HTTPException(
            status_code=504,
            detail="Auxiliary service timeout"
        )
    
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error from auxiliary service: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Auxiliary service error: {e.response.text}"
        )
    
    except httpx.RequestError as e:
        logger.error(f"Request error calling auxiliary service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Cannot reach auxiliary service: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error calling auxiliary service: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/s3/buckets")
async def list_s3_buckets(request: Request):
    """
    List all S3 buckets in the AWS account.
    
    Returns:
        JSON response with list of buckets and version information
    """
    logger.info("Listing S3 buckets")
    
    data = await call_auxiliary_service(request, "/aws/s3/buckets")
    
    # Add main API version
    return {
        **data,
        "main_api_version": settings.app_version
    }


@router.get("/parameters")
async def list_parameters(request: Request, path_prefix: Optional[str] = Query(None, description="Filter parameters by path prefix")):
    """
    List all parameters in AWS Systems Manager Parameter Store.
    
    Args:
        path_prefix: Optional filter to list parameters under a specific path
    
    Returns:
        JSON response with list of parameters and version information
    """
    logger.info(f"Listing parameters (prefix: {path_prefix})")
    
    params = {}
    if path_prefix:
        params["path_prefix"] = path_prefix
    
    data = await call_auxiliary_service(request, "/aws/parameters", params)
    
    # Add main API version
    return {
        **data,
        "main_api_version": settings.app_version
    }


@router.get("/parameters/value")
async def get_parameter_value(
    request: Request,
    name: str = Query(..., description="Name of the parameter to retrieve"),
    decrypt: bool = Query(True, description="Decrypt secure string parameters")
):
    """
    Get the value of a specific parameter from AWS Systems Manager Parameter Store.
    
    Args:
        name: Name of the parameter
        decrypt: Whether to decrypt SecureString parameters (default: True)
    
    Returns:
        JSON response with parameter details and version information
    """
    logger.info(f"Getting parameter value: {name}")
    
    params = {
        "name": name,
        "decrypt": str(decrypt).lower()
    }
    
    data = await call_auxiliary_service(request, "/aws/parameters/value", params)
    
    # Add main API version
    return {
        **data,
        "main_api_version": settings.app_version
    }
