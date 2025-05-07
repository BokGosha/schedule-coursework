from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.config import get_settings
from app.core.security import oauth2_scheme
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserResponse
from app.services.auth import (
    authenticate_user,
    create_access_token,
)
from app.core.deps import get_current_user
from app.core.logger import logger

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials"
        },
    },
)

settings = get_settings()


@router.post("/login", response_model=Token, summary="Вход в систему")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Вход в систему и получение токена доступа.

    - **username**: Email или имя пользователя
    - **password**: Пароль пользователя
    """
    logger.info(
        f"Попытка входа в систему для пользователя: {form_data.username}"
    )

    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(
            f"Неудачная попытка входа для пользователя: {form_data.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        logger.warning(
            f"Попытка входа неактивного пользователя: {form_data.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Учетная запись неактивна",
        )

    logger.info(
        f"Вход пользователя {form_data.username} успешен, создаю токен..."
    )
    logger.debug(
        f"Информация о пользователе: ID={user.id} ({type(user.id)}), email={user.email}, username={user.username}"
    )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    user_id_str = str(user.id)
    logger.debug(
        f"ID пользователя для токена: {user_id_str}, тип: {type(user_id_str)}"
    )

    access_token = create_access_token(
        data={"sub": user_id_str}, expires_delta=access_token_expires
    )

    logger.info(
        f"Токен успешно создан и отправлен для пользователя: {form_data.username}"
    )
    logger.debug(f"Первые 10 символов токена: {access_token[:10]}...")

    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Получение информации о текущем пользователе",
)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Получение информации о текущем аутентифицированном пользователе.
    """
    logger.info(f"Запрос информации о пользователе: ID={current_user.id}")
    logger.debug(
        f"Полная информация о пользователе: ID={current_user.id}, username={current_user.username}, email={current_user.email}, is_active={current_user.is_active}"
    )
    return current_user
