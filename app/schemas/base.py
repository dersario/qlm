"""Базовые схемы"""

from pydantic import BaseModel


class BaseSchema(BaseModel):
    """Базовая схема с общими настройками"""

    model_config = {"from_attributes": True}

