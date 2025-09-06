# app/routers/users.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import SessionLocal
from app.routers.auth import get_current_active_user  # Import the dependency

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """
    Fetches the profile data for the currently authenticated user.
    """
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user_me(
    profile_update: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Updates the profile of the currently authenticated user.
    """
    return crud.update_user_profile(db=db, user=current_user, profile_update=profile_update)


@router.put("/me/settings", response_model=schemas.User)
def update_user_me_settings(
    settings_update: schemas.UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Updates user-specific settings for the currently authenticated user.
    """
    return crud.update_user_settings(db=db, user=current_user, settings_update=settings_update)


@router.get("/me/achievements", response_model=List[schemas.AchievementDetail])
def read_user_me_achievements(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Gets the list of all achievements for the currently authenticated user.
    """
    return crud.get_achievements_for_user(db=db, user_id=current_user.id)


@router.get("/me/stats", response_model=schemas.UserStats)
def read_user_me_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Fetches aggregated statistics for the user's profile dashboards.
    """
    return crud.get_user_stats(db=db, user_id=current_user)