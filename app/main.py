# main.py
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas
from app.database import SessionLocal, engine
from .routers import users, decks # Import your new routers

# This command creates all the database tables based on your models.py
# It's safe to run this every time; it will only create tables that don't exist.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Luma API",
    description="API for the Luma flashcard application.",
    version="0.1.0",
)

app.include_router(users.router)

# --- Dependency ---
# This function gets a database session for each request and ensures it's closed afterward.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Welcome to the Luma API!"}

# --- Users ---

@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user.
    """
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # TODO: Implement proper password hashing (e.g., using passlib)
    # NEVER store plain text passwords. This is a placeholder.
    hashed_password = user.password + "_hashed" # Replace this with a hashing library

    new_user = models.User(
        email=user.email,
        full_name=user.full_name,
        password_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(user_id: str, db: Session = Depends(get_db)):
    """
    Get a specific user by their ID.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# --- Decks ---

@app.post("/users/{user_id}/decks/", response_model=schemas.Deck, tags=["Decks"])
def create_deck_for_user(user_id: str, deck: schemas.DeckCreate, db: Session = Depends(get_db)):
    """
    Create a new deck for a specific user.
    """
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    new_deck = models.Deck(**deck.dict(), user_id=user_id)
    db.add(new_deck)
    db.commit()
    db.refresh(new_deck)
    return new_deck

@app.get("/decks/", response_model=List[schemas.Deck], tags=["Decks"])
def read_decks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of all decks.
    """
    decks = db.query(models.Deck).offset(skip).limit(limit).all()
    return decks

# --- Words ---

@app.post("/decks/{deck_id}/words/", response_model=schemas.Word, tags=["Words"])
def create_word_for_deck(deck_id: str, word: schemas.WordCreate, db: Session = Depends(get_db)):
    """
    Add a new word to a specific deck.
    """
    db_deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not db_deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    new_word = models.Word(**word.dict(), deck_id=deck_id)
    db.add(new_word)
    db.commit()
    db.refresh(new_word)
    return new_word

# TODO: Add more endpoints for getting, updating, and deleting items.
# (e.g., getting a specific deck, getting all words in a deck, etc.)