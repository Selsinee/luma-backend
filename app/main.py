# app/main.py
from fastapi import FastAPI

from . import models
from .database import engine
from .routers import auth, decks, study, users, words

# Create all database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Luma API",
    description="API for the Luma flashcard application.",
    version="0.1.0",
)

# --- Include Routers ---
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(decks.router)
app.include_router(words.router)
app.include_router(study.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Luma API!"}