"""Модели проектов"""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProjectUser(Base):
    """Связь пользователей с проектами"""

    __tablename__ = "project_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Связи
    project: Mapped["Project"] = relationship("Project", back_populates="project_users")
    user: Mapped["User"] = relationship("User", back_populates="project_assignments")


class Project(Base):
    from app.models.lead import Lead

    """Модель проекта"""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    api_key: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    webhook_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    webhook_headers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    custom_fields_schema: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True
    )  # Схема дополнительных полей
    status_config: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True
    )  # Кастомные статусы
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Связи
    leads: Mapped[list["Lead"]] = relationship("Lead", back_populates="project")
    project_users: Mapped[list["ProjectUser"]] = relationship(
        "ProjectUser", back_populates="project"
    )
