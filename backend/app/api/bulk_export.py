"""Bulk export endpoint — process and download multiple CVs."""
from __future__ import annotations

import asyncio
import os
import zipfile
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.models.requests import ExportRequest
from app.services.bulk_service import BulkService, BULK_OUTPUT_DIR

logger = logging.getLogger(__name__)
router = APIRouter()
bulk_service = BulkService()


class BulkExportRequest:
    """Request for bulk export."""
    def __init__(self, bulk_id: str, format: str = "pdf", template_id: str = "ntt-classic", language: str = "en"):
        self.bulkId = bulk_id
        self.format = format
        self.templateId = template_id
        self.language = language


@router.post("/export/bulk")
async def request_bulk_export(body: dict):
    """Start bulk export processing.
    
    Args:
        body: {
            "bulkId": str,
            "format": str (pdf, docx, json, pptx),
            "templateId": str,
            "language": str
        }
        
    Returns:
        Job status and download URL
    """
    bulk_id = body.get("bulkId")
    format = body.get("format", "pdf")
    template_id = body.get("templateId", "ntt-classic")
    language = body.get("language", "en")
    
    logger.info(f"🔵 [Start Bulk Export] Request received with parameters: bulkId={bulk_id}, format={format}, templateId={template_id}, language={language}")
    
    if not bulk_id:
        logger.error("❌ [Start Bulk Export] bulkId is required but missing")
        raise HTTPException(status_code=400, detail="bulkId is required")
    
    # Get bulk job
    bulk_job = bulk_service.get_bulk_job(bulk_id)
    if not bulk_job:
        logger.error(f"❌ [Start Bulk Export] Bulk job {bulk_id} not found")
        raise HTTPException(status_code=404, detail=f"Bulk job {bulk_id} not found")
    
    logger.info(f"📋 [Start Bulk Export] Found bulk job: totalFiles={bulk_job['totalFiles']}")
    
    # Update job parameters
    bulk_job["format"] = format
    bulk_job["templateId"] = template_id
    bulk_job["language"] = language
    
    logger.info(f"🔄 [Start Bulk Export] Starting async processing task for bulkId={bulk_id}")
    
    # Start async processing (fire and forget)
    asyncio.create_task(bulk_service.process_bulk_job(bulk_id))
    
    logger.info(f"✅ [Start Bulk Export] Async job created, returning response")
    
    return {
        "bulkId": bulk_id,
        "status": "processing",
        "totalFiles": bulk_job["totalFiles"],
        "processedFiles": 0,
    }


@router.get("/export/bulk/{bulk_id}/status")
async def get_bulk_export_status(bulk_id: str):
    """Get status of bulk export job.
    
    Args:
        bulk_id: Bulk job ID
        
    Returns:
        Job status
    """
    logger.info(f"🔍 [Get Bulk Status] Status query for bulkId={bulk_id}")
    
    bulk_job = bulk_service.get_bulk_job(bulk_id)
    if not bulk_job:
        logger.error(f"❌ [Get Bulk Status] Bulk job {bulk_id} not found")
        raise HTTPException(status_code=404, detail=f"Bulk job {bulk_id} not found")
    
    status_info = {
        "bulkId": bulk_id,
        "status": bulk_job["status"],
        "totalFiles": bulk_job["totalFiles"],
        "processedFiles": bulk_job["processedFiles"],
        "failedFiles": bulk_job["failedFiles"],
        "completedAt": bulk_job["completedAt"],
        "downloadUrl": bulk_job.get("downloadUrl"),
    }
    
    logger.info(f"📊 [Get Bulk Status] Current status: {status_info}")
    
    return status_info


@router.get("/download/bulk/{bulk_id}")
async def download_bulk_files(bulk_id: str):
    """Download all processed CVs as a zip file.
    
    Args:
        bulk_id: Bulk job ID
        
    Returns:
        Zip file containing all processed CVs
    """
    logger.info(f"📥 [Download Bulk] Download request for bulkId={bulk_id}")
    
    bulk_job = bulk_service.get_bulk_job(bulk_id)
    if not bulk_job:
        logger.error(f"❌ [Download Bulk] Bulk job {bulk_id} not found")
        raise HTTPException(status_code=404, detail=f"Bulk job {bulk_id} not found")
    
    if bulk_job["status"] != "completed":
        logger.error(f"❌ [Download Bulk] Bulk job {bulk_id} status is {bulk_job['status']}, not completed")
        raise HTTPException(status_code=400, detail=f"Bulk job {bulk_id} is not yet completed (status: {bulk_job['status']})")
    
    logger.info(f"✅ [Download Bulk] Bulk job {bulk_id} is completed, generating ZIP file")
    
    # Get zip file path
    zip_path = bulk_service.get_all_bulk_files_zip_path(bulk_id)
    
    if not os.path.exists(zip_path):
        logger.error(f"❌ [Download Bulk] ZIP file not found at {zip_path}")
        raise HTTPException(status_code=500, detail="Zip file not found")
    
    file_size = os.path.getsize(zip_path)
    logger.info(f"📦 [Download Bulk] ZIP file ready: {zip_path}, size={file_size} bytes")
    zip_filename = bulk_service.get_bulk_zip_filename(bulk_job.get("format", "pdf"))
    
    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_filename,
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'}
    )


@router.delete("/export/bulk/{bulk_id}")
async def cleanup_bulk_job(bulk_id: str):
    """Delete a bulk job and its files.
    
    Args:
        bulk_id: Bulk job ID
    """
    logger.info(f"🗑️  [Cleanup Bulk] Cleanup request for bulkId={bulk_id}")
    
    bulk_job = bulk_service.get_bulk_job(bulk_id)
    if not bulk_job:
        logger.error(f"❌ [Cleanup Bulk] Bulk job {bulk_id} not found")
        raise HTTPException(status_code=404, detail=f"Bulk job {bulk_id} not found")
    
    logger.info(f"🔄 [Cleanup Bulk] Deleting bulk job files and records for bulkId={bulk_id}")
    bulk_service.cleanup_bulk_job(bulk_id)
    
    logger.info(f"✅ [Cleanup Bulk] Bulk job {bulk_id} cleaned up successfully")
    
    return {
        "bulkId": bulk_id,
        "status": "deleted"
    }
