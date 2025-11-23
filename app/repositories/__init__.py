"""Репозитории для доступа к данным (Data Access Layer)"""

from app.repositories.lead_repository import LeadRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository

__all__ = ["UserRepository", "ProjectRepository", "LeadRepository"]
