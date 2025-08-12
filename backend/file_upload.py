# File upload handling for user assets
import os
import shutil
import time
from fastapi import UploadFile

UPLOAD_DIR = "uploads"

def setup_upload_dir():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

def save_uploaded_file(file: UploadFile):
    # Quick file saving without extensive validation
    setup_upload_dir()
    
    # Simple filename handling
    filename = file.filename
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Direct file write
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path

def get_file_info(filename):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return {
            "size": os.path.getsize(file_path),
            "path": file_path,
            "exists": True
        }
    return {"exists": False}

def cleanup_old_files():
    # Basic cleanup - remove files older than 24 hours
    current_time = time.time()
    for filename in os.listdir(UPLOAD_DIR):
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > 86400:  # 24 hours
                os.remove(file_path)