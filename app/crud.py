# app/crud.py
from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from . import models, schemas

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# --- User CRUD ---

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email, full_name=user.full_name, password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_profile(db: Session, user: models.User, profile_update: schemas.UserProfileUpdate):
    """
    Update a user's profile information.
    """
    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_settings(db: Session, user: models.User, settings_update: schemas.UserSettingsUpdate):
    """
    Update a user's settings.
    """
    update_data = settings_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_achievements_for_user(db: Session, user_id: str):
    """
    Get all achievements, marking which ones the user has unlocked using a single, efficient query.
    """
    # Subquery to find achievements unlocked by the specific user
    user_achievements_subquery = db.query(
        models.UserAchievement.achievement_id,
        models.UserAchievement.earned_at
    ).filter(models.UserAchievement.user_id == user_id).subquery()

    # Main query with a LEFT JOIN to get all achievements
    # and mark the ones that the user has unlocked.
    results = db.query(
        models.Achievement,
        (user_achievements_subquery.c.achievement_id != None).label("is_unlocked"),
        user_achievements_subquery.c.earned_at
    ).outerjoin(
        user_achievements_subquery, models.Achievement.id == user_achievements_subquery.c.achievement_id
    ).all()

    return [
        schemas.AchievementDetail(
            id=achievement.id,
            title=achievement.title,
            description=achievement.description,
            icon_name=achievement.icon_name,
            is_unlocked=is_unlocked,
            earned_at=earned_at
        )
        for achievement, is_unlocked, earned_at in results
    ]

def get_user_stats(db: Session, user_id: str) -> schemas.UserStats:
    """
    Calculates aggregated stats for a user at runtime.
    """
    # Calculate total study time in seconds
    total_duration_result = db.query(func.sum(models.StudySession.duration_seconds)).filter(models.StudySession.user_id == user_id).scalar()
    total_duration = total_duration_result or 0

    # Calculate accuracy rate from quiz sessions
    accuracy_result = db.query(func.avg(models.StudySession.score_percentage)).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.session_type == 'quiz'
    ).scalar()
    accuracy = accuracy_result or 0.0

    # Count total words mastered
    total_mastered = db.query(func.count(models.UserWordProgress.word_id)).filter(
        models.UserWordProgress.user_id == user_id,
        models.UserWordProgress.status == 'mastered'
    ).scalar()

    # Count distinct days active from study sessions
    days_active = db.query(func.count(distinct(func.date(models.StudySession.completed_at)))).filter(
        models.StudySession.user_id == user_id
    ).scalar()

    return schemas.UserStats(
        study_time_seconds=total_duration,
        accuracy_rate=accuracy,
        total_words_mastered=total_mastered,
        days_active=days_active
    )

def delete_user(db: Session, user_id: str):
    """
    Delete a user.
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    db.delete(db_user)
    db.commit()
    return db_user

# --- Deck CRUD ---

def get_deck(db: Session, deck_id: str):
    return db.query(models.Deck).filter(models.Deck.id == deck_id).first()

def get_decks_by_user(db: Session, user_id: str, category: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Deck).filter(models.Deck.user_id == user_id)
    if category:
        query = query.filter(models.Deck.category == category)
    return query.offset(skip).limit(limit).all()

def count_total_words_in_deck(db: Session, deck_id: str) -> int:
    return db.query(models.Word).filter(models.Word.deck_id == deck_id).count()

def count_words_by_status(db: Session, deck_id: str, status: models.StatusEnum, user_id: str) -> int:
    return db.query(models.UserWordProgress).join(models.Word).filter(
        models.Word.deck_id == deck_id,
        models.UserWordProgress.user_id == user_id,
        models.UserWordProgress.status == status
    ).count()

def count_words_by_difficulty(db: Session, deck_id: str, difficulty: models.DifficultyEnum) -> int:
    return db.query(models.Word).filter(
        models.Word.deck_id == deck_id,
        models.Word.difficulty == difficulty
    ).count()

def create_deck(db: Session, deck: schemas.DeckCreate, user_id: str):
    db_deck = models.Deck(**deck.model_dump(), user_id=user_id)
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    return db_deck

def update_deck(db: Session, deck_id: str, deck_update: schemas.DeckUpdate):
    """
    Update a deck's information.
    """
    db_deck = get_deck(db, deck_id)
    if not db_deck:
        return None

    update_data = deck_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_deck, key, value)

    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    return db_deck

def delete_deck(db: Session, deck_id: str):
    """
    Delete a deck.
    """
    db_deck = get_deck(db, deck_id)
    if not db_deck:
        return None
    db.delete(db_deck)
    db.commit()
    return db_deck

# --- Word CRUD ---

def get_word(db: Session, word_id: str):
    return db.query(models.Word).filter(models.Word.id == word_id).first()

def get_words_by_deck(db: Session, deck_id: str, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Word)
        .filter(models.Word.deck_id == deck_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_word(db: Session, word: schemas.WordCreate, deck_id: str):
    db_word = models.Word(**word.model_dump(), deck_id=deck_id)
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word

def update_word(db: Session, word_id: str, word_update: schemas.WordUpdate):
    """
    Update a word's information.
    """
    db_word = get_word(db, word_id)
    if not db_word:
        return None
        
    update_data = word_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_word, key, value)
        
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word

def delete_word(db: Session, word_id: str):
    """
    Delete a word.
    """
    db_word = get_word(db, word_id)
    if not db_word:
        return None
    db.delete(db_word)
    db.commit()
    return db_word

def create_study_session(db: Session, session: schemas.StudySessionCreate, user_id: str):
    """
    Create a new study session record for a user.
    """
    db_session = models.StudySession(**session.model_dump(), user_id=user_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def update_word_progress(db: Session, word_id: str, user_id: str, progress_update: schemas.UserWordProgressUpdate):
    """
    Updates a user's progress for a single word. Creates the record if it doesn't exist.
    """
    db_progress = db.query(models.UserWordProgress).filter(
        models.UserWordProgress.word_id == word_id,
        models.UserWordProgress.user_id == user_id
    ).first()

    if db_progress:
        # Update existing progress record
        db_progress.status = progress_update.status
        if progress_update.status == models.StatusEnum.mastered:
             db_progress.correct_streak += 1
        else:
             db_progress.correct_streak = 0
    else:
        # Create new progress record if one doesn't exist
        db_progress = models.UserWordProgress(
            user_id=user_id,
            word_id=word_id,
            status=progress_update.status,
            correct_streak=1 if progress_update.status == models.StatusEnum.mastered else 0
        )
    
    db.add(db_progress)
    db.commit()
    db.refresh(db_progress)
    return db_progress