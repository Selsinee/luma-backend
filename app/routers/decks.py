# app/routers/decks.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal
from app.models import DifficultyEnum, StatusEnum
from app.routers.auth import get_current_active_user

router = APIRouter(
    prefix="/decks",
    tags=["Decks"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.Deck, operation_id="create_deck")
def create_deck(
    deck: schemas.DeckCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Creates a new deck for the authenticated user.
    """
    return crud.create_deck(db=db, deck=deck, user_id=current_user.id)


@router.get("/", response_model=List[schemas.Deck], operation_id="get_decks_by_user")
def read_decks_for_user(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Gets a list of all decks created by the authenticated user.
    Can be filtered by category.
    """
    return crud.get_decks_by_user(db, user_id=current_user.id, category=category)


@router.get("/{deck_id}", response_model=schemas.DeckDetail, operation_id="get_deck_by_id")
def read_deck(
    deck_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Gets the detailed information for a single deck, including its words and stats.
    """
    db_deck = crud.get_deck(db, deck_id=deck_id)
    if db_deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    if db_deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this deck")

    # --- Calculate Stats at Runtime ---
    words_mastered = crud.count_words_by_status(db, deck_id=deck_id, status=StatusEnum.mastered, user_id=current_user.id)
    total_words = crud.count_total_words_in_deck(db, deck_id=deck_id)
    
    mastery_percentage = (words_mastered / total_words) * 100 if total_words > 0 else 0

    deck_details = schemas.DeckDetail(
        **db_deck.__dict__,
        mastery_percentage=mastery_percentage,
        words_mastered=words_mastered,
        words_learning=total_words - words_mastered,
        easy_count=crud.count_words_by_difficulty(db, deck_id=deck_id, difficulty=DifficultyEnum.easy),
        medium_count=crud.count_words_by_difficulty(db, deck_id=deck_id, difficulty=DifficultyEnum.medium),
        hard_count=crud.count_words_by_difficulty(db, deck_id=deck_id, difficulty=DifficultyEnum.hard),
    )
    return deck_details


@router.put("/{deck_id}", response_model=schemas.Deck, operation_id="update_deck")
def update_deck(
    deck_id: str,
    deck_update: schemas.DeckUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Updates a deck's information.
    """
    db_deck = crud.get_deck(db, deck_id=deck_id)
    if db_deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    if db_deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this deck")
    
    return crud.update_deck(db, deck_id=deck_id, deck_update=deck_update)


@router.delete("/{deck_id}", response_model=schemas.Deck, operation_id="delete_deck")
def delete_deck(
    deck_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Deletes a deck and all the words within it.
    """
    db_deck = crud.get_deck(db, deck_id=deck_id)
    if db_deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    if db_deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this deck")
        
    return crud.delete_deck(db, deck_id=deck_id)