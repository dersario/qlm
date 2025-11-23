"""Сервис для работы с пользователями"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserUpdate


class UserService:
    """Сервис для бизнес-логики пользователей"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository()

    def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return self.repository.get_user(self.db, user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        return self.repository.get_user_by_email(self.db, email)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получить пользователя по username"""
        return self.repository.get_user_by_username(self.db, username)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить список пользователей"""
        return self.repository.get_users(self.db, skip=skip, limit=limit)

    def create_user(self, user: UserCreate) -> User:
        """Создать нового пользователя"""
        # Проверяем, что пользователь не существует
        if self.repository.get_user_by_email(self.db, user.email):
            raise ValueError("Пользователь с таким email уже существует")
        if self.repository.get_user_by_username(self.db, user.username):
            raise ValueError("Пользователь с таким именем уже существует")

        return self.repository.create_user(self.db, user)

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Обновить пользователя"""
        return self.repository.update_user(self.db, user_id, user_update)

    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        return self.repository.delete_user(self.db, user_id)
