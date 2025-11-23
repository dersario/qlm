"""Схемы для вебхуков"""

from datetime import datetime
from typing import Annotated, Optional

from pydantic import StringConstraints

from app.schemas.base import BaseSchema

WebhookUrl = Annotated[str, StringConstraints(max_length=500)]


class WebhookLogResponse(BaseSchema):
    """Схема ответа с логом вебхука"""

    id: int
    webhook_url: WebhookUrl
    response_status: Optional[int] = None
    response_body: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True)]
    ] = None
    error_message: Optional[
        Annotated[str, StringConstraints(strip_whitespace=True)]
    ] = None
    attempt: int
    is_success: bool
    created_at: datetime
