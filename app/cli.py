"""CLI команды для запуска приложения"""

import uvicorn
from app.config import settings


def start_server():
    """Запуск сервера через uvicorn"""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )


if __name__ == "__main__":
    start_server()

