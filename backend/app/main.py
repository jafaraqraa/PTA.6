from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.controllers import session_controller, auth_controller

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

@app.get("/")
def start():
    return {"id": "112"}
