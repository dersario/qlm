"""Схемы для аутентификации"""

from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints

from app.schemas.base import BaseSchema


class GetTokenSchema(BaseModel):
    """Схема для получения токена"""

    username: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ]
    password: Annotated[str, StringConstraints(min_length=6)]


class Token(BaseSchema):
    """Схема токена доступа"""

    access_token: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ]
    token_type: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1)
    ] = Field(default="bearer")

