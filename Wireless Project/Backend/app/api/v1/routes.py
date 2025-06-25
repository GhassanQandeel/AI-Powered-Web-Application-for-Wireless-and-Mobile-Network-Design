from fastapi import APIRouter, Query
from app.core.ai_agent import ask_gemini

router = APIRouter()

@router.get("/ai")
def ask(prompt: str = Query(..., description="Prompt to Gemini")):
    response = ask_gemini(prompt)
    return {"gemini_response": response}
