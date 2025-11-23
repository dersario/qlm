from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from app.models import User, Project, Lead, LeadStatusHistory, LeadComment, ProjectUser
from app.schemas import (
    UserCreate, UserUpdate, ProjectCreate, ProjectUpdate,
    LeadCreate, LeadUpdate, LeadFilter, LeadCommentCreate
)
from app.auth import get_password_hash, generate_api_key


# CRUD для пользователей
class UserCRUD:
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            role=user.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            update_data = user_update.dict(exclude_unset=True)
            if "password" in update_data:
                update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
            
            for field, value in update_data.items():
                setattr(db_user, field, value)
            
            db.commit()
            db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False


# CRUD для проектов
class ProjectCRUD:
    @staticmethod
    def get_project(db: Session, project_id: int) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id).first()
    
    @staticmethod
    def get_project_by_api_key(db: Session, api_key: str) -> Optional[Project]:
        return db.query(Project).filter(Project.api_key == api_key).first()
    
    @staticmethod
    def get_projects(db: Session, skip: int = 0, limit: int = 100) -> List[Project]:
        return db.query(Project).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_project(db: Session, project: ProjectCreate) -> Project:
        api_key = generate_api_key()
        db_project = Project(
            name=project.name,
            description=project.description,
            api_key=api_key,
            webhook_url=project.webhook_url,
            webhook_headers=project.webhook_headers,
            custom_fields_schema=project.custom_fields_schema,
            status_config=project.status_config
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    
    @staticmethod
    def update_project(db: Session, project_id: int, project_update: ProjectUpdate) -> Optional[Project]:
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if db_project:
            update_data = project_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_project, field, value)
            
            db.commit()
            db.refresh(db_project)
        return db_project
    
    @staticmethod
    def delete_project(db: Session, project_id: int) -> bool:
        db_project = db.query(Project).filter(Project.id == project_id).first()
        if db_project:
            db.delete(db_project)
            db.commit()
            return True
        return False
    
    @staticmethod
    def assign_user_to_project(db: Session, project_id: int, user_id: int) -> bool:
        # Проверяем, не назначен ли уже пользователь
        existing = db.query(ProjectUser).filter(
            and_(ProjectUser.project_id == project_id, ProjectUser.user_id == user_id)
        ).first()
        
        if existing:
            return False
        
        assignment = ProjectUser(project_id=project_id, user_id=user_id)
        db.add(assignment)
        db.commit()
        return True
    
    @staticmethod
    def remove_user_from_project(db: Session, project_id: int, user_id: int) -> bool:
        assignment = db.query(ProjectUser).filter(
            and_(ProjectUser.project_id == project_id, ProjectUser.user_id == user_id)
        ).first()
        
        if assignment:
            db.delete(assignment)
            db.commit()
            return True
        return False


# CRUD для заявок
class LeadCRUD:
    @staticmethod
    def get_lead(db: Session, lead_id: int) -> Optional[Lead]:
        return db.query(Lead).filter(Lead.id == lead_id).first()
    
    @staticmethod
    def get_leads(
        db: Session,
        filters: Optional[LeadFilter] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Lead]:
        query = db.query(Lead)
        
        if filters:
            if filters.project_id:
                query = query.filter(Lead.project_id == filters.project_id)
            if filters.status:
                query = query.filter(Lead.status == filters.status)
            if filters.assigned_to:
                query = query.filter(Lead.assigned_to == filters.assigned_to)
            if filters.priority:
                query = query.filter(Lead.priority == filters.priority)
            if filters.date_from:
                query = query.filter(Lead.created_at >= filters.date_from)
            if filters.date_to:
                query = query.filter(Lead.created_at <= filters.date_to)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        Lead.name.ilike(search_term),
                        Lead.phone.ilike(search_term),
                        Lead.email.ilike(search_term)
                    )
                )
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_lead(db: Session, lead: LeadCreate, ip_address: str = None, user_agent: str = None) -> Lead:
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
            user_agent=user_agent
        )
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        
        # Создаем запись в истории статусов
        history = LeadStatusHistory(
            lead_id=db_lead.id,
            new_status=db_lead.status,
            comment="Заявка создана"
        )
        db.add(history)
        db.commit()
        
        return db_lead
    
    @staticmethod
    def update_lead(db: Session, lead_id: int, lead_update: LeadUpdate, changed_by: int = None) -> Optional[Lead]:
        db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if db_lead:
            old_status = db_lead.status
            
            update_data = lead_update.dict(exclude_unset=True)
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
                    changed_by=changed_by
                )
                db.add(history)
                db.commit()
        
        return db_lead
    
    @staticmethod
    def delete_lead(db: Session, lead_id: int) -> bool:
        db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if db_lead:
            db.delete(db_lead)
            db.commit()
            return True
        return False
    
    @staticmethod
    def add_comment(db: Session, lead_id: int, comment_data: LeadCommentCreate, user_id: int) -> Optional[LeadComment]:
        db_comment = LeadComment(
            lead_id=lead_id,
            user_id=user_id,
            comment=comment_data.comment,
            is_internal=comment_data.is_internal
        )
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    
    @staticmethod
    def get_lead_stats(db: Session, project_id: Optional[int] = None) -> Dict[str, Any]:
        query = db.query(Lead)
        if project_id:
            query = query.filter(Lead.project_id == project_id)
        
        total = query.count()
        
        # Статистика по статусам
        status_stats = {}
        for status in ["new", "in_progress", "callback", "success", "failed"]:
            count = query.filter(Lead.status == status).count()
            status_stats[status] = count
        
        # Статистика по периодам
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        leads_today = query.filter(Lead.created_at >= today).count()
        leads_week = query.filter(Lead.created_at >= week_ago).count()
        leads_month = query.filter(Lead.created_at >= month_ago).count()
        
        # Конверсия
        success_count = status_stats.get("success", 0)
        conversion_rate = (success_count / total * 100) if total > 0 else 0
        
        return {
            "total_leads": total,
            "leads_by_status": status_stats,
            "leads_today": leads_today,
            "leads_this_week": leads_week,
            "leads_this_month": leads_month,
            "conversion_rate": round(conversion_rate, 2)
        }


# Создаем экземпляры CRUD классов
user_crud = UserCRUD()
project_crud = ProjectCRUD()
lead_crud = LeadCRUD()
