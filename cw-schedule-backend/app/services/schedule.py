from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate


async def get_schedule(
    db: AsyncSession, schedule_id: int, user_id: int
) -> Optional[Schedule]:
    result = await db.execute(
        select(Schedule).where(
            Schedule.id == schedule_id, Schedule.user_id == user_id
        )
    )
    return result.scalar_one_or_none()

async def get_schedules(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Schedule]:
    query = select(Schedule).where(Schedule.user_id == user_id)

    if start_date:
        query = query.where(Schedule.start_time >= start_date)
    if end_date:
        query = query.where(Schedule.end_time <= end_date)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


async def create_schedule(
    db: AsyncSession, schedule: ScheduleCreate, user_id: int
) -> Schedule:
    db_schedule = Schedule(
        **schedule.dict(), user_id=user_id, created_at=datetime.utcnow()
    )
    db.add(db_schedule)
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule


async def update_schedule(
    db: AsyncSession, schedule_id: int, schedule: ScheduleUpdate, user_id: int
) -> Optional[Schedule]:
    db_schedule = await get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return None

    for field, value in schedule.dict(exclude_unset=True).items():
        setattr(db_schedule, field, value)

    db_schedule.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(db_schedule)
    return db_schedule


async def delete_schedule(
    db: AsyncSession, schedule_id: int, user_id: int
) -> bool:
    db_schedule = await get_schedule(db, schedule_id, user_id)
    if not db_schedule:
        return False

    await db.delete(db_schedule)
    await db.commit()
    return True
