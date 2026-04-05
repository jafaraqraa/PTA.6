from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import (
    session_controller,
    auth_controller,
    user_controller,
    university_controller,
    subscription_controller,
    analytics_controller
)

app = FastAPI(title="PTA Simulator Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
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

@app.get("/")
def start():
    return {"id": "112"}
