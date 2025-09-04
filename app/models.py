# models.py
import enum
import uuid
from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

# --- Base Class for Declarative Models ---
Base = declarative_base()

# --- Python Enums for Database ENUM Types ---
# These ensure that the data in your database is one of a few specific values.
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

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(255))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255))
    google_id = Column(String(255), unique=True, nullable=True)
    avatar_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    streak = Column(Integer, default=0)
    level = Column(Integer, default=1)
    daily_goal = Column(Integer, default=10)
    notifications_enabled = Column(Boolean, default=True)
    sound_effects_enabled = Column(Boolean, default=True)
    dark_mode_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    decks = relationship("Deck", back_populates="owner", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    word_progress = relationship("UserWordProgress", back_populates="user", cascade="all, delete-orphan")

class Deck(Base):
    __tablename__ = "decks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String(255))
    description = Column(Text, nullable=True)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner = relationship("User", back_populates="decks")
    words = relationship("Word", back_populates="deck", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="deck", cascade="all, delete-orphan")

class Word(Base):
    __tablename__ = "words"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    deck_id = Column(String, ForeignKey("decks.id"), nullable=False)
    word = Column(String(255))
    definition = Column(Text)
    example = Column(Text, nullable=True)
    difficulty = Column(Enum(DifficultyEnum), nullable=False)

    # Relationships
    deck = relationship("Deck", back_populates="words")
    user_progress = relationship("UserWordProgress", back_populates="word", cascade="all, delete-orphan")

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), unique=True)
    description = Column(Text)
    icon_name = Column(String(100))

    # Relationships
    users = relationship("UserAchievement", back_populates="achievement")

# --- Join Tables (for Many-to-Many relationships and tracking) ---

class UserWordProgress(Base):
    __tablename__ = "user_word_progress"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    word_id = Column(String, ForeignKey("words.id"), primary_key=True)
    status = Column(Enum(StatusEnum), default=StatusEnum.learning)
    last_reviewed_at = Column(DateTime(timezone=True), server_default=func.now())
    correct_streak = Column(Integer, default=0)

    # Relationships
    user = relationship("User", back_populates="word_progress")
    word = relationship("Word", back_populates="user_progress")

class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    deck_id = Column(String, ForeignKey("decks.id"), nullable=False)
    session_type = Column(Enum(SessionTypeEnum), nullable=False)
    score_percentage = Column(Integer, nullable=True) # Nullable for flashcard sessions
    words_reviewed = Column(Integer)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_seconds = Column(Integer)

    # Relationships
    user = relationship("User", back_populates="study_sessions")
    deck = relationship("Deck", back_populates="study_sessions")

class UserAchievement(Base):
    __tablename__ = "user_achievements"

    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    achievement_id = Column(String, ForeignKey("achievements.id"), primary_key=True)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")