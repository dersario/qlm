"""Схемы для проектов"""

from datetime import datetime
from typing import Annotated, Any, Dict, Optional

from pydantic import Field, StringConstraints

from app.schemas.base import BaseSchema

# Типы для URL валидации
WebhookUrl = Annotated[str, StringConstraints(max_length=500)]


class ProjectBase(BaseSchema):
    """Базовая схема проекта"""

    name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
    ]
    description: Optional[Annotated[str, StringConstraints(strip_whitespace=True)]] = (
        None
    )
    webhook_url: Optional[WebhookUrl] = None
    webhook_headers: Optional[Dict[str, str]] = None
    custom_fields_schema: Optional[Dict[str, Any]] = None
    status_config: Optional[Dict[str, Any]] = None


class ProjectCreate(ProjectBase):
    """Схема создания проекта"""

    pass


class ProjectUpdate(BaseSchema):
    """Схема обновления проекта"""

    name: Optional[
        Annotated[
            str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)
        ]
    ] = None
    description: Optional[Annotated[str, StringConstraints(strip_whitespace=True)]] = (
        None
    )
    webhook_url: Optional[WebhookUrl] = None
    webhook_headers: Optional[Dict[str, str]] = None
    custom_fields_schema: Optional[Dict[str, Any]] = None
    status_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ProjectResponse(ProjectBase):
    """Схема ответа с данными проекта"""

    id: int
    api_key: Annotated[str, StringConstraints(min_length=1)]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    leads_count: Annotated[int, Field(default=0)]


class ProjectUserAssignment(BaseSchema):
    """Схема назначения пользователя на проект"""

    user_id: int
