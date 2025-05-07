from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.models.schedule import Schedule
from app.models.shared_schedule import SharedSchedule, PermissionLevel
from app.models.friend import Friend, FriendStatus
from app.services.friend import get_friend_relation
from app.schemas.shared_schedule import (
    SharedScheduleCreate,
    SharedScheduleUpdate,
)


async def get_shared_schedule(
    db: AsyncSession, shared_id: int, user_id: int
) -> Optional[SharedSchedule]:
    """
    Получение общего события по ID
    """
    result = await db.execute(
        select(SharedSchedule).where(
            SharedSchedule.id == shared_id,
            or_(
                SharedSchedule.user_id == user_id,
                SharedSchedule.shared_with_id == user_id,
            ),
        )
    )
    return result.scalar_one_or_none()


async def get_shared_schedules_by_owner(
    db: AsyncSession, user_id: int
) -> List[SharedSchedule]:
    """
    Получение всех событий, которыми поделился пользователь
    """
    result = await db.execute(
        select(SharedSchedule).where(SharedSchedule.user_id == user_id)
    )
    return result.scalars().all()


async def get_shared_schedules_with_user(
    db: AsyncSession, user_id: int
) -> List[SharedSchedule]:
    """
    Получение всех событий, которыми поделились с пользователем
    """
    result = await db.execute(
        select(SharedSchedule).where(SharedSchedule.shared_with_id == user_id)
    )
    return result.scalars().all()

async def get_shared_schedules_with_user_with_data(
    db: AsyncSession, user_id: int
) -> List[Schedule]:
    """
    Получение всех событий, которыми поделились с пользователем,
    включая полные данные о самих событиях
    """
    result = await db.execute(
        select(Schedule)
        .join(SharedSchedule, Schedule.id == SharedSchedule.schedule_id)
        .where(SharedSchedule.shared_with_id == user_id)
    )
    return result.scalars().all()


async def create_shared_schedule(
    db: AsyncSession, shared_schedule: SharedScheduleCreate, user_id: int
) -> Optional[SharedSchedule]:
    """
    Создание общего события
    """
    friend_relation = await get_friend_relation(
        db, user_id, shared_schedule.shared_with_id
    )
    if not friend_relation or friend_relation.status != FriendStatus.ACCEPTED:
        return None

    result = await db.execute(
        select(SharedSchedule).where(
            SharedSchedule.user_id == user_id,
            SharedSchedule.shared_with_id == shared_schedule.shared_with_id,
            SharedSchedule.schedule_id == shared_schedule.schedule_id,
        )
    )
    existing_share = result.scalar_one_or_none()
    if existing_share:
        return existing_share

    db_shared_schedule = SharedSchedule(
        user_id=user_id,
        shared_with_id=shared_schedule.shared_with_id,
        schedule_id=shared_schedule.schedule_id,
        permission_level=shared_schedule.permission_level,
    )
    db.add(db_shared_schedule)
    await db.commit()
    await db.refresh(db_shared_schedule)
    return db_shared_schedule


async def update_shared_schedule(
    db: AsyncSession,
    shared_id: int,
    shared_update: SharedScheduleUpdate,
    user_id: int,
) -> Optional[SharedSchedule]:
    """
    Обновление разрешений для общего события
    """
    db_shared_schedule = await get_shared_schedule(db, shared_id, user_id)
    if not db_shared_schedule or db_shared_schedule.user_id != user_id:
        return None

    db_shared_schedule.permission_level = shared_update.permission_level
    await db.commit()
    await db.refresh(db_shared_schedule)
    return db_shared_schedule


async def delete_shared_schedule(
    db: AsyncSession, shared_id: int, user_id: int
) -> bool:
    """
    Удаление общего события
    """
    db_shared_schedule = await get_shared_schedule(db, shared_id, user_id)
    if not db_shared_schedule or db_shared_schedule.user_id != user_id:
        return False

    await db.delete(db_shared_schedule)
    await db.commit()
    return True
