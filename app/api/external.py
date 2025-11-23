from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.auth import verify_api_key
from app.database import get_db
from app.schemas import LeadCreate, LeadCreateExternal, LeadResponse
from app.services.lead_service import LeadService

router = APIRouter(prefix="/api/v1", tags=["external"])


async def verify_api_key_header(
    x_api_key: str = Header(..., alias="X-API-Key"), db: Session = Depends(get_db)
):
    """Проверка API ключа из заголовка"""
    project = verify_api_key(x_api_key, db)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или неактивный API ключ",
        )
    return project


@router.post("/lead", response_model=LeadResponse)
async def create_lead_external(
    lead_data: LeadCreateExternal,
    request: Request,
    project=Depends(verify_api_key_header),
    db: Session = Depends(get_db),
):
    """Прием заявки через внешний API"""
    # Создаем заявку для проекта
    lead_create = LeadCreate(
        project_id=project.id,
        name=lead_data.name,
        phone=lead_data.phone,
        email=lead_data.email,
        message=lead_data.message,
        utm_source=lead_data.utm_source,
        utm_medium=lead_data.utm_medium,
        utm_campaign=lead_data.utm_campaign,
        utm_term=lead_data.utm_term,
        utm_content=lead_data.utm_content,
        custom_fields=lead_data.custom_fields,
    )

    # Получаем IP и User-Agent
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    referrer = request.headers.get("referer")

    # Создаем заявку через сервис
    lead_service = LeadService(db)
    lead = lead_service.create_lead(
        lead=lead_create,
        ip_address=ip_address,
        user_agent=user_agent,
        referrer=referrer,
    )

    # TODO: Здесь будет асинхронная отправка вебхука
    # await send_webhook_async.delay(project.id, lead.id)

    return lead


@router.get("/health")
async def health_check():
    """Проверка работоспособности API"""
    return {"status": "ok", "message": "QuickLead Manager API работает"}
