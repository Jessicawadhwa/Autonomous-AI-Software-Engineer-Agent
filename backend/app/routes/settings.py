import os
from fastapi import APIRouter, HTTPException
from backend.app.schemas.schemas import LLMSettings
from backend.app.config import settings

router = APIRouter(prefix="/api/settings", tags=["settings"])

# In-memory settings cache initialized from environment
current_settings = LLMSettings(
    provider=settings.DEFAULT_PROVIDER,
    openai_api_key=settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY"),
    openai_model=settings.OPENAI_MODEL,
    google_api_key=settings.GOOGLE_API_KEY or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"),
    gemini_model=settings.GEMINI_MODEL,
    temperature=settings.TEMPERATURE,
    max_tokens=settings.MAX_TOKENS,
    max_debug_iterations=settings.MAX_DEBUG_ITERATIONS,
    auto_approve=settings.AUTO_APPROVE_SAFE_COMMANDS
)

@router.get("", response_model=LLMSettings)
async def get_settings():
    # Mask secret API keys for secure UI display
    masked = current_settings.model_copy()
    if masked.openai_api_key:
        masked.openai_api_key = masked.openai_api_key[:4] + "..." + masked.openai_api_key[-4:] if len(masked.openai_api_key) > 8 else "***"
    if masked.google_api_key:
        masked.google_api_key = masked.google_api_key[:4] + "..." + masked.google_api_key[-4:] if len(masked.google_api_key) > 8 else "***"
    return masked

@router.post("", response_model=LLMSettings)
async def update_settings(payload: LLMSettings):
    global current_settings
    # If key wasn't altered (or masked), keep existing
    if payload.openai_api_key and "..." not in payload.openai_api_key and "***" not in payload.openai_api_key:
        current_settings.openai_api_key = payload.openai_api_key
    if payload.google_api_key and "..." not in payload.google_api_key and "***" not in payload.google_api_key:
        current_settings.google_api_key = payload.google_api_key

    current_settings.provider = payload.provider
    current_settings.openai_model = payload.openai_model
    current_settings.gemini_model = payload.gemini_model
    current_settings.temperature = payload.temperature
    current_settings.max_tokens = payload.max_tokens
    current_settings.max_debug_iterations = payload.max_debug_iterations
    current_settings.auto_approve = payload.auto_approve

    return await get_settings()

@router.post("/test-connection")
async def test_llm_connection(payload: LLMSettings):
    """Verifies that the chosen API key and provider work correctly."""
    if payload.provider == "demo":
        return {"success": True, "message": "Demo Mode is active and requires zero API keys."}
    
    if payload.provider == "openai":
        key = payload.openai_api_key or current_settings.openai_api_key
        if not key:
            raise HTTPException(status_code=400, detail="OpenAI API Key is required")
        try:
            import httpx
            headers = {"Authorization": f"Bearer {key}"}
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get("https://api.openai.com/v1/models", headers=headers)
                if res.status_code == 200:
                    return {"success": True, "message": "Successfully connected to OpenAI API!"}
                else:
                    raise HTTPException(status_code=400, detail=f"OpenAI error: {res.text}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

    if payload.provider == "gemini":
        key = payload.google_api_key or current_settings.google_api_key
        if not key:
            raise HTTPException(status_code=400, detail="Google Gemini API Key is required")
        try:
            import httpx
            url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url)
                if res.status_code == 200:
                    return {"success": True, "message": "Successfully connected to Google Gemini API!"}
                else:
                    raise HTTPException(status_code=400, detail=f"Gemini error: {res.text}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

    return {"success": True, "message": "Provider tested."}
