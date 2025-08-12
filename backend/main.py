# Load environment variables first
from dotenv import load_dotenv

load_dotenv()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import screenshot, generate_code, home, evals, upload
import analytics
from file_upload import setup_upload_dir
import time

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

# Configure CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Quick startup tasks
setup_upload_dir()

# Add routes
app.include_router(generate_code.router)
app.include_router(screenshot.router)
app.include_router(home.router)
app.include_router(evals.router)
app.include_router(upload.router)

# Basic health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}

# Simple analytics endpoint
@app.get("/analytics/{user_id}")
def get_analytics(user_id: str):
    stats = analytics.get_user_stats(user_id)
    return {"user_id": user_id, "events": stats}
