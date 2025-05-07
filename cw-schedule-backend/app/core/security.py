from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from jose import jwt
from passlib.context import CryptContext
from app.core.logger import logger
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.config import get_settings

settings = get_settings()

try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception as e:
    logger.error(f"Error initializing CryptContext: {str(e)}")
    if "__about__" in str(e):
        import bcrypt

        if not hasattr(bcrypt, "__about__"):
            bcrypt.__about__ = {"__version__": bcrypt.__version__}
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    else:
        raise

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    scheme_name="Bearer",
    auto_error=True,
    scopes=None,
    description="Bearer token авторизация",
)


def get_password_hash(password: str) -> str:
    """
    Хеширование пароля.
    """
    logger.debug("Hashing password")
    try:
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {str(e)}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля.
    """
    logger.debug("Verifying password")
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {str(e)}")
        return False


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
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
