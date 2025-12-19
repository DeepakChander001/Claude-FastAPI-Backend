"""
S3 Service - AWS S3 operations for workspace management.

Provides functions to:
- Upload files/directories to S3
- Download files/directories from S3
- List objects in S3 bucket
- Delete objects from S3
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class S3Service:
    """Service for interacting with AWS S3."""
    
    def __init__(
        self,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
        region: str = "eu-north-1",
        endpoint_url: Optional[str] = None
    ):
        self.bucket_name = bucket_name
        self.region = region
        
        # Initialize S3 client
        self.client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region,
            endpoint_url=endpoint_url
        )
        
        logger.info(f"S3Service initialized for bucket: {bucket_name}")
    
    def _get_user_prefix(self, user_id: str, project_name: str) -> str:
        """Get the S3 prefix for a user's project."""
        return f"users/{user_id}/{project_name}/"
    
    def upload_file(
        self,
        local_path: str,
        user_id: str,
        project_name: str,
        relative_path: str
    ) -> Dict[str, Any]:
        """Upload a single file to S3."""
        s3_key = f"{self._get_user_prefix(user_id, project_name)}{relative_path}"
        
        try:
            self.client.upload_file(local_path, self.bucket_name, s3_key)
            logger.info(f"Uploaded: {local_path} -> s3://{self.bucket_name}/{s3_key}")
            return {"success": True, "s3_key": s3_key}
        except ClientError as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            return {"success": False, "error": str(e)}
    
    def upload_content(
        self,
        content: str,
        user_id: str,
        project_name: str,
        relative_path: str
    ) -> Dict[str, Any]:
        """Upload content directly to S3 (for sync operations)."""
        s3_key = f"{self._get_user_prefix(user_id, project_name)}{relative_path}"
        
        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content.encode('utf-8')
            )
            logger.info(f"Synced content -> s3://{self.bucket_name}/{s3_key}")
            return {"success": True, "s3_key": s3_key}
        except ClientError as e:
            logger.error(f"Failed to sync content: {e}")
            return {"success": False, "error": str(e)}
    
    def upload_directory(
        self,
        local_dir: str,
        user_id: str,
        project_name: str,
        exclude_patterns: List[str] = None
    ) -> Dict[str, Any]:
        """Upload an entire directory to S3."""
        if exclude_patterns is None:
            exclude_patterns = ['.git', '__pycache__', 'node_modules', '.env', 'venv', '.venv']
        
        uploaded_files = []
        failed_files = []
        local_path = Path(local_dir)
        
        for file_path in local_path.rglob('*'):
            if file_path.is_file():
                # Check exclusions
                should_exclude = False
                for pattern in exclude_patterns:
                    if pattern in str(file_path):
                        should_exclude = True
                        break
                
                if should_exclude:
                    continue
                
                relative_path = file_path.relative_to(local_path)
                result = self.upload_file(
                    str(file_path),
                    user_id,
                    project_name,
                    str(relative_path).replace('\\', '/')
                )
                
                if result["success"]:
                    uploaded_files.append(str(relative_path))
                else:
                    failed_files.append({"path": str(relative_path), "error": result["error"]})
        
        return {
            "success": len(failed_files) == 0,
            "uploaded_count": len(uploaded_files),
            "failed_count": len(failed_files),
            "uploaded_files": uploaded_files,
            "failed_files": failed_files,
            "s3_prefix": self._get_user_prefix(user_id, project_name)
        }
    
    def download_file(
        self,
        user_id: str,
        project_name: str,
        relative_path: str
    ) -> Dict[str, Any]:
        """Download a file's content from S3."""
        s3_key = f"{self._get_user_prefix(user_id, project_name)}{relative_path}"
        
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            return {"success": True, "content": content, "s3_key": s3_key}
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return {"success": False, "error": "File not found"}
            logger.error(f"Failed to download {s3_key}: {e}")
            return {"success": False, "error": str(e)}
    
    def list_objects(
        self,
        user_id: str,
        project_name: str,
        path: str = ""
    ) -> Dict[str, Any]:
        """List objects in a directory (prefix)."""
        prefix = f"{self._get_user_prefix(user_id, project_name)}{path}"
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            objects = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                relative_key = key.replace(self._get_user_prefix(user_id, project_name), '')
                objects.append({
                    "path": relative_key,
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat()
                })
            
            return {
                "success": True,
                "objects": objects,
                "count": len(objects)
            }
        except ClientError as e:
            logger.error(f"Failed to list objects: {e}")
            return {"success": False, "error": str(e)}
    
    def delete_object(
        self,
        user_id: str,
        project_name: str,
        relative_path: str
    ) -> Dict[str, Any]:
        """Delete an object from S3."""
        s3_key = f"{self._get_user_prefix(user_id, project_name)}{relative_path}"
        
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Deleted: s3://{self.bucket_name}/{s3_key}")
            return {"success": True, "s3_key": s3_key}
        except ClientError as e:
            logger.error(f"Failed to delete {s3_key}: {e}")
            return {"success": False, "error": str(e)}
    
    def list_user_projects(self, user_id: str) -> Dict[str, Any]:
        """List all projects for a user."""
        prefix = f"users/{user_id}/"
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                Delimiter='/'
            )
            
            projects = []
            for cp in response.get('CommonPrefixes', []):
                project_path = cp['Prefix']
                project_name = project_path.replace(prefix, '').rstrip('/')
                projects.append(project_name)
            
            return {"success": True, "projects": projects}
        except ClientError as e:
            logger.error(f"Failed to list projects: {e}")
            return {"success": False, "error": str(e)}


# Singleton instance
_s3_service: Optional[S3Service] = None


def get_s3_service() -> Optional[S3Service]:
    """Get or create S3 service instance."""
    global _s3_service
    
    if _s3_service is None:
        access_key = os.environ.get("AWS_ACCESS_KEY_ID")
        secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        bucket = os.environ.get("S3_BUCKET_NAME")
        region = os.environ.get("AWS_REGION", "eu-north-1")
        endpoint = os.environ.get("S3_ENDPOINT")
        
        if not all([access_key, secret_key, bucket]):
            logger.warning("S3 credentials not configured")
            return None
        
        _s3_service = S3Service(
            access_key_id=access_key,
            secret_access_key=secret_key,
            bucket_name=bucket,
            region=region,
            endpoint_url=endpoint
        )
    
    return _s3_service
