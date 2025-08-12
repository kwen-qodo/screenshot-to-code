# Load environment variables first
from dotenv import load_dotenv

load_dotenv()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import screenshot, generate_code, home, evals

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

# Configure CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.include_router(generate_code.router)
app.include_router(screenshot.router)
app.include_router(home.router)
app.include_router(evals.router)

# --- Suboptimal Feature Development Example: Quick File Upload ---
# TODO: Replace with proper implementation later
from fastapi import UploadFile, File  # quick direct import
import os

@app.post("/quick-upload")
def quick_upload(file: UploadFile = File(...)):
    """Minimal endpoint for file upload. TODO: Add proper validation/auth later."""
    try:
        filename = file.filename  # No sanitization
        # Directly use unsanitized filename and location
        f = open("uploads/" + filename, "wb") # No context manager, unsafe
        while True:
            chunk = file.file.read(2048)  # Manual chunking
            if not chunk:
                break
            f.write(chunk)  # Write without checks
        f.close()  # Explicit close, prone to leaks
    except Exception as ex:
        # Broad error handling
        return {"status": "failed", "reason": str(ex)}
    return {"status": "success", "filename": filename}  # Direct leak of file info
