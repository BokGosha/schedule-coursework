from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleInDB
from app.services.schedule import (
    get_schedule,
    get_schedules,
    create_schedule,
    update_schedule,
    delete_schedule,
)

router = APIRouter()


@router.get(
    "/", response_model=List[ScheduleInDB], summary="Получить список событий"
)
async def read_schedules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
):
    """
    Получить список всех событий текущего пользователя.
    Можно фильтровать по дате начала и окончания.
    """
    schedules = await get_schedules(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        start_date=start_date,
        end_date=end_date,
    )
    return schedules


@router.post("/", response_model=ScheduleInDB, summary="Создать новое событие")
async def create_schedule_endpoint(
    schedule: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создать новое событие в расписании.
    """
    return await create_schedule(
        db=db, schedule=schedule, user_id=current_user.id
    )


@router.get(
    "/{schedule_id}",
    response_model=ScheduleInDB,
    summary="Получить информацию о событии",
)
async def read_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить подробную информацию о конкретном событии.
    """
    schedule = await get_schedule(
        db=db, schedule_id=schedule_id, user_id=current_user.id
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return schedule


@router.put(
    "/{schedule_id}", response_model=ScheduleInDB, summary="Обновить событие"
)
async def update_schedule_endpoint(
    schedule_id: int,
    schedule: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить информацию о событии.
    """
    updated_schedule = await update_schedule(
        db=db,
        schedule_id=schedule_id,
        schedule=schedule,
        user_id=current_user.id,
    )
    if not updated_schedule:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return updated_schedule


@router.delete("/{schedule_id}", summary="Удалить событие")
async def delete_schedule_endpoint(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Удалить событие из расписания.
    """
    success = await delete_schedule(
        db=db, schedule_id=schedule_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return {"message": "Событие успешно удалено"}
