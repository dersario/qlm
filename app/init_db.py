#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных и создания первого администратора
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import User, UserRole
from app.auth import get_password_hash
from app.config import settings

def init_db():
    """Инициализация базы данных"""
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы базы данных созданы")

def create_admin_user():
    """Создание первого администратора"""
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже администраторы
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if admin_exists:
            print("ℹ️  Администратор уже существует")
            return
        
        # Создаем администратора
        admin_user = User(
            email="admin@quicklead.local",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            full_name="Системный администратор",
            role=UserRole.ADMIN,
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Администратор создан:")
        print(f"   Email: admin@quicklead.local")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print("⚠️  Обязательно смените пароль после первого входа!")
        
    except Exception as e:
        print(f"❌ Ошибка при создании администратора: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Основная функция"""
    print("🚀 Инициализация QuickLead Manager...")
    
    init_db()
    create_admin_user()
    
    print("\n✅ Инициализация завершена!")
    print("🌐 Запустите приложение командой: uvicorn app.main:app --reload")
    print("📚 Документация API будет доступна по адресу: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
