# app/schemas.py
import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from .models import DifficultyEnum, SessionTypeEnum, StatusEnum


# --- Base Schemas ---
class WordBase(BaseModel):
    word: str
    definition: str
    example: Optional[str] = None
    difficulty: DifficultyEnum

class WordCreate(WordBase):
    pass

class WordUpdate(BaseModel):
    word: Optional[str] = None
    definition: Optional[str] = None
    example: Optional[str] = None
    difficulty: Optional[DifficultyEnum] = None

class DeckBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: str

class DeckCreate(DeckBase):
    pass

class DeckUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserSettingsUpdate(BaseModel):
    daily_goal: Optional[int] = None
    notifications_enabled: Optional[bool] = None
    sound_effects_enabled: Optional[bool] = None
    dark_mode_enabled: Optional[bool] = None

# --- Schemas for Stats and Achievements Responses ---
class WeeklyActivity(BaseModel):
    day: str  # e.g., "Mon", "Tue"
    words_studied: int

class MonthlyProgress(BaseModel):
    month: str  # e.g., "Jan", "Feb"
    words_studied: int

class DifficultyBreakdown(BaseModel):
    easy: int
    medium: int
    hard: int

class UserDashboardStats(BaseModel):
    study_time_seconds: int
    accuracy_rate: float
    total_words_mastered: int
    days_active: int
    weekly_words_goal: int
    weekly_words_progress: int
    monthly_progress: List[MonthlyProgress]
    difficulty_breakdown: DifficultyBreakdown
    weekly_activity: List[WeeklyActivity]

class AchievementDetail(BaseModel):
    id: str
    title: str
    description: str
    icon_name: str
    is_unlocked: bool
    earned_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Schemas for Authentication ---
class Token(BaseModel):
    access_token: str
    token_type: str
    user: "User"

class TokenData(BaseModel):
    email: Optional[str] = None

class GoogleToken(BaseModel):
    google_token: str


# --- Full Schemas (for reading data from the API) ---

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

class DeckDetail(Deck):
    mastery_percentage: float
    words_mastered: int
    words_learning: int
    easy_count: int
    medium_count: int
    hard_count: int

class User(UserBase):
    id: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    streak: int
    best_streak: int
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

# --- Schemas for Study Endpoints ---
class StudySessionCreate(BaseModel):
    deck_id: str
    session_type: SessionTypeEnum
    score_percentage: Optional[int] = None
    words_reviewed: int
    duration_seconds: int

class UserWordProgressUpdate(BaseModel):
    status: StatusEnum

Token.model_rebuild()