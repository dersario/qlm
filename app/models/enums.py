"""Перечисления для моделей"""

import enum


class UserRole(str, enum.Enum):
    """Роли пользователей"""

    ADMIN = "admin"
    OPERATOR = "operator"


class LeadStatus(str, enum.Enum):
    """Статусы заявок"""

    NEW = "new"
    IN_PROGRESS = "in_progress"
    CALLBACK = "callback"
    SUCCESS = "success"
    FAILED = "failed"
