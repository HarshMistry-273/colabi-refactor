from celery import Celery
from src.config import Config


celery_app = Celery(
    "colabi",
    broker=Config.REDIS_URL,
    backend=Config.REDIS_URL,
    include=["src.tasks.task"],
)

# Configure Celery to not ignore results
celery_app.conf.update(
    task_track_started=True,
    result_expires=None,  # Results won't expire
    task_ignore_result=False,  # Don't ignore results
)
