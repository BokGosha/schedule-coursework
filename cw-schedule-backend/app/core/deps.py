from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import get_settings
from app.db.session import get_session
from app.models.user import User
from app.core.security import oauth2_scheme, verify_password
from app.core.logger import logger

settings = get_settings()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для получения асинхронной сессии базы данных.
    """
    async for session in get_session():
        yield session


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Зависимость для получения текущего аутентифицированного пользователя.
    """
    logger.info("Попытка аутентификации по токену")
    logger.debug(f"Полученный токен: {token[:10]}...")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        logger.info(f"Декодирование токена с алгоритмом: {settings.ALGORITHM}")
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        logger.debug(f"Декодированный payload: {payload}")

        user_id = payload.get("sub")
        logger.info(
            f"Получен ID пользователя из токена: {user_id}, тип: {type(user_id)}"
        )

        if user_id is None:
            logger.warning("ID пользователя отсутствует в токене")
            raise credentials_exception

    except JWTError as e:
        logger.error(f"Ошибка декодирования JWT: {str(e)}")
        raise credentials_exception

    try:
        user_id_int = int(user_id)
        logger.info(
            f"Преобразованный ID пользователя: {user_id_int}, тип: {type(user_id_int)}"
        )
        logger.info(f"Поиск пользователя с ID: {user_id_int}")

        # Дополнительный отладочный запрос для проверки существующих пользователей
        all_users_check = await db.execute(
            select(User.id, User.email, User.username)
        )
        users = all_users_check.fetchall()
        logger.debug(f"Существующие пользователи в БД: {users}")

        result = await db.execute(select(User).where(User.id == user_id_int))
        user = result.scalar_one_or_none()

        if user is None:
            logger.warning(
                f"Пользователь с ID {user_id_int} не найден в базе данных"
            )
            raise credentials_exception

        logger.info(
            f"Пользователь найден: ID={user.id}, username={user.username}, email={user.email}"
        )
        return user

    except ValueError as e:
        logger.error(
            f"Ошибка преобразования ID пользователя '{user_id}' в int: {str(e)}"
        )
        raise credentials_exception
    except Exception as e:
        logger.error(
            f"Ошибка при получении пользователя из базы данных: {str(e)}"
        )
        raise credentials_exception
