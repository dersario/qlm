"""Сервис для работы с заявками"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Lead, User, UserRole
from app.repositories.lead_repository import LeadRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas import (
    DashboardStats,
    LeadCommentCreate,
    LeadCommentResponse,
    LeadCreate,
    LeadFilter,
    LeadUpdate,
)


class LeadService:
    """Сервис для бизнес-логики заявок"""

    def __init__(self, db: Session):
        self.db = db
        self.repository = LeadRepository()
        self.project_repository = ProjectRepository()

    def get_lead(self, lead_id: int) -> Optional[Lead]:
        """Получить заявку по ID"""
        return self.repository.get_lead(self.db, lead_id)

    def get_leads(
        self,
        filters: Optional[LeadFilter] = None,
        skip: int = 0,
        limit: int = 100,
        user: Optional[User] = None,
    ) -> List[Lead]:
        """Получить список заявок с фильтрацией"""
        # Если пользователь не админ, ограничиваем доступ только к его проектам
        if user and user.role != UserRole.ADMIN:
            user_projects = [
                assignment.project.id for assignment in user.project_assignments
            ]
            if filters and filters.project_id:
                if filters.project_id not in user_projects:
                    return []
            elif not filters:
                filters = LeadFilter()
            elif not filters.project_id:
                if not user_projects:
                    return []
                filters.project_id = user_projects[0]

        return self.repository.get_leads(
            self.db, filters=filters, skip=skip, limit=limit
        )

    def create_lead(
        self,
        lead: LeadCreate,
        ip_address: str = None,
        user_agent: str = None,
        referrer: str = None,
        user: Optional[User] = None,
    ) -> Lead:
        """Создать новую заявку"""
        # Проверяем доступ к проекту
        if user and user.role != UserRole.ADMIN:
            user_projects = [
                assignment.project.id for assignment in user.project_assignments
            ]
            if lead.project_id not in user_projects:
                raise ValueError("Недостаточно прав доступа к проекту")

        # Проверяем, что проект существует
        project = self.project_repository.get_project(self.db, lead.project_id)
        if not project:
            raise ValueError("Проект не найден")

        return self.repository.create_lead(
            self.db,
            lead,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
        )

    def update_lead(
        self,
        lead_id: int,
        lead_update: LeadUpdate,
        user: Optional[User] = None,
    ) -> Optional[Lead]:
        """Обновить заявку"""
        lead = self.repository.get_lead(self.db, lead_id)
        if not lead:
            raise ValueError("Заявка не найдена")

        # Проверяем доступ
        if user and user.role != UserRole.ADMIN:
            user_projects = [
                assignment.project.id for assignment in user.project_assignments
            ]
            if lead.project_id not in user_projects:
                raise ValueError("Недостаточно прав доступа к заявке")

        changed_by = user.id if user else None
        return self.repository.update_lead(
            self.db, lead_id, lead_update, changed_by=changed_by
        )

    def delete_lead(self, lead_id: int, user: Optional[User] = None) -> bool:
        """Удалить заявку"""
        lead = self.repository.get_lead(self.db, lead_id)
        if not lead:
            raise ValueError("Заявка не найдена")

        # Проверяем доступ
        if user and user.role != UserRole.ADMIN:
            user_projects = [
                assignment.project.id for assignment in user.project_assignments
            ]
            if lead.project_id not in user_projects:
                raise ValueError("Недостаточно прав доступа к заявке")

        return self.repository.delete_lead(self.db, lead_id)

    def add_comment(
        self, lead_id: int, comment_data: LeadCommentCreate, user: User
    ) -> LeadCommentResponse:
        """Добавить комментарий к заявке"""
        lead = self.repository.get_lead(self.db, lead_id)
        if not lead:
            raise ValueError("Заявка не найдена")

        # Проверяем доступ
        if user.role != UserRole.ADMIN:
            user_projects = [
                assignment.project.id for assignment in user.project_assignments
            ]
            if lead.project_id not in user_projects:
                raise ValueError("Недостаточно прав доступа к заявке")

        comment = self.repository.add_comment(self.db, lead_id, comment_data, user.id)
        if not comment:
            raise ValueError("Не удалось добавить комментарий")

        return comment

    def get_dashboard_stats(
        self, project_id: Optional[int] = None, user: Optional[User] = None
    ) -> DashboardStats:
        """Получить статистику для дашборда"""
        # Если пользователь не админ, ограничиваем доступ только к его проектам
        if user and user.role != UserRole.ADMIN:
            user_projects = [
                assignment.project.id for assignment in user.project_assignments
            ]
            if project_id and project_id not in user_projects:
                raise ValueError("Недостаточно прав доступа к проекту")
            elif not project_id and len(user_projects) == 1:
                project_id = user_projects[0]

        stats = self.repository.get_lead_stats(self.db, project_id=project_id)
        return DashboardStats(**stats)

    def check_user_access(self, user: User, lead: Lead) -> bool:
        """Проверить доступ пользователя к заявке"""
        if user.role == UserRole.ADMIN:
            return True
        user_projects = [
            assignment.project.id for assignment in user.project_assignments
        ]
        return lead.project_id in user_projects
