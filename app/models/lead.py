"""Модели заявок"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import LeadStatus


class Lead(Base):
    """Модель заявки"""

    __tablename__ = "leads"


    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id"), nullable=False
    )

    # Основные поля
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # UTM метки
    utm_source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    utm_medium: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    utm_campaign: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    utm_term: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    utm_content: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Дополнительные поля (JSON)
    custom_fields: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Статус и управление
    status: Mapped[LeadStatus] = mapped_column(Enum(LeadStatus), default=LeadStatus.NEW)
    assigned_to: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    priority: Mapped[int] = mapped_column(
        Integer, default=1
    )  # 1-5, где 5 - высший приоритет

    # Метаданные
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referrer: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Связи
    project: Mapped["Project"] = relationship("Project", back_populates="leads")
    assigned_user: Mapped[Optional["User"]] = relationship("User")
    status_history: Mapped[list["LeadStatusHistory"]] = relationship(
        "LeadStatusHistory", back_populates="lead"
    )
    comments: Mapped[list["LeadComment"]] = relationship(
        "LeadComment", back_populates="lead"
    )


class LeadStatusHistory(Base):
    """История изменения статусов заявок"""

    __tablename__ = "lead_status_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("leads.id"), nullable=False
    )
    old_status: Mapped[Optional[LeadStatus]] = mapped_column(
        Enum(LeadStatus), nullable=True
    )
    new_status: Mapped[LeadStatus] = mapped_column(Enum(LeadStatus), nullable=False)
    changed_by: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Связи
    lead: Mapped["Lead"] = relationship("Lead", back_populates="status_history")
    user: Mapped[Optional["User"]] = relationship("User")


class LeadComment(Base):
    """Комментарии к заявкам"""

    __tablename__ = "lead_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("leads.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(
        Boolean, default=False
    )  # Внутренний комментарий
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Связи
    lead: Mapped["Lead"] = relationship("Lead", back_populates="comments")
    user: Mapped["User"] = relationship("User")

