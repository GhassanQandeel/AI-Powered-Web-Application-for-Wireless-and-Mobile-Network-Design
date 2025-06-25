import os
from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.v1.routes import router as api_router


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=env_path)

app = FastAPI()
app.include_router(api_router, prefix="/api/v1")
app.include_router(api_router, prefix="")   
@app.get("/")
def read_root():
    return {"message": "FastAPI is working!"}
