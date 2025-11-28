import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api import auth, external, leads, projects, users
from app.config import settings
from app.database import Base, engine


# Создаем таблицы при запуске
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass


# Создание приложения FastAPI
app = FastAPI(
    title=settings.app_name,
    description="Централизованная система для работы с лидами (заявками)",
    version="1.0.0",
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутеров
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(leads.router, prefix="/api")
app.include_router(external.router)  # Без префикса /api

# Статические файлы для админ-панели
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница с информацией об API"""
    return """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QuickLead Manager</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2563eb;
                text-align: center;
                margin-bottom: 30px;
            }
            .api-info {
                background: #f8fafc;
                padding: 20px;
                border-radius: 6px;
                margin: 20px 0;
            }
            .endpoint {
                background: #e0f2fe;
                padding: 10px;
                margin: 10px 0;
                border-radius: 4px;
                font-family: monospace;
            }
            .docs-link {
                text-align: center;
                margin-top: 30px;
            }
            .docs-link a {
                background: #2563eb;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                display: inline-block;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 QuickLead Manager</h1>
            <p>Централизованная система для приема, обработки и распределения заявок с сайтов и лендингов.</p>
            
            <div class="api-info">
                <h3>📡 Основные API эндпоинты:</h3>
                <div class="endpoint">POST /api/v1/lead - Прием заявок (внешний API)</div>
                <div class="endpoint">GET /api/leads - Просмотр заявок</div>
                <div class="endpoint">GET /api/projects - Управление проектами</div>
                <div class="endpoint">GET /api/users - Управление пользователями</div>
                <div class="endpoint">POST /api/auth/login - Аутентификация</div>
            </div>
            
            <div class="api-info">
                <h3>🔑 Аутентификация:</h3>
                <p>Для внешнего API используйте заголовок <code>X-API-Key</code> с ключом проекта.</p>
                <p>Для внутреннего API используйте JWT токен в заголовке <code>Authorization: Bearer &lt;token&gt;</code></p>
            </div>
            
            <div class="docs-link">
                <a href="/docs" target="_blank">📚 Открыть документацию API</a>
            </div>
        </div>
    </body>
    </html>
    """


logger = logging.Logger("main")

# Добавляем текущую директорию в путь


def init_database():
    """Инициализация базы данных"""
    try:
        from app.auth import get_password_hash
        from app.database import Base, SessionLocal, engine
        from app.models import User, UserRole

        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Таблицы базы данных созданы")

        # Создаем администратора
        db = SessionLocal()
        try:
            # Проверяем, есть ли уже администраторы
            admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
            if admin_exists:
                logger.info("ℹ️  Администратор уже существует")
            else:
                # Создаем администратора
                admin_user = User(
                    email="admin@gmail.com",
                    username="admin",
                    hashed_password=get_password_hash("admin123"),
                    full_name="Admin",
                    role=UserRole.ADMIN,
                    is_active=True,
                )

                db.add(admin_user)
                db.commit()
                db.refresh(admin_user)

                logger.info("✅ Администратор создан:")
                print("   Email: admin@quicklead.local")
                print("   Username: admin")
                print("   Password: admin123")
                print("⚠️  Обязательно смените пароль после первого входа!")
        finally:
            db.close()

    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False

    return True

init_database()
@app.get("/health")
async def health_check():
    """Проверка работоспособности приложения"""
    return {"status": "ok", "message": "QuickLead Manager работает", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
