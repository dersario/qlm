from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    app_name: str = "QuickLead Manager"
    debug: bool = False
    secret_key: str = "your-secret-key-change-in-production"
    
    # База данных
    database_url: str = "sqlite:///./quicklead.db"
    
    # JWT настройки
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # Redis для Celery
    redis_url: str = "redis://localhost:6379"
    
    # Настройки вебхуков
    webhook_timeout: int = 30
    webhook_retry_attempts: int = 3
    
    # Telegram Bot (опционально)
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Slack (опционально)
    slack_bot_token: Optional[str] = None
    slack_channel: Optional[str] = None
    
    class Config:
        env_file = ".env"


settings = Settings()
