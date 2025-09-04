# schemas.py
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from app.models import DifficultyEnum, SessionTypeEnum, StatusEnum

# --- Base Schemas (for shared attributes) ---

class WordBase(BaseModel):
    word: str
    definition: str
    example: Optional[str] = None
    difficulty: DifficultyEnum

class WordCreate(WordBase):
    pass

class DeckBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str

class DeckCreate(DeckBase):
    pass

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

# --- Full Schemas (for reading data from the API) ---
# These include all fields and have from_attributes = True to work with SQLAlchemy models.

class Word(WordBase):
    id: str
    deck_id: str

    class Config:
        from_attributes = True

class Deck(DeckBase):
    id: str
    user_id: str
    words: List[Word] = []

    class Config:
        from_attributes = True

class User(UserBase):
    id: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    streak: int
    level: int
    daily_goal: int
    notifications_enabled: bool
    sound_effects_enabled: bool
    dark_mode_enabled: bool
    created_at: datetime
    decks: List[Deck] = []

    class Config:
        from_attributes = True

# --- Schemas for other models ---

class Achievement(BaseModel):
    id: str
    title: str
    description: str
    icon_name: str

    class Config:
        from_attributes = True

class UserAchievement(BaseModel):
    user_id: str
    achievement_id: str
    earned_at: datetime

    class Config:
        from_attributes = True

class StudySession(BaseModel):
    id: str
    user_id: str
    deck_id: str
    session_type: SessionTypeEnum
    score_percentage: Optional[int] = None
    words_reviewed: int
    completed_at: datetime
    duration_seconds: int

    class Config:
        from_attributes = True

class UserWordProgress(BaseModel):
    user_id: str
    word_id: str
    status: StatusEnum
    last_reviewed_at: datetime
    correct_streak: int

    class Config:
        from_attributes = True