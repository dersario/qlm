#!/usr/bin/env python3
"""
Скрипт для запуска QuickLead Manager
"""

import os
import sys
import logging

logger = logging.Logger("main")

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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


def start_server():
    """Запуск сервера"""
    try:
        import uvicorn

        print("🚀 Запуск сервера...")
        print("📚 Документация API: http://localhost:8000/docs")
        print("🌐 Главная страница: http://localhost:8000")
        print("⏹️  Для остановки нажмите Ctrl+C")
        print("-" * 50)

        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n👋 Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")


if __name__ == "__main__":
    print("🚀 QuickLead Manager - Запуск...")
    print("=" * 50)

    if init_database():
        start_server()
    else:
        print("❌ Не удалось инициализировать базу данных")
        sys.exit(1)
