"""Схемы для заявок"""

from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

from pydantic import EmailStr, Field, StringConstraints

from app.models.lead import LeadStatus
from app.schemas.base import BaseSchema
from app.schemas.projects import ProjectResponse
from app.schemas.users import UserResponse


class LeadBase(BaseSchema):
    """Базовая схема заявки"""

    name: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    ] = None
    phone: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
    ] = None
    email: Optional[EmailStr] = None
    message: Optional[Annotated[str, StringConstraints(strip_whitespace=True)]] = None

    # UTM метки
    utm_source: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    ] = None
    utm_medium: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    ] = None
    utm_campaign: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    ] = None
    utm_term: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    ] = None
    utm_content: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    ] = None

    # Дополнительные поля
    custom_fields: Optional[Dict[str, Any]] = None


class LeadCreate(LeadBase):
    """Схема создания заявки"""

    project_id: int


class LeadCreateExternal(LeadBase):
    """Схема для внешнего API (без project_id)"""

    pass


class LeadUpdate(BaseSchema):
    """Схема обновления заявки"""

    model_config = {"from_attributes": True}

    name: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    ] = None
    phone: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
    ] = None
    email: Optional[EmailStr] = None
    message: Optional[Annotated[str, StringConstraints(strip_whitespace=True)]] = None
    status: Optional[LeadStatus] = None
    assigned_to: Optional[int] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    custom_fields: Optional[Dict[str, Any]] = None


class LeadResponse(LeadBase):
    """Схема ответа с данными заявки"""

    id: int
    project_id: int
    status: LeadStatus
    assigned_to: Optional[int] = None
    priority: int
    ip_address: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=45)]
    ] = None
    user_agent: Optional[Annotated[str, StringConstraints(strip_whitespace=True)]] = (
        None
    )
    referrer: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=500)]
    ] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class LeadStatusHistoryResponse(BaseSchema):
    """Схема истории изменения статусов"""

    id: int
    old_status: Optional[LeadStatus] = None
    new_status: LeadStatus
    changed_by: Optional[int] = None
    comment: Optional[Annotated[str, StringConstraints(strip_whitespace=True)]] = None
    created_at: datetime
    user: Optional[UserResponse] = None


class LeadCommentCreate(BaseSchema):
    """Схема создания комментария"""

    comment: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1000)
    ]
    is_internal: bool = False


class LeadCommentResponse(BaseSchema):
    """Схема ответа с комментарием"""

    id: int
    comment: Annotated[str, StringConstraints(min_length=1)]
    is_internal: bool
    created_at: datetime
    user: UserResponse


class LeadDetailResponse(LeadResponse):
    """Детальная информация о заявке с дополнительными данными"""

    project: ProjectResponse
    assigned_user: Optional[UserResponse] = None
    status_history: List[LeadStatusHistoryResponse] = []
    comments: List[LeadCommentResponse] = []


class LeadFilter(BaseSchema):
    """Фильтры для поиска заявок"""

    project_id: Optional[int] = None
    status: Optional[LeadStatus] = None
    assigned_to: Optional[int] = None
    priority: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search: Optional[Annotated[str, StringConstraints(strip_whitespace=True)]] = (
        None  # Поиск по имени, телефону, email
    )


class LeadExport(BaseSchema):
    """Параметры экспорта заявок"""

    format: Annotated[str, StringConstraints(pattern="^(csv|xlsx)$")] = "csv"
    filters: Optional[LeadFilter] = None


class DashboardStats(BaseSchema):
    """Схема статистики для дашборда"""

    total_leads: int
    leads_by_status: Dict[str, int]
    leads_today: int
    leads_this_week: int
    leads_this_month: int
    conversion_rate: float
