import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.controllers import (
    session_controller,
    auth_controller,
    user_controller,
    university_controller,
    subscription_controller,
    analytics_controller,
    quiz_controller
)

app = FastAPI(title="PTA Simulator Backend")

@app.on_event("startup")
async def verify_schema():
    """Safety layer: Verify DB schema matches expected ORM models on startup."""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(text("PRAGMA table_info(universities)"))
            columns = [row[1] for row in result.fetchall()]
            if 'domain' in columns:
                logging.error("DATABASE SCHEMA MISMATCH: 'domain' column still exists in 'universities' table. Please run migrations.")
        except Exception as e:
            logging.error(f"Failed to verify database schema: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_controller.router, prefix="/auth", tags=["Authentication"])
app.include_router(session_controller.router, prefix="/sessions")
app.include_router(user_controller.router, prefix="/users", tags=["Users"])
app.include_router(university_controller.router, prefix="/universities", tags=["Universities"])
app.include_router(subscription_controller.router, prefix="/subscriptions", tags=["Subscriptions"])
app.include_router(analytics_controller.router, prefix="/analytics", tags=["Analytics"])
app.include_router(quiz_controller.router, prefix="/quizzes", tags=["Quizzes"])

@app.get("/")
def start():
    return {"id": "112"}
