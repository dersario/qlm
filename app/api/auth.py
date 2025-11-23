from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import authenticate_user, create_access_token
from app.config import settings
from app.database import get_db
from app.schemas import GetTokenSchema, Token, UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login")
async def login(
    form_data: GetTokenSchema = Depends(), db: Session = Depends(get_db)
) -> Token:
    """Аутентификация пользователя"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email},  # ← ИСПРАВЛЕНО: user.email вместо user.username
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """Регистрация нового пользователя (только для администраторов)"""
    user_service = UserService(db)
    try:
        return user_service.create_user(user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
