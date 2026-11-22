from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from app.core.database import get_db
from app.services.translation_service import translation_service
from app.api.v1.schemas import TranslateRequest, TranslateResponse
from app.db.repositories.session_repo import SessionRepository
from app.api.deps import get_optional_user
from app.db.models.user import User

router = APIRouter(prefix="/translation", tags=["Intelligent Translation Engine"])

@router.post("/process", response_model=TranslateResponse)
async def process_translation(
    request: TranslateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """
    Translates a sequence of sign tokens into formatted, punctuated text with autocorrect and suggestions.
    """
    result = translation_service.assemble_sentence(request.tokens)

    # If session provided and sentence changed, store in translation history
    if request.session_id and result["sentence"] and result["sentence"] != request.current_sentence:
        repo = SessionRepository(db)
        await repo.add_translation(
            session_id=request.session_id,
            raw_tokens=" ".join(request.tokens),
            translated_sentence=result["sentence"]
        )

    return {
        "sentence": result["sentence"],
        "current_word": result["current_word"],
        "suggestions": result["suggestions"],
        "is_valid_word": result["is_valid_word"],
        "tts_text": result["tts_text"]
    }

@router.get("/suggestions")
async def get_word_suggestions(word: str):
    """
    Returns live completion and autocorrect candidates for the word being signed.
    """
    suggestions = translation_service.get_suggestions(word)
    return {"word": word, "suggestions": suggestions}
