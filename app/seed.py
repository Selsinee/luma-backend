# app/seed.py
from sqlalchemy.orm import Session

from app import models
from app.database import SessionLocal, engine

ACHIEVEMENTS_TO_CREATE = [
    {
        "title": "First Steps",
        "description": "Learn your first 10 words",
        "icon_name": "star",
    },
    {
        "title": "Word Master",
        "description": "Learn 100 words",
        "icon_name": "award",
    },
    {
        "title": "Streak Warrior",
        "description": "Maintain a 7-day streak",
        "icon_name": "zap",
    },
    {
        "title": "Polyglot",
        "description": "Study 3 different languages",
        "icon_name": "globe",
    },
    {
        "title": "Dedicated Learner",
        "description": "Study for 30 consecutive days",
        "icon_name": "calendar",
    },
]

def seed_achievements(db: Session):
    print("Seeding achievements...")
    for ach_data in ACHIEVEMENTS_TO_CREATE:
        # Check if achievement with this title already exists
        db_achievement = db.query(models.Achievement).filter(models.Achievement.title == ach_data["title"]).first()
        if not db_achievement:
            # If it doesn't exist, create it without specifying the ID
            new_achievement = models.Achievement(
                title=ach_data["title"],
                description=ach_data["description"],
                icon_name=ach_data["icon_name"],
            )
            db.add(new_achievement)
            print(f"  - Created achievement: {ach_data['title']}")
    db.commit()
    print("Seeding complete.")


if __name__ == "__main__":
    # Ensure tables are created before seeding
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_achievements(db)
    finally:
        db.close()