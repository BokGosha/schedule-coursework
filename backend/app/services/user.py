from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Dict, Any

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.logger import logger
from app.core.security import get_password_hash, verify_password


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def create(self, user_data: UserCreate) -> User:
        try:
            user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=get_password_hash(user_data.password),
                is_active=True,
                is_superuser=False,
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(f"Created new user: {user.username}")
            return user
        except IntegrityError:
            await self.db.rollback()
            logger.error(f"Failed to create user: {user_data.username}")
            raise

    async def update(self, user: User, user_data: UserUpdate) -> User:
        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.db.commit()
        await self.db.refresh(user)
        logger.info(f"Updated user: {user.username}")
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()
        logger.info(f"Deleted user: {user.username}")


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Получение пользователя по ID
    """
    try:
        user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        result = await db.execute(select(User).where(User.id == user_id_int))
        return result.scalar_one_or_none()
    except ValueError:
        logger.error(
            f"Невозможно преобразовать ID пользователя '{user_id}' в int"
        )
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя по ID: {str(e)}")
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Получение пользователя по email
    """
    try:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Ошибка при получении пользователя по email: {str(e)}")
        return None


async def get_user_by_username(
    db: AsyncSession, username: str
) -> Optional[User]:
    """
    Получение пользователя по имени пользователя
    """
    try:
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        logger.error(
            f"Ошибка при получении пользователя по username: {str(e)}"
        )
        return None


async def get_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[User]:
    """
    Получение списка пользователей
    """
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """
    Создание нового пользователя
    """
    try:
        db_user_email = await get_user_by_email(db, email=user.email)
        if db_user_email:
            raise ValueError("Email уже зарегистрирован")

        db_user_username = await get_user_by_username(
            db, username=user.username
        )
        if db_user_username:
            raise ValueError("Имя пользователя уже занято")

        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        logger.info(
            f"Пользователь создан: ID={db_user.id}, username={db_user.username}"
        )
        return db_user
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при создании пользователя: {str(e)}")
        raise


async def update_user(
    db: AsyncSession, user_id: int, user: UserUpdate
) -> Optional[User]:
    """
    Обновление данных пользователя
    """
    try:
        db_user = await get_user(db, user_id=user_id)
        if not db_user:
            return None

        update_data = user.dict(exclude_unset=True)

        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(
                update_data.pop("password")
            )

        if "email" in update_data and update_data["email"] != db_user.email:
            existing_user = await get_user_by_email(
                db, email=update_data["email"]
            )
            if existing_user:
                raise ValueError("Email уже зарегистрирован")

        if (
            "username" in update_data
            and update_data["username"] != db_user.username
        ):
            existing_user = await get_user_by_username(
                db, username=update_data["username"]
            )
            if existing_user:
                raise ValueError("Имя пользователя уже занято")

        for field, value in update_data.items():
            setattr(db_user, field, value)

        await db.commit()
        await db.refresh(db_user)
        logger.info(
            f"Пользователь обновлен: ID={db_user.id}, username={db_user.username}"
        )
        return db_user
    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка при обновлении пользователя: {str(e)}")
        raise


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Удаление пользователя
    """
    db_user = await get_user(db, user_id=user_id)
    if not db_user:
        return False

    await db.delete(db_user)
    await db.commit()
    return True
