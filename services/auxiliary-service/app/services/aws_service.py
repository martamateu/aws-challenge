"""AWS Service - Handles all interactions with AWS SDK (boto3)."""

import logging
from datetime import datetime
from typing import List, Dict, Optional

import boto3
from botocore.exceptions import ClientError, BotoCoreError

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AWSService:
    """Service class for AWS interactions."""
    
    def __init__(self):
        """Initialize AWS clients."""
        self.region = settings.aws_region
        
        # Initialize boto3 clients
        # When running with IRSA, boto3 automatically uses the service account credentials
        self.s3_client = boto3.client('s3', region_name=self.region)
        self.ssm_client = boto3.client('ssm', region_name=self.region)
        
        logger.info(f"AWS Service initialized for region: {self.region}")
    
    def list_s3_buckets(self) -> Dict:
        """
        List all S3 buckets in the AWS account.
        
        Returns:
            Dictionary with buckets list and count
            
        Raises:
            Exception: If AWS API call fails
        """
        try:
            logger.info("Fetching S3 buckets from AWS")
            response = self.s3_client.list_buckets()
            
            buckets = [
                {
                    "name": bucket['Name'],
                    "creation_date": bucket['CreationDate'].isoformat()
                }
                for bucket in response.get('Buckets', [])
            ]
            
            logger.info(f"Successfully retrieved {len(buckets)} S3 buckets")
            
            return {
                "buckets": buckets,
                "count": len(buckets)
            }
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS ClientError listing S3 buckets: {error_code} - {error_message}")
            raise Exception(f"AWS Error: {error_code} - {error_message}")
        
        except BotoCoreError as e:
            logger.error(f"BotoCoreError listing S3 buckets: {str(e)}")
            raise Exception(f"AWS connection error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error listing S3 buckets: {str(e)}")
            raise Exception(f"Unexpected error: {str(e)}")
    
    def list_parameters(self, path_prefix: Optional[str] = None) -> Dict:
        """
        List all parameters from AWS Systems Manager Parameter Store.
        
        Args:
            path_prefix: Optional filter to list parameters under a specific path
            
        Returns:
            Dictionary with parameters list and count
            
        Raises:
            Exception: If AWS API call fails
        """
        try:
            logger.info(f"Fetching parameters from AWS Parameter Store (prefix: {path_prefix})")
            
            parameters = []
            paginator = self.ssm_client.get_paginator('describe_parameters')
            
            # Build request parameters
            request_params = {}
            if path_prefix:
                request_params['ParameterFilters'] = [
                    {
                        'Key': 'Name',
                        'Option': 'BeginsWith',
                        'Values': [path_prefix]
                    }
                ]
            
            # Paginate through all parameters
            for page in paginator.paginate(**request_params):
                for param in page.get('Parameters', []):
                    parameters.append({
                        "name": param['Name'],
                        "type": param['Type'],
                        "last_modified": param['LastModifiedDate'].isoformat(),
                        "version": param.get('Version', 1)
                    })
            
            logger.info(f"Successfully retrieved {len(parameters)} parameters")
            
            return {
                "parameters": parameters,
                "count": len(parameters),
                "path_prefix": path_prefix
            }
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS ClientError listing parameters: {error_code} - {error_message}")
            raise Exception(f"AWS Error: {error_code} - {error_message}")
        
        except BotoCoreError as e:
            logger.error(f"BotoCoreError listing parameters: {str(e)}")
            raise Exception(f"AWS connection error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error listing parameters: {str(e)}")
            raise Exception(f"Unexpected error: {str(e)}")
    
    def get_parameter_value(self, name: str, decrypt: bool = True) -> Dict:
        """
        Get the value of a specific parameter from AWS Systems Manager Parameter Store.
        
        Args:
            name: Name of the parameter
            decrypt: Whether to decrypt SecureString parameters
            
        Returns:
            Dictionary with parameter details including value
            
        Raises:
            Exception: If parameter not found or AWS API call fails
        """
        try:
            logger.info(f"Fetching parameter value: {name} (decrypt: {decrypt})")
            
            response = self.ssm_client.get_parameter(
                Name=name,
                WithDecryption=decrypt
            )
            
            param = response['Parameter']
            
            result = {
                "name": param['Name'],
                "value": param['Value'],
                "type": param['Type'],
                "version": param.get('Version', 1),
                "last_modified": param['LastModifiedDate'].isoformat(),
                "arn": param.get('ARN', '')
            }
            
            logger.info(f"Successfully retrieved parameter: {name}")
            
            return result
        
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'ParameterNotFound':
                logger.warning(f"Parameter not found: {name}")
                raise Exception(f"Parameter '{name}' not found")
            
            logger.error(f"AWS ClientError getting parameter: {error_code} - {error_message}")
            raise Exception(f"AWS Error: {error_code} - {error_message}")
        
        except BotoCoreError as e:
            logger.error(f"BotoCoreError getting parameter: {str(e)}")
            raise Exception(f"AWS connection error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error getting parameter: {str(e)}")
            raise Exception(f"Unexpected error: {str(e)}")


# Singleton instance
aws_service = AWSService()
