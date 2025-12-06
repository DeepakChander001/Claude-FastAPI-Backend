import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_secrets_from_aws(secret_name: str, boto3_client: Optional[Any] = None) -> Dict[str, Any]:
    """
    Retrieves a secret from AWS Secrets Manager.
    
    Args:
        secret_name: The name of the secret to retrieve.
        boto3_client: Optional boto3 client instance. If None, attempts to create one.
                      Pass a mock client here for testing.
    
    Returns:
        A dictionary containing the parsed secret JSON, or an empty dict on error.
    """
    client = boto3_client
    
    if client is None:
        try:
            import boto3
            # In a real app, region_name might be configured or inferred
            client = boto3.client("secretsmanager")
        except ImportError:
            logger.warning("boto3 not installed. Cannot fetch secrets from AWS.")
            return {}
        except Exception as e:
            logger.error(f"Failed to create boto3 client: {e}")
            return {}

    try:
        # Example call:
        # response = client.get_secret_value(SecretId=secret_name)
        response = client.get_secret_value(SecretId=secret_name)
        
        if "SecretString" in response:
            return json.loads(response["SecretString"])
        else:
            logger.warning(f"Secret {secret_name} does not contain SecretString.")
            return {}
            
    except Exception as e:
        # Catch-all for ClientError, etc. to prevent app crash
        logger.error(f"Error retrieving secret {secret_name}: {e}")
        return {}
