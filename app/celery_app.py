from celery import Celery
from app.config import settings

# Создание экземпляра Celery
celery_app = Celery(
    "quicklead_manager",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"]
)

# Настройки Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)
