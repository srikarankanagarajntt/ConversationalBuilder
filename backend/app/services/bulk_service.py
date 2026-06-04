"""Bulk processing service — handles multiple CV processing asynchronously."""
from __future__ import annotations

import asyncio
import json
import os
import uuid
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.cv_schema import CvSchema
from app.services.export_service import ExportService

logger = logging.getLogger(__name__)

# In-memory bulk job store
_bulk_jobs: Dict[str, Dict[str, Any]] = {}

# Bulk output directory
BULK_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "exports", "bulk")
os.makedirs(BULK_OUTPUT_DIR, exist_ok=True)


class BulkService:
    """Service for managing bulk CV processing."""
    
    def __init__(self):
        self.export_service = ExportService()

    @staticmethod
    def get_bulk_zip_filename(format: str) -> str:
        """Return the user-facing ZIP filename for a bulk export format."""
        normalized_format = (format or "pdf").lower()
        format_label = "ppt" if normalized_format == "pptx" else normalized_format
        return f"CV_NTTdata_{format_label}.zip"

    @staticmethod
    def _sanitize_filename_part(value: Any, fallback: str) -> str:
        """Sanitize one filename component for safe download names."""
        text = str(value or "").strip().lower()
        text = re.sub(r"[^a-z0-9]+", "_", text)
        text = re.sub(r"_+", "_", text).strip("_")
        return text or fallback

    def _build_employee_filename(self, cv: CvSchema, extension: str) -> str:
        """Build firstname_lastname_role filename without random IDs."""
        personal_info = getattr(cv, "personalInfo", None)
        full_name = getattr(personal_info, "fullName", "") if personal_info else ""
        role = getattr(personal_info, "role", "") if personal_info else ""

        if not role:
            header = getattr(cv, "header", {}) or {}
            role = header.get("jobTitle", "") if isinstance(header, dict) else ""

        name_parts = [part for part in str(full_name or "").split() if part]
        first_name = name_parts[0] if name_parts else "unknown"
        last_name = name_parts[-1] if len(name_parts) > 1 else "employee"

        safe_first_name = self._sanitize_filename_part(first_name, "unknown")
        safe_last_name = self._sanitize_filename_part(last_name, "employee")
        safe_role = self._sanitize_filename_part(role, "role")
        safe_extension = self._sanitize_filename_part(extension, "pdf")

        return f"{safe_first_name}_{safe_last_name}_{safe_role}.{safe_extension}"
    
    def create_bulk_job(self, cv_list: List[CvSchema], template_id: str = "ntt-classic", language: str = "en", format: str = "pdf") -> Dict[str, Any]:
        """Create a new bulk processing job.
        
        Args:
            cv_list: List of CV schemas to process
            template_id: Template identifier
            language: Language code for export
            format: Export format (pdf, docx, json, pptx)
            
        Returns:
            Bulk job record
        """
        bulk_id = str(uuid.uuid4())
        job_files: Dict[str, Dict[str, Any]] = {}
        
        # Create file records for each CV
        for idx, cv in enumerate(cv_list):
            file_id = str(uuid.uuid4())
            job_files[file_id] = {
                "fileId": file_id,
                "cvName": cv.personalInfo.fullName if cv.personalInfo else f"CV_{idx}",
                "format": format,
                "status": "pending",  # pending, processing, completed, error
                "filePath": None,
                "errorMessage": None,
                "createdAt": datetime.now().isoformat(),
            }
        
        bulk_job = {
            "bulkId": bulk_id,
            "files": job_files,
            "cvList": cv_list,
            "templateId": template_id,
            "language": language,
            "format": format,
            "status": "pending",  # pending, processing, completed, error
            "totalFiles": len(cv_list),
            "processedFiles": 0,
            "failedFiles": 0,
            "createdAt": datetime.now().isoformat(),
            "completedAt": None,
            "downloadUrl": None,
        }
        
        _bulk_jobs[bulk_id] = bulk_job
        return bulk_job
    
    def get_bulk_job(self, bulk_id: str) -> Optional[Dict[str, Any]]:
        """Get a bulk job by ID."""
        return _bulk_jobs.get(bulk_id)
    
    async def process_bulk_job(self, bulk_id: str) -> Dict[str, Any]:
        """Process all CVs in a bulk job asynchronously in parallel.
        
        Args:
            bulk_id: Bulk job ID
            
        Returns:
            Updated bulk job record
        """
        logger.info(f"🔵 [Process Bulk] Starting bulk processing for bulkId={bulk_id}")
        
        bulk_job = self.get_bulk_job(bulk_id)
        if not bulk_job:
            logger.error(f"❌ [Process Bulk] Bulk job {bulk_id} not found")
            raise ValueError(f"Bulk job {bulk_id} not found")
        
        logger.info(f"📊 [Process Bulk] Job details: totalFiles={bulk_job['totalFiles']}, format={bulk_job['format']}, templateId={bulk_job['templateId']}")
        
        bulk_job["status"] = "processing"
        
        # Process all CVs in parallel
        tasks = []
        for file_id, cv in zip(bulk_job["files"].keys(), bulk_job["cvList"]):
            task = self._process_cv_file(bulk_id, file_id, cv, bulk_job["templateId"], bulk_job["language"], bulk_job["format"])
            tasks.append(task)
        
        logger.info(f"⏳ [Process Bulk] Created {len(tasks)} processing tasks, starting parallel execution...")
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"🔍 [Process Bulk] All tasks completed, analyzing results...")
        
        # Update job statistics
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                bulk_job["failedFiles"] += 1
                logger.error(f"❌ [Process Bulk] Task {idx} failed: {str(result)}")
            else:
                bulk_job["processedFiles"] += 1
                logger.info(f"✅ [Process Bulk] Task {idx} completed successfully")
        
        # Mark job as completed
        bulk_job["status"] = "completed"
        bulk_job["completedAt"] = datetime.now().isoformat()
        bulk_job["downloadUrl"] = f"/api/download/bulk/{bulk_id}"
        
        logger.info(f"✅ [Process Bulk] Bulk job {bulk_id} completed: processed={bulk_job['processedFiles']}, failed={bulk_job['failedFiles']}")
        
        return bulk_job
    
    async def _process_cv_file(self, bulk_id: str, file_id: str, cv: CvSchema, template_id: str, language: str, format: str) -> str:
        """Process a single CV file in a bulk job.
        
        Args:
            bulk_id: Bulk job ID
            file_id: File ID within the bulk job
            cv: CV schema to export
            template_id: Template ID
            language: Language code
            format: Export format
            
        Returns:
            File path on success
        """
        logger.info(f"🔄 [Process CV File] Processing fileId={file_id} with format={format}, templateId={template_id}")
        
        bulk_job = self.get_bulk_job(bulk_id)
        file_record = bulk_job["files"][file_id]
        
        try:
            file_record["status"] = "processing"
            logger.info(f"📝 [Process CV File] Exporting CV: {file_record.get('cvName', file_id)}")
            
            # Create temporary export job
            export_job = await self.export_service.create_export_job(cv, format, template_id, language)
            
            logger.info(f"✅ [Process CV File] Export job created: {export_job.get('filename')}")
            
            # Move file to bulk directory with deterministic employee filename
            export_path = export_job["filePath"]
            extension = os.path.splitext(export_path)[1].lstrip(".") or format
            employee_filename = self._build_employee_filename(cv, extension)
            bulk_file_path = os.path.join(BULK_OUTPUT_DIR, bulk_id, employee_filename)
            os.makedirs(os.path.dirname(bulk_file_path), exist_ok=True)

            # Avoid overwriting if two CVs have the same employee name/role.
            base_path, ext = os.path.splitext(bulk_file_path)
            duplicate_index = 2
            while os.path.exists(bulk_file_path):
                bulk_file_path = f"{base_path}_{duplicate_index}{ext}"
                duplicate_index += 1
            
            # Copy file
            logger.info(f"📂 [Process CV File] Copying file to bulk directory: {bulk_file_path}")
            with open(export_path, "rb") as src:
                with open(bulk_file_path, "wb") as dst:
                    dst.write(src.read())
            
            file_record["filePath"] = bulk_file_path
            file_record["downloadFilename"] = os.path.basename(bulk_file_path)
            file_record["status"] = "completed"
            
            logger.info(f"✅ [Process CV File] File processing completed: {file_id}")
            return bulk_file_path
            
        except Exception as e:
            file_record["status"] = "error"
            file_record["errorMessage"] = str(e)
            logger.error(f"❌ [Process CV File] Error processing fileId={file_id}: {str(e)}")
            raise
    
    def get_bulk_files(self, bulk_id: str) -> List[tuple[str, str]]:
        """Get list of processed files for a bulk job.
        
        Args:
            bulk_id: Bulk job ID
            
        Returns:
            List of (file_path, filename) tuples
        """
        bulk_job = self.get_bulk_job(bulk_id)
        if not bulk_job:
            raise ValueError(f"Bulk job {bulk_id} not found")
        
        files = []
        bulk_dir = os.path.join(BULK_OUTPUT_DIR, bulk_id)
        
        if os.path.exists(bulk_dir):
            for file_record in bulk_job["files"].values():
                if file_record["status"] == "completed" and file_record["filePath"]:
                    filename = file_record.get("downloadFilename") or os.path.basename(file_record["filePath"])
                    files.append((file_record["filePath"], filename))
        
        return files
    
    def get_all_bulk_files_zip_path(self, bulk_id: str) -> str:
        """Get path to zip file containing all processed CVs.
        
        Args:
            bulk_id: Bulk job ID
            
        Returns:
            Path to zip file
        """
        import zipfile
        
        logger.info(f"📦 [Create ZIP] Creating ZIP file for bulkId={bulk_id}")
        
        bulk_job = self.get_bulk_job(bulk_id)
        if not bulk_job:
            logger.error(f"❌ [Create ZIP] Bulk job {bulk_id} not found")
            raise ValueError(f"Bulk job {bulk_id} not found")
        
        zip_filename = self.get_bulk_zip_filename(bulk_job.get("format", "pdf"))
        zip_path = os.path.join(BULK_OUTPUT_DIR, bulk_id, zip_filename)
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)

        # Always recreate ZIP so file names reflect the selected format/template run.
        logger.info(f"📝 [Create ZIP] Creating ZIP file with filename: {zip_filename}")
        files = self.get_bulk_files(bulk_id)
        logger.info(f"📂 [Create ZIP] Found {len(files)} processed files to ZIP")

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            used_names: set[str] = set()
            for idx, (file_path, filename) in enumerate(files):
                if os.path.exists(file_path):
                    arcname = filename
                    base_name, extension = os.path.splitext(arcname)
                    duplicate_index = 2
                    while arcname in used_names:
                        arcname = f"{base_name}_{duplicate_index}{extension}"
                        duplicate_index += 1
                    used_names.add(arcname)

                    logger.info(f"🗜️  [Create ZIP] Adding file {idx+1}/{len(files)}: {arcname}")
                    zipf.write(file_path, arcname=arcname)

        zip_size = os.path.getsize(zip_path)
        logger.info(f"✅ [Create ZIP] ZIP file created successfully: {zip_path}, size={zip_size} bytes")
        
        return zip_path
    
    def cleanup_bulk_job(self, bulk_id: str) -> None:
        """Clean up bulk job files and records.
        
        Args:
            bulk_id: Bulk job ID
        """
        import shutil
        
        bulk_dir = os.path.join(BULK_OUTPUT_DIR, bulk_id)
        zip_path = os.path.join(BULK_OUTPUT_DIR, f"{bulk_id}.zip")
        
        # Remove directories and files
        if os.path.exists(bulk_dir):
            shutil.rmtree(bulk_dir)
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        # Remove job record
        if bulk_id in _bulk_jobs:
            del _bulk_jobs[bulk_id]
