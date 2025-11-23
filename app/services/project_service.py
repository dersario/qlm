"""Сервис для работы с проектами"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Project, User
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.schemas import ProjectCreate, ProjectUpdate


class ProjectService:
    """Сервис для бизнес-логики проектов"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = ProjectRepository()
        self.user_repository = UserRepository()

    def get_project(self, project_id: int) -> Optional[Project]:
        """Получить проект по ID"""
        return self.repository.get_project(self.db, project_id)

    def get_project_by_api_key(self, api_key: str) -> Optional[Project]:
        """Получить проект по API ключу"""
        return self.repository.get_project_by_api_key(self.db, api_key)

    def get_projects(self, skip: int = 0, limit: int = 100) -> List[Project]:
        """Получить список проектов"""
        return self.repository.get_projects(self.db, skip=skip, limit=limit)

    def get_user_projects(self, user: User) -> List[Project]:
        """Получить проекты пользователя"""
        if user.role.value == "admin":
            return self.get_projects()
        return [assignment.project for assignment in user.project_assignments]

    def create_project(self, project: ProjectCreate) -> Project:
        """Создать новый проект"""
        return self.repository.create_project(self.db, project)

    def update_project(
        self, project_id: int, project_update: ProjectUpdate
    ) -> Optional[Project]:
        """Обновить проект"""
        return self.repository.update_project(self.db, project_id, project_update)

    def delete_project(self, project_id: int) -> bool:
        """Удалить проект"""
        return self.repository.delete_project(self.db, project_id)

    def assign_user_to_project(self, project_id: int, user_id: int) -> bool:
        """Назначить пользователя на проект"""
        # Проверяем, что проект существует
        project = self.repository.get_project(self.db, project_id)
        if not project:
            raise ValueError("Проект не найден")

        # Проверяем, что пользователь существует
        user = self.user_repository.get_user(self.db, user_id)
        if not user:
            raise ValueError("Пользователь не найден")

        return self.repository.assign_user_to_project(self.db, project_id, user_id)

    def remove_user_from_project(self, project_id: int, user_id: int) -> bool:
        """Удалить пользователя из проекта"""
        return self.repository.remove_user_from_project(self.db, project_id, user_id)

    def check_user_access(self, user: User, project_id: int) -> bool:
        """Проверить доступ пользователя к проекту"""
        if user.role.value == "admin":
            return True
        user_projects = [assignment.project.id for assignment in user.project_assignments]
        return project_id in user_projects

