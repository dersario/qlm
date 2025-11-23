"""Репозиторий для работы с пользователями"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_password_hash
from app.models import User
from app.schemas import UserCreate, UserUpdate


class UserRepository:
    """Репозиторий для доступа к данным пользователей"""

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        stmt = select(User).where(User.id == user_id)
        return db.scalar(stmt)

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        stmt = select(User).where(User.email == email)
        return db.scalar(stmt)

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Получить пользователя по username"""
        stmt = select(User).where(User.username == username)
        return db.scalar(stmt)

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить список пользователей"""
        stmt = select(User).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """Создать нового пользователя"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            role=user.role,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update_user(
        db: Session, user_id: int, user_update: UserUpdate
    ) -> Optional[User]:
        """Обновить пользователя"""
        stmt = select(User).where(User.id == user_id)
        db_user = db.scalar(stmt)
        if db_user:
            update_data = user_update.model_dump(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(
                    update_data.pop("password")
                )

            for field, value in update_data.items():
                setattr(db_user, field, value)

            db.commit()
            db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Удалить пользователя"""
        stmt = select(User).where(User.id == user_id)
        db_user = db.scalar(stmt)
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False
