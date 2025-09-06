# app/models.py
import enum
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (Boolean, DateTime, Enum, ForeignKey, Integer, String,
                        Text, func)
from sqlalchemy.orm import (Mapped, declarative_base, mapped_column,
                            relationship)

# --- Base Class for Declarative Models ---
Base = declarative_base()

# --- Python Enums for Database ENUM Types ---
class DifficultyEnum(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

class StatusEnum(str, enum.Enum):
    learning = "learning"
    mastered = "mastered"

class SessionTypeEnum(str, enum.Enum):
    flashcard = "flashcard"
    quiz = "quiz"

# --- Main Tables ---

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    google_id: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    best_streak: Mapped[int] = mapped_column(Integer, default=0)
    level: Mapped[int] = mapped_column(Integer, default=1)
    daily_goal: Mapped[int] = mapped_column(Integer, default=10)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    sound_effects_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    dark_mode_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    decks: Mapped[List["Deck"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    study_sessions: Mapped[List["StudySession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    achievements: Mapped[List["UserAchievement"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    word_progress: Mapped[List["UserWordProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Deck(Base):
    __tablename__ = "decks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="decks")
    words: Mapped[List["Word"]] = relationship(back_populates="deck", cascade="all, delete-orphan")
    study_sessions: Mapped[List["StudySession"]] = relationship(back_populates="deck", cascade="all, delete-orphan")

class Word(Base):
    __tablename__ = "words"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    deck_id: Mapped[str] = mapped_column(ForeignKey("decks.id"), nullable=False)
    word: Mapped[str] = mapped_column(String(255))
    definition: Mapped[str] = mapped_column(Text)
    example: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty: Mapped[DifficultyEnum] = mapped_column(Enum(DifficultyEnum), nullable=False)

    # Relationships
    deck: Mapped["Deck"] = relationship(back_populates="words")
    user_progress: Mapped[List["UserWordProgress"]] = relationship(back_populates="word", cascade="all, delete-orphan")

class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str] = mapped_column(Text)
    icon_name: Mapped[str] = mapped_column(String(100))

    # Relationships
    users: Mapped[List["UserAchievement"]] = relationship(back_populates="achievement")

# --- Join Tables (for Many-to-Many relationships and tracking) ---

class UserWordProgress(Base):
    __tablename__ = "user_word_progress"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    word_id: Mapped[str] = mapped_column(ForeignKey("words.id"), primary_key=True)
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum), default=StatusEnum.learning)
    last_reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    correct_streak: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="word_progress")
    word: Mapped["Word"] = relationship(back_populates="user_progress")

class StudySession(Base):
    __tablename__ = "study_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    deck_id: Mapped[str] = mapped_column(ForeignKey("decks.id"), nullable=False)
    session_type: Mapped[SessionTypeEnum] = mapped_column(Enum(SessionTypeEnum), nullable=False)
    score_percentage: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    words_reviewed: Mapped[int] = mapped_column(Integer)
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    duration_seconds: Mapped[int] = mapped_column(Integer)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="study_sessions")
    deck: Mapped["Deck"] = relationship(back_populates="study_sessions")

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    achievement_id: Mapped[str] = mapped_column(ForeignKey("achievements.id"), primary_key=True)
    earned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user: Mapped["User"] = relationship(back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship(back_populates="users")