"""
Workspace API - Endpoints for S3 project workspace management.

Provides:
- Project initialization (upload to S3)
- Project listing
- File sync operations
- File read/write operations
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field

from src.app.services.s3_service import get_s3_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["workspace"])


# ============ Request/Response Models ============

class FileUpload(BaseModel):
    """Single file to upload."""
    path: str = Field(..., description="Relative path within the project")
    content: str = Field(..., description="File content (base64 or text)")


class InitProjectRequest(BaseModel):
    """Request to initialize a project in S3 with files."""
    project_name: str = Field(..., description="Name of the project")
    files: List[FileUpload] = Field(..., description="List of files to upload")


class InitProjectResponse(BaseModel):
    """Response after initializing a project."""
    success: bool
    project_name: str
    s3_prefix: str
    uploaded_count: int
    failed_count: int
    message: str


class SyncFileRequest(BaseModel):
    """Request to sync a file to S3."""
    project_name: str
    file_path: str = Field(..., description="Relative path within the project")
    content: str = Field(..., description="File content")
    action: str = Field("update", description="create, update, or delete")


class FileContentResponse(BaseModel):
    """Response with file content from S3."""
    success: bool
    path: str
    content: Optional[str] = None
    error: Optional[str] = None


class ProjectListResponse(BaseModel):
    """Response with list of user's projects."""
    success: bool
    projects: List[str]
    count: int


class DirectoryListResponse(BaseModel):
    """Response with directory listing from S3."""
    success: bool
    path: str
    objects: List[Dict[str, Any]]
    count: int


# ============ Helper Functions ============

def get_user_id_from_token(authorization: str = None) -> str:
    """Extract user ID from authorization token."""
    if authorization and "nexus-dev-token" in authorization:
        return "dev-user-001"
    return "default-user"


# ============ Endpoints ============

@router.post("/init", response_model=InitProjectResponse)
async def init_project(
    request: InitProjectRequest,
    authorization: str = Header(None)
):
    """
    Initialize a new project by receiving files from CLI and uploading to S3.
    
    The CLI sends all file contents directly - no local path access needed.
    """
    s3 = get_s3_service()
    if not s3:
        raise HTTPException(status_code=500, detail="S3 service not configured")
    
    user_id = get_user_id_from_token(authorization)
    
    logger.info(f"Initializing project: {request.project_name} for user: {user_id} with {len(request.files)} files")
    
    uploaded_count = 0
    failed_count = 0
    
    for file in request.files:
        result = s3.upload_content(
            content=file.content,
            user_id=user_id,
            project_name=request.project_name,
            relative_path=file.path
        )
        if result["success"]:
            uploaded_count += 1
        else:
            failed_count += 1
            logger.error(f"Failed to upload {file.path}: {result.get('error')}")
    
    s3_prefix = s3._get_user_prefix(user_id, request.project_name)
    
    return InitProjectResponse(
        success=failed_count == 0,
        project_name=request.project_name,
        s3_prefix=s3_prefix,
        uploaded_count=uploaded_count,
        failed_count=failed_count,
        message=f"Uploaded {uploaded_count} files to S3" if failed_count == 0 else f"Uploaded {uploaded_count}, failed {failed_count}"
    )


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(authorization: str = Header(None)):
    """List all projects for the current user."""
    s3 = get_s3_service()
    if not s3:
        raise HTTPException(status_code=500, detail="S3 service not configured")
    
    user_id = get_user_id_from_token(authorization)
    result = s3.list_user_projects(user_id)
    
    return ProjectListResponse(
        success=result["success"],
        projects=result.get("projects", []),
        count=len(result.get("projects", []))
    )


@router.post("/sync")
async def sync_file(
    request: SyncFileRequest,
    authorization: str = Header(None)
):
    """Sync a file change to S3 (create, update, or delete)."""
    s3 = get_s3_service()
    if not s3:
        raise HTTPException(status_code=500, detail="S3 service not configured")
    
    user_id = get_user_id_from_token(authorization)
    
    if request.action == "delete":
        result = s3.delete_object(user_id, request.project_name, request.file_path)
    else:
        result = s3.upload_content(
            content=request.content,
            user_id=user_id,
            project_name=request.project_name,
            relative_path=request.file_path
        )
    
    return {
        "success": result["success"],
        "action": request.action,
        "path": request.file_path,
        "s3_key": result.get("s3_key"),
        "error": result.get("error")
    }


@router.get("/file", response_model=FileContentResponse)
async def get_file(
    project_name: str,
    path: str,
    authorization: str = Header(None)
):
    """Read a file from S3."""
    s3 = get_s3_service()
    if not s3:
        raise HTTPException(status_code=500, detail="S3 service not configured")
    
    user_id = get_user_id_from_token(authorization)
    result = s3.download_file(user_id, project_name, path)
    
    return FileContentResponse(
        success=result["success"],
        path=path,
        content=result.get("content"),
        error=result.get("error")
    )


@router.get("/ls", response_model=DirectoryListResponse)
async def list_directory(
    project_name: str,
    path: str = "",
    authorization: str = Header(None)
):
    """List files in a directory from S3."""
    s3 = get_s3_service()
    if not s3:
        raise HTTPException(status_code=500, detail="S3 service not configured")
    
    user_id = get_user_id_from_token(authorization)
    result = s3.list_objects(user_id, project_name, path)
    
    return DirectoryListResponse(
        success=result["success"],
        path=path,
        objects=result.get("objects", []),
        count=result.get("count", 0)
    )


@router.get("/status")
async def workspace_status(
    project_name: str,
    authorization: str = Header(None)
):
    """Get workspace status - total files, last sync time, etc."""
    s3 = get_s3_service()
    if not s3:
        raise HTTPException(status_code=500, detail="S3 service not configured")
    
    user_id = get_user_id_from_token(authorization)
    result = s3.list_objects(user_id, project_name)
    
    if result["success"]:
        objects = result.get("objects", [])
        last_modified = None
        if objects:
            last_modified = max(obj["last_modified"] for obj in objects)
        
        return {
            "success": True,
            "project_name": project_name,
            "user_id": user_id,
            "total_files": len(objects),
            "last_modified": last_modified,
            "s3_bucket": s3.bucket_name,
            "s3_prefix": s3._get_user_prefix(user_id, project_name)
        }
    
    return {"success": False, "error": result.get("error")}
