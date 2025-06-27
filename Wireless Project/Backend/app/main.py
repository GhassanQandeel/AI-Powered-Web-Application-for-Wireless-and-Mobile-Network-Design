import os
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi.staticfiles import StaticFiles

from app.api.v1.routes import router as api_router


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI()
#app.mount("/", StaticFiles(directory="../frontend", html=True), name="static")
# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router, prefix="")   
@app.get("/")
def read_root():
    frontend_path = os.path.join(BASE_DIR, "..", "Frontend", "index.html")
    return FileResponse(os.path.abspath(frontend_path), media_type="text/html")

