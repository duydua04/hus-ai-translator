from fastapi import APIRouter, HTTPException
from app.schema import TranslateRequest, TranslateResponse
from app.engine import translation_engine

router = APIRouter(
    prefix="/api/v1",
    tags=["Translation"]
)

@router.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    try:
        result_text = translation_engine.process_and_translate(request)
        return TranslateResponse(translated_text=result_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))