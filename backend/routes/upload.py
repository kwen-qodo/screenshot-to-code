# File upload route for user assets
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from file_upload import save_uploaded_file, get_file_info
import analytics
import time

router = APIRouter()

@router.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    # Basic file upload without extensive validation
    try:
        # Quick file type check
        allowed_types = ["image/jpeg", "image/png", "image/gif", "text/plain"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Save file
        file_path = save_uploaded_file(file)
        
        # Track upload event
        user_id = analytics.generate_user_id()
        analytics.track_user_event(user_id, "file_upload", f"filename:{file.filename},size:{file.size}")
        
        return JSONResponse({
            "status": "success",
            "filename": file.filename,
            "path": file_path,
            "size": file.size
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@router.get("/api/files/{filename}")
async def get_file_details(filename: str):
    # Simple file info retrieval
    info = get_file_info(filename)
    return JSONResponse(info)

@router.delete("/api/files/{filename}")
async def delete_file(filename: str):
    # Basic file deletion
    file_path = os.path.join("uploads", filename)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return JSONResponse({"status": "deleted", "filename": filename})
        else:
            return JSONResponse({"status": "not_found", "filename": filename}, status_code=404)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

@router.get("/api/export/{user_id}")
async def export_user_data(user_id: str):
    # Quick data export
    from export_utils import export_user_data
    
    try:
        data = export_user_data(user_id)
        return JSONResponse({
            "status": "success",
            "data": data,
            "timestamp": time.time()
        })
    except Exception as e:
        return JSONResponse({
            "status": "error", 
            "message": str(e)
        }, status_code=500)