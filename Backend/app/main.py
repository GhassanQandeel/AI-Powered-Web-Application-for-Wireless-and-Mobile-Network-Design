import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

from app.api.v1.routes import router as api_router

# Paths
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))  # .../Backend/app
BASE_DIR = os.path.dirname(BACKEND_DIR)  # .../Backend
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # .../ProjectWireless (root)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "Frontend")
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# CORS Middleware for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (like /static/images/Aws.jpg)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# Include API routes
app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router, prefix="")  # Optional alias

# Route for welcome.html as homepage
@app.get("/")
def serve_welcome():
    return FileResponse(os.path.join(FRONTEND_DIR, "welcome.html"), media_type="text/html")

# Route for index.html (start button target)
@app.get("/index.html")
def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"), media_type="text/html")
