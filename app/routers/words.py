# app/routers/words.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal
from app.routers.auth import get_current_active_user

router = APIRouter(
    # The prefix is nested under decks because words always belong to a deck
    prefix="/decks/{deck_id}/words",
    tags=["Words"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.Word)
def create_word_for_deck_endpoint(
    deck_id: str,
    word: schemas.WordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Adds a new word to a specific deck.
    Ensures the current user owns the deck.
    """
    db_deck = crud.get_deck(db, deck_id=deck_id)
    if not db_deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if db_deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add words to this deck")
    
    return crud.create_word(db=db, word=word, deck_id=deck_id)


@router.put("/{word_id}", response_model=schemas.Word)
def update_word_endpoint(
    deck_id: str,
    word_id: str,
    word: schemas.WordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Updates a word's information.
    Ensures the current user owns the deck containing the word.
    """
    db_deck = crud.get_deck(db, deck_id=deck_id)
    if not db_deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if db_deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this deck's words")

    db_word = crud.update_word(db, word_id=word_id, word_update=word)
    if db_word is None:
        raise HTTPException(status_code=404, detail="Word not found")
        
    return db_word


@router.delete("/{word_id}", response_model=schemas.Word)
def delete_word_endpoint(
    deck_id: str,
    word_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user),
):
    """
    Deletes a word from a deck.
    Ensures the current user owns the deck containing the word.
    """
    db_deck = crud.get_deck(db, deck_id=deck_id)
    if not db_deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    if db_deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this deck's words")

    db_word = crud.delete_word(db, word_id=word_id)
    if db_word is None:
        raise HTTPException(status_code=404, detail="Word not found")
        
    return db_word