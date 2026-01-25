from fastapi import APIRouter
from app.api.v1 import auth, journals, goals, voice, scores, trends, verdicts, users, notifications

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(journals.router)
api_router.include_router(goals.router)
api_router.include_router(voice.router)
api_router.include_router(scores.router)
api_router.include_router(trends.router)
api_router.include_router(verdicts.router)
api_router.include_router(users.router)
api_router.include_router(notifications.router)
