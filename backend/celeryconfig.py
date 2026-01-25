"""Celery configuration."""
from celery.schedules import crontab

# Task serialization
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "UTC"
enable_utc = True

# Task execution settings
task_acks_late = True  # Acknowledge after task completes (reliability)
task_reject_on_worker_lost = True  # Requeue if worker dies
task_time_limit = 300  # 5 minute hard limit per task
task_soft_time_limit = 240  # 4 minute soft limit (raises exception)

# Retry settings for failed tasks
task_default_retry_delay = 60  # 1 minute initial retry
task_max_retries = 3

# Beat schedule - periodic tasks
beat_schedule = {
    "check-due-analyses": {
        "task": "app.tasks.orchestrator.check_due_analyses",
        "schedule": crontab(minute="*"),  # Every minute
        "options": {"queue": "default"},
    },
    "check-non-loggers-hourly": {
        "task": "app.tasks.notification_tasks.check_and_notify_non_loggers",
        "schedule": crontab(minute=0),  # Run at the top of every hour
        "options": {"queue": "notifications"},
    },
}

# Queue configuration
task_routes = {
    "app.tasks.orchestrator.*": {"queue": "default"},
    "app.tasks.analysis.*": {"queue": "analysis"},
    "app.tasks.notification_tasks.*": {"queue": "notifications"},
}

# Result backend settings
result_expires = 3600  # Results expire after 1 hour
