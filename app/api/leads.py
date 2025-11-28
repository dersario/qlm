from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth import get_current_active_user
from app.database import get_db
from app.models import User
from app.models.enums import LeadStatus
from app.schemas import (
    DashboardStats,
    LeadCommentCreate,
    LeadCommentResponse,
    LeadCreate,
    LeadDetailResponse,
    LeadFilter,
    LeadResponse,
    LeadUpdate,
)
from app.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    project_id: int = None,
    status: Optional[str] = None,
    assigned_to: int = None,
    priority: int = None,
    search: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение списка заявок с фильтрацией"""
    # Создаем фильтр
    filters = LeadFilter(
        project_id=project_id,
        status=status,
        assigned_to=assigned_to,
        priority=priority,
        search=search,
    )

    lead_service = LeadService(db)
    leads = lead_service.get_leads(
        filters=filters, skip=skip, limit=limit, user=current_user
    )
    return leads


@router.get("/{lead_id}", response_model=LeadDetailResponse)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение детальной информации о заявке"""
    lead_service = LeadService(db)
    lead = lead_service.get_lead(lead_id=lead_id)
    if lead is None:
        raise HTTPException(status_code=404, detail="Заявка не найдена")

    # Проверяем доступ
    if not lead_service.check_user_access(current_user, lead):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав доступа к заявке",
        )

    return lead


@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead: LeadCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Создание новой заявки"""
    # Получаем IP и User-Agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")

    lead_service = LeadService(db)
    try:
        return lead_service.create_lead(
            lead=lead,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
            user=current_user,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Обновление заявки"""
    lead_service = LeadService(db)
    try:
        return lead_service.update_lead(
            lead_id=lead_id, lead_update=lead_update, user=current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{lead_id}/status", response_model=LeadResponse)
async def update_lead_status(
    lead_id: int,
    new_status: LeadStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Обновление заявки"""
    lead_service = LeadService(db)
    try:
        return lead_service.update_lead(
            lead_id=lead_id, lead_update=new_status, user=current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Удаление заявки"""
    lead_service = LeadService(db)
    try:
        success = lead_service.delete_lead(lead_id=lead_id, user=current_user)
        if not success:
            raise HTTPException(status_code=404, detail="Заявка не найдена")
        return {"message": "Заявка успешно удалена"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{lead_id}/comments", response_model=LeadCommentResponse)
async def add_comment(
    lead_id: int,
    comment_data: LeadCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Добавление комментария к заявке"""
    lead_service = LeadService(db)
    try:
        return lead_service.add_comment(
            lead_id=lead_id, comment_data=comment_data, user=current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/stats/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Получение статистики для дашборда"""
    lead_service = LeadService(db)
    try:
        return lead_service.get_dashboard_stats(
            project_id=project_id, user=current_user
        )
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
