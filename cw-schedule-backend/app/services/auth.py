from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status, Depends
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import oauth2_scheme, verify_password, get_password_hash
from app.models.user import User
from app.schemas.auth import TokenData
from app.services.user import get_user_by_email, get_user_by_username
from app.db.database import get_db
from app.core.logger import logger

settings = get_settings()


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> Optional[User]:
    """
    Аутентификация пользователя
    """
    logger.info(f"Попытка аутентификации пользователя: {username}")

    user = await get_user_by_email(db, email=username)
    if not user:
        logger.info(
            f"Пользователь с email {username} не найден, пробуем поиск по имени пользователя"
        )
        user = await get_user_by_username(db, username=username)

    if not user:
        logger.warning(f"Пользователь с email/username {username} не найден")
        return None

    logger.info(
        f"Пользователь найден: ID={user.id}, username={user.username}, email={user.email}"
    )

    try:
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Неверный пароль для пользователя {username}")
            return None
    except Exception as e:
        logger.error(f"Ошибка при проверке пароля: {str(e)}")
        return None

    logger.info(f"Пользователь {username} успешно аутентифицирован")
    return user


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """
    Создание JWT-токена
    """
    to_encode = data.copy()
    logger.info(
        f"Создание токена доступа для пользователя с ID: {data.get('sub')}"
    )

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    logger.info(f"Токен истекает: {expire}")
    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        logger.info(
            f"Токен успешно создан для пользователя с ID: {data.get('sub')}"
        )
        return encoded_jwt
    except Exception as e:
        logger.error(f"Ошибка при создании токена: {str(e)}")
        raise
