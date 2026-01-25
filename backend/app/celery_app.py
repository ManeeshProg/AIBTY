"""Celery application configuration."""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "amibetter",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend_url,
)

# Load config from celeryconfig.py
celery_app.config_from_object("celeryconfig")

# Auto-discover tasks in app.tasks module
celery_app.autodiscover_tasks(["app.tasks"])
