"""
Utility functions for the Main API service.
"""
from typing import Dict, Any


def add_version_info(data: Dict[str, Any], version: str = "1.0.0") -> Dict[str, Any]:
    """
    Add version information to response data.
    
    Args:
        data: Original response data
        version: API version string
        
    Returns:
        Response data with version information added
    """
    return {
        **data,
        "version": version,
        "api": "main-api"
    }
