"""Схемы Pydantic для валидации данных"""

from app.schemas.auth import GetTokenSchema, Token
from app.schemas.leads import (
    DashboardStats,
    LeadCommentCreate,
    LeadCommentResponse,
    LeadCreate,
    LeadCreateExternal,
    LeadDetailResponse,
    LeadExport,
    LeadFilter,
    LeadResponse,
    LeadStatusHistoryResponse,
    LeadUpdate,
)
from app.schemas.projects import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectUserAssignment,
)
from app.schemas.users import UserCreate, UserLogin, UserResponse, UserUpdate
from app.schemas.webhooks import WebhookLogResponse

__all__ = [
    # Auth
    "GetTokenSchema",
    "Token",
    # Users
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    # Projects
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectUserAssignment",
    # Leads
    "LeadCreate",
    "LeadCreateExternal",
    "LeadUpdate",
    "LeadResponse",
    "LeadDetailResponse",
    "LeadFilter",
    "LeadExport",
    "LeadCommentCreate",
    "LeadCommentResponse",
    "LeadStatusHistoryResponse",
    "DashboardStats",
    # Webhooks
    "WebhookLogResponse",
]
