from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.models.friend import Friend, FriendStatus
from app.schemas.friend import FriendCreate, FriendUpdate
from app.models.user import User
from app.core.logger import logger
from app.services.user import get_user_by_email


async def get_friend(
    db: AsyncSession, friend_relation_id: int, user_id: int
) -> Optional[Friend]:
    """
    Получение отношения дружбы по ID
    """
    result = await db.execute(
        select(Friend).where(
            Friend.id == friend_relation_id,
            or_(Friend.user_id == user_id, Friend.friend_id == user_id),
        )
    )
    return result.scalar_one_or_none()


async def get_all_friends(
    db: AsyncSession, user_id: int, status: Optional[str] = None
) -> List[Friend]:
    """
    Получение всех отношений дружбы пользователя
    """
    query = select(Friend).where(
        or_(Friend.user_id == user_id, Friend.friend_id == user_id)
    )

    if status:
        query = query.where(Friend.status == status)

    result = await db.execute(query)
    return result.scalars().all()


async def get_friend_relation(
    db: AsyncSession, user_id: int, friend_id: int
) -> Optional[Friend]:
    """
    Проверка существования отношения дружбы между пользователями
    """
    result = await db.execute(
        select(Friend).where(
            or_(
                and_(Friend.user_id == user_id, Friend.friend_id == friend_id),
                and_(Friend.user_id == friend_id, Friend.friend_id == user_id),
            )
        )
    )
    return result.scalar_one_or_none()


async def create_friend_request(
    db: AsyncSession, friend: FriendCreate, user_id: int
) -> Friend:
    """
    Создание запроса на дружбу
    """
    existing_relation = await get_friend_relation(
        db, user_id, friend.friend_id
    )
    if existing_relation:
        return existing_relation

    db_friend = Friend(
        user_id=user_id,
        friend_id=friend.friend_id,
        status=FriendStatus.PENDING,
    )
    db.add(db_friend)
    await db.commit()
    await db.refresh(db_friend)
    return db_friend


async def create_friend_request_by_email(
    db: AsyncSession, email: str, user_id: int
) -> Optional[Friend]:
    """
    Создание запроса на дружбу по email
    """
    logger.info(f"Поиск пользователя с email: {email}")
    friend_user = await get_user_by_email(db, email=email)

    if not friend_user:
        logger.warning(f"Пользователь с email {email} не найден")
        return None

    if friend_user.id == user_id:
        logger.warning(
            f"Попытка добавить себя в друзья: user_id={user_id}, email={email}"
        )
        return None

    existing_relation = await get_friend_relation(db, user_id, friend_user.id)
    if existing_relation:
        logger.info(
            f"Найдено существующее отношение дружбы: {existing_relation.id}"
        )
        return existing_relation

    logger.info(
        f"Создание нового запроса на дружбу: от user_id={user_id} к friend_id={friend_user.id}"
    )
    db_friend = Friend(
        user_id=user_id, friend_id=friend_user.id, status=FriendStatus.PENDING
    )
    db.add(db_friend)
    await db.commit()
    await db.refresh(db_friend)
    logger.info(f"Запрос дружбы создан: id={db_friend.id}")
    return db_friend


async def update_friend_status(
    db: AsyncSession,
    friend_relation_id: int,
    friend_update: FriendUpdate,
    user_id: int,
) -> Optional[Friend]:
    """
    Обновление статуса дружбы (принятие или отклонение запроса)
    """
    db_friend = await get_friend(db, friend_relation_id, user_id)
    if not db_friend:
        return None

    if db_friend.friend_id != user_id:
        return None

    db_friend.status = friend_update.status
    await db.commit()
    await db.refresh(db_friend)
    return db_friend


async def delete_friend(
    db: AsyncSession, friend_relation_id: int, user_id: int
) -> bool:
    """
    Удаление отношения дружбы
    """
    db_friend = await get_friend(db, friend_relation_id, user_id)
    if not db_friend:
        return False

    await db.delete(db_friend)
    await db.commit()
    return True
