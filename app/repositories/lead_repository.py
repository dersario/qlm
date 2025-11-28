"""Репозиторий для работы с заявками"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.enums import LeadStatus
from app.models.lead import Lead, LeadComment, LeadStatusHistory
from app.schemas import LeadCommentCreate, LeadCreate, LeadFilter, LeadUpdate


class LeadRepository:
    """Репозиторий для доступа к данным заявок"""

    @staticmethod
    def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
        """Получить заявку по ID"""
        stmt = select(Lead).where(Lead.id == lead_id)
        return db.scalar(stmt)

    @staticmethod
    def get_leads(
        db: Session,
        filters: Optional[LeadFilter] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Lead]:
        """Получить список заявок с фильтрацией"""
        stmt = select(Lead)

        if filters:
            if filters.project_id:
                stmt = stmt.where(Lead.project_id == filters.project_id)
            if filters.status:
                stmt = stmt.where(Lead.status == filters.status)
            if filters.assigned_to:
                stmt = stmt.where(Lead.assigned_to == filters.assigned_to)
            if filters.priority:
                stmt = stmt.where(Lead.priority == filters.priority)
            if filters.date_from:
                stmt = stmt.where(Lead.created_at >= filters.date_from)
            if filters.date_to:
                stmt = stmt.where(Lead.created_at <= filters.date_to)
            if filters.search:
                search_term = f"%{filters.search}%"
                stmt = stmt.where(
                    or_(
                        Lead.name.ilike(search_term),
                        Lead.phone.ilike(search_term),
                        Lead.email.ilike(search_term),
                    )
                )

        stmt = stmt.offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    @staticmethod
    def create_lead(
        db: Session,
        lead: LeadCreate,
        ip_address: str = None,
        user_agent: str = None,
        referrer: str = None,
    ) -> Lead:
        """Создать новую заявку"""
        db_lead = Lead(
            project_id=lead.project_id,
            name=lead.name,
            phone=lead.phone,
            email=lead.email,
            message=lead.message,
            utm_source=lead.utm_source,
            utm_medium=lead.utm_medium,
            utm_campaign=lead.utm_campaign,
            utm_term=lead.utm_term,
            utm_content=lead.utm_content,
            custom_fields=lead.custom_fields,
            ip_address=ip_address,
            user_agent=user_agent,
            referrer=referrer,
        )
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)

        # Создаем запись в истории статусов
        history = LeadStatusHistory(
            lead_id=db_lead.id, new_status=db_lead.status, comment="Заявка создана"
        )
        db.add(history)
        db.commit()

        return db_lead

    @staticmethod
    def update_lead(
        db: Session,
        lead_id: int,
        lead_update: LeadUpdate | LeadStatus,
        changed_by: int = None,
    ) -> Optional[Lead]:
        """Обновить заявку"""
        stmt = select(Lead).where(Lead.id == lead_id)
        db_lead = db.scalar(stmt)
        if db_lead:
            old_status = db_lead.status

            if isinstance(lead_update, LeadUpdate):
                update_data = lead_update.model_dump(exclude_unset=True)
            if lead_update in LeadStatus:
                update_data = LeadUpdate.model_validate(db_lead)
                update_data.status = lead_update
                update_data = update_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_lead, field, value)

            db.commit()
            db.refresh(db_lead)

            # Если изменился статус, добавляем в историю
            if "status" in update_data and old_status != db_lead.status:
                history = LeadStatusHistory(
                    lead_id=lead_id,
                    old_status=old_status,
                    new_status=db_lead.status,
                    changed_by=changed_by,
                )
                db.add(history)
                db.commit()

        return db_lead

    @staticmethod
    def delete_lead(db: Session, lead_id: int) -> bool:
        """Удалить заявку"""
        stmt = select(Lead).where(Lead.id == lead_id)
        db_lead = db.scalar(stmt)
        if db_lead:
            db.delete(db_lead)
            db.commit()
            return True
        return False

    @staticmethod
    def add_comment(
        db: Session, lead_id: int, comment_data: LeadCommentCreate, user_id: int
    ) -> Optional[LeadComment]:
        """Добавить комментарий к заявке"""
        db_comment = LeadComment(
            lead_id=lead_id,
            user_id=user_id,
            comment=comment_data.comment,
            is_internal=comment_data.is_internal,
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def get_lead_stats(db: Session, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Получить статистику по заявкам"""
        # Базовое условие
        conditions = []
        if project_id:
            conditions.append(Lead.project_id == project_id)

        # Общее количество
        total_stmt = select(func.count(Lead.id))
        if conditions:
            total_stmt = total_stmt.where(*conditions)
        total = db.scalar(total_stmt) or 0

        # Статистика по статусам
        status_stats = {}
        for status in ["new", "in_progress", "callback", "success", "failed"]:
            stmt = select(func.count(Lead.id)).where(Lead.status == status)
            if conditions:
                stmt = stmt.where(*conditions)
            count = db.scalar(stmt) or 0
            status_stats[status] = count

        # Статистика по периодам
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        leads_today_stmt = select(func.count(Lead.id)).where(Lead.created_at >= today)
        if conditions:
            leads_today_stmt = leads_today_stmt.where(*conditions)
        leads_today = db.scalar(leads_today_stmt) or 0

        leads_week_stmt = select(func.count(Lead.id)).where(Lead.created_at >= week_ago)
        if conditions:
            leads_week_stmt = leads_week_stmt.where(*conditions)
        leads_week = db.scalar(leads_week_stmt) or 0

        leads_month_stmt = select(func.count(Lead.id)).where(
            Lead.created_at >= month_ago
        )
        if conditions:
            leads_month_stmt = leads_month_stmt.where(*conditions)
        leads_month = db.scalar(leads_month_stmt) or 0

        # Конверсия
        success_count = status_stats.get("success", 0)
        conversion_rate = (success_count / total * 100) if total > 0 else 0

        return {
            "total_leads": total,
            "leads_by_status": status_stats,
            "leads_today": leads_today,
            "leads_this_week": leads_week,
            "leads_this_month": leads_month,
            "conversion_rate": round(conversion_rate, 2),
        }
