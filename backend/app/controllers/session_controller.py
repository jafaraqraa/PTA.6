from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.session_manager import SessionManager
from app.schemas.attempt_schema import AttemptCreateDTO
from app.schemas.stored_threshold_schema import CreateStoredThresholdDTO
from app.schemas.final_interpretation_schema import EndSessionDTO

router = APIRouter()

@router.post("/startSession")
async def start_session(user_id: int, db: AsyncSession = Depends(get_db)):

    try:
        session = await SessionManager.start_session(db, user_id)
        return session
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from exc


@router.post("/playTone")
async def play_tone(dto: AttemptCreateDTO, db: AsyncSession = Depends(get_db)):

    try:
        result = await SessionManager.play_tone(
            db,
            dto
        )
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc) or "Bad request"
        ) from exc


@router.post("/storeTone")
async def store_tone(dto: CreateStoredThresholdDTO, db: AsyncSession = Depends(get_db)):
    
    try:
        threshold = await SessionManager.store_threshold(db, dto)
        return {
            "confirmation": "Tone stored successfully",
            "data": threshold
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc) or "Bad request"
        ) from exc

@router.post("/endSession")
async def end_session(dto: EndSessionDTO, db: AsyncSession = Depends(get_db)):
    try:
        results = await SessionManager.end_session(
            db,
            dto
        )
        return results
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc)
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc) or "Bad request"
        ) from exc
