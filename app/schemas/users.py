"""Схемы для пользователей"""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, EmailStr, StringConstraints

from app.models import UserRole
from app.schemas.base import BaseSchema


class UserBase(BaseSchema):
    """Базовая схема пользователя"""

    email: EmailStr
    username: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=3, max_length=100)
    ]
    full_name: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    ] = None
    role: UserRole = UserRole.OPERATOR


class UserCreate(UserBase):
    """Схема создания пользователя"""

    password: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=6, max_length=100)
    ]


class UserUpdate(BaseSchema):
    """Схема обновления пользователя"""

    email: Optional[EmailStr] = None
    username: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=100)]
    ] = None
    full_name: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    ] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Схема ответа с данными пользователя"""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserLogin(BaseSchema):
    """Схема для входа пользователя"""

    username: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ]
    password: Annotated[str, StringConstraints(min_length=6)]

