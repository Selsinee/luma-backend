# app/routers/study.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/study",
    tags=["Study"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/sessions", response_model=schemas.StudySession, operation_id="log_study_session")
def create_study_session(
    session: schemas.StudySessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Records the completion of a study session (flashcard or quiz).
    """
    # Verify the user owns the deck they are studying
    db_deck = crud.get_deck(db, deck_id=session.deck_id)
    if not db_deck or db_deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to study this deck")
        
    return crud.create_study_session(db=db, session=session, user_id=current_user.id)


@router.put("/progress/{word_id}", response_model=schemas.UserWordProgress, operation_id="update_word_progress")
def update_word_progress(
    word_id: str,
    progress: schemas.UserWordProgressUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Updates the user's progress for a single word (e.g., marks it as "mastered").
    """
    db_word = crud.get_word(db, word_id=word_id)
    if not db_word:
        raise HTTPException(status_code=404, detail="Word not found")

    # Verify the user owns the deck this word belongs to
    if db_word.deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update progress for this word")

    return crud.update_word_progress(db=db, word_id=word_id, user_id=current_user.id, progress_update=progress)