from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_active_user, get_current_admin_user
from app.database import get_db
from app.models import Project, User
from app.schemas import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectUserAssignment,
    UserResponse,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение списка проектов"""
    project_service = ProjectService(db)
    projects: list[Project] = project_service.get_user_projects(current_user)

    return [
        ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            api_key=project.api_key,
            is_active=project.is_active,
            created_at=project.created_at,
            updated_at=project.updated_at,
            leads_count=len(project.leads),
        )
        for project in projects
    ]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение информации о проекте"""
    project_service = ProjectService(db)
    project = project_service.get_project(project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")

    # Проверяем доступ
    if not project_service.check_user_access(current_user, project_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа к проекту",
        )

    return project


@router.post("/", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Создание нового проекта (только для администраторов)"""
    project_service = ProjectService(db)
    return project_service.create_project(project=project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Обновление проекта (только для администраторов)"""
    project_service = ProjectService(db)
    project = project_service.update_project(
        project_id=project_id, project_update=project_update
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Удаление проекта (только для администраторов)"""
    project_service = ProjectService(db)
    success = project_service.delete_project(project_id=project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Проект не найден")

    return {"message": "Проект успешно удален"}


@router.post("/{project_id}/users", response_model=UserResponse)
async def assign_user_to_project(
    project_id: int,
    assignment: ProjectUserAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Назначение пользователя на проект (только для администраторов)"""
    project_service = ProjectService(db)
    try:
        success = project_service.assign_user_to_project(
            project_id=project_id, user_id=assignment.user_id
        )
        if not success:
            raise HTTPException(
                status_code=400, detail="Пользователь уже назначен на проект"
            )

        from app.services.user_service import UserService

        user_service = UserService(db)
        user = user_service.get_user(assignment.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{project_id}/users/{user_id}")
async def remove_user_from_project(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Удаление пользователя из проекта (только для администраторов)"""
    project_service = ProjectService(db)
    success = project_service.remove_user_from_project(
        project_id=project_id, user_id=user_id
    )
    if not success:
        raise HTTPException(
            status_code=404, detail="Пользователь не назначен на проект"
        )

    return {"message": "Пользователь успешно удален из проекта"}


@router.get("/{project_id}/users", response_model=List[UserResponse])
async def get_project_users(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение списка пользователей проекта"""
    project_service = ProjectService(db)
    project = project_service.get_project(project_id=project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")

    # Проверяем доступ
    if not project_service.check_user_access(current_user, project_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа к проекту",
        )

    users = [assignment.user for assignment in project.project_users]
    return users
