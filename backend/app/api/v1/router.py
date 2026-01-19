from fastapi import APIRouter
from app.api.v1 import auth, journals, goals, voice

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(journals.router)
api_router.include_router(goals.router)
api_router.include_router(voice.router)
