"""Репозиторий для работы с проектами"""

from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.auth import generate_api_key
from app.models.project import Project, ProjectUser
from app.schemas import ProjectCreate, ProjectUpdate


class ProjectRepository:
    """Репозиторий для доступа к данным проектов"""

    @staticmethod
    def get_project(db: Session, project_id: int) -> Optional[Project]:
        """Получить проект по ID"""
        stmt = select(Project).where(Project.id == project_id)
        return db.scalar(stmt)

    @staticmethod
    def get_project_by_api_key(db: Session, api_key: str) -> Optional[Project]:
        """Получить проект по API ключу"""
        stmt = select(Project).where(Project.api_key == api_key)
        return db.scalar(stmt)

    @staticmethod
    def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
        """Получить список проектов"""
        stmt = select(Project).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    @staticmethod
    def create_project(db: Session, project: ProjectCreate) -> Project:
        """Создать новый проект"""
        api_key = generate_api_key()
        db_project = Project(
            name=project.name,
            description=project.description,
            api_key=api_key,
            webhook_url=project.webhook_url,
            webhook_headers=project.webhook_headers,
            custom_fields_schema=project.custom_fields_schema,
            status_config=project.status_config,
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

    @staticmethod
    def update_project(
        db: Session, project_id: int, project_update: ProjectUpdate
    ) -> Optional[Project]:
        """Обновить проект"""
        stmt = select(Project).where(Project.id == project_id)
        db_project = db.scalar(stmt)
        if db_project:
            update_data = project_update.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_project, field, value)

            db.commit()
            db.refresh(db_project)
        return db_project

    @staticmethod
    def delete_project(db: Session, project_id: int) -> bool:
        """Удалить проект"""
        stmt = select(Project).where(Project.id == project_id)
        db_project = db.scalar(stmt)
        if db_project:
            db.delete(db_project)
            db.commit()
            return True
        return False

    @staticmethod
    def assign_user_to_project(db: Session, project_id: int, user_id: int) -> bool:
        """Назначить пользователя на проект"""
        stmt = select(ProjectUser).where(
            and_(ProjectUser.project_id == project_id, ProjectUser.user_id == user_id)
        )
        existing = db.scalar(stmt)

        if existing:
            return False

        assignment = ProjectUser(project_id=project_id, user_id=user_id)
        db.add(assignment)
        db.commit()
        return True

    @staticmethod
    def remove_user_from_project(db: Session, project_id: int, user_id: int) -> bool:
        """Удалить пользователя из проекта"""
        stmt = select(ProjectUser).where(
            and_(ProjectUser.project_id == project_id, ProjectUser.user_id == user_id)
        )
        assignment = db.scalar(stmt)

        if assignment:
            db.delete(assignment)
            db.commit()
            return True
        return False
