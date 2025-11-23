from typing import Any, Dict

import httpx
from sqlalchemy import delete, select

from app.celery_app import celery_app
from app.config import settings
from app.database import SessionLocal
from app.models import Lead, Project, WebhookLog

# Импорт для уведомлений
try:
    from app.notifications import send_slack_notification, send_telegram_notification
except ImportError:
    send_telegram_notification = None
    send_slack_notification = None


@celery_app.task(bind=True, max_retries=3)
def send_webhook(self, project_id: int, lead_id: int):
    """Асинхронная отправка вебхука"""
    db = SessionLocal()
    try:
        # Получаем проект и заявку
        project_stmt = select(Project).where(Project.id == project_id)
        project = db.scalar(project_stmt)
        lead_stmt = select(Lead).where(Lead.id == lead_id)
        lead = db.scalar(lead_stmt)
        if not project or not lead:
            raise Exception(f"Проект {project_id} или заявка {lead_id} не найдены")

        if not project.webhook_url:
            return {"status": "skipped", "reason": "Webhook URL не настроен"}

        # Формируем payload
        payload = {
            "id": lead.id,
            "project_id": project.id,
            "name": lead.name,
            "phone": lead.phone,
            "email": lead.email,
            "message": lead.message,
            "status": lead.status,
            "priority": lead.priority,
            "utm": {
                "source": lead.utm_source,
                "medium": lead.utm_medium,
                "campaign": lead.utm_campaign,
                "term": lead.utm_term,
                "content": lead.utm_content,
            },
            "custom_fields": lead.custom_fields,
            "created_at": lead.created_at.isoformat(),
            "updated_at": lead.updated_at.isoformat() if lead.updated_at else None,
        }

        # Отправляем вебхук
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "QuickLead-Manager/1.0",
        }

        # Добавляем кастомные заголовки если есть
        if project.webhook_headers:
            headers.update(project.webhook_headers)

        # Логируем попытку отправки
        webhook_log = WebhookLog(
            project_id=project_id,
            lead_id=lead_id,
            webhook_url=project.webhook_url,
            payload=payload,
            attempt=self.request.retries + 1,
        )

        with httpx.Client(timeout=settings.webhook_timeout) as client:
            response = client.post(project.webhook_url, json=payload, headers=headers)

            # Записываем результат
            webhook_log.response_status = response.status_code
            webhook_log.response_body = response.text
            webhook_log.is_success = 200 <= response.status_code < 300

            if not webhook_log.is_success:
                webhook_log.error_message = (
                    f"HTTP {response.status_code}: {response.text}"
                )

                # Повторная попытка
                raise Exception(f"Webhook failed with status {response.status_code}")

            db.add(webhook_log)
            db.commit()

            return {
                "status": "success",
                "response_status": response.status_code,
                "attempt": self.request.retries + 1,
            }

    except Exception as exc:
        # Логируем ошибку
        webhook_log = WebhookLog(
            project_id=project_id,
            lead_id=lead_id,
            webhook_url=project.webhook_url if project else "unknown",
            payload=payload if "payload" in locals() else {},
            error_message=str(exc),
            attempt=self.request.retries + 1,
            is_success=False,
        )
        db.add(webhook_log)
        db.commit()

        # Повторная попытка с экспоненциальной задержкой
        raise self.retry(
            exc=exc,
            countdown=60 * (2**self.request.retries),  # 1, 2, 4 минуты
            max_retries=settings.webhook_retry_attempts,
        )

    finally:
        db.close()


@celery_app.task
def send_telegram_notification_task(lead_id: int, message: str):
    """Отправка уведомления в Telegram"""
    if not send_telegram_notification:
        return {"status": "skipped", "reason": "Telegram notifications not configured"}

    try:
        send_telegram_notification(message)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task
def send_slack_notification_task(lead_id: int, message: str):
    """Отправка уведомления в Slack"""
    if not send_slack_notification:
        return {"status": "skipped", "reason": "Slack notifications not configured"}

    try:
        send_slack_notification(message)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@celery_app.task
def validate_phone_task(phone: str) -> Dict[str, Any]:
    """Валидация номера телефона"""
    try:
        import phonenumbers

        parsed = phonenumbers.parse(phone, "RU")  # По умолчанию Россия
        is_valid = phonenumbers.is_valid_number(parsed)
        formatted = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.E164
        )

        return {
            "is_valid": is_valid,
            "formatted": formatted,
            "country_code": parsed.country_code,
            "national_number": parsed.national_number,
        }
    except Exception as e:
        return {"is_valid": False, "error": str(e)}


@celery_app.task
def validate_email_task(email: str) -> Dict[str, Any]:
    """Валидация email адреса"""
    try:
        from email_validator import EmailNotValidError, validate_email

        validated_email = validate_email(email)
        return {
            "is_valid": True,
            "normalized": validated_email.email,
            "domain": validated_email.domain,
        }
    except EmailNotValidError as e:
        return {"is_valid": False, "error": str(e)}
    except Exception as e:
        return {"is_valid": False, "error": str(e)}


@celery_app.task
def cleanup_old_webhook_logs(days: int = 30):
    """Очистка старых логов вебхуков"""
    from datetime import datetime, timedelta, timezone

    db = SessionLocal()
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

        stmt = delete(WebhookLog).where(WebhookLog.created_at < cutoff_date)
        result = db.execute(stmt)
        deleted_count = result.rowcount

        db.commit()

        return {"deleted_logs": deleted_count}
    finally:
        db.close()
