from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.services.schedule import get_schedule
from app.schemas.shared_schedule import (
    SharedScheduleCreate,
    SharedScheduleUpdate,
    SharedScheduleInDB,
)
from app.schemas.schedule import (
    ScheduleInDB,
)
from app.services.shared_schedule import (
    get_shared_schedule,
    get_shared_schedules_by_owner,
    get_shared_schedules_with_user,
    get_shared_schedules_with_user_with_data,
    create_shared_schedule,
    update_shared_schedule,
    delete_shared_schedule,
)

router = APIRouter()


@router.get(
    "/shared-by-me",
    response_model=List[SharedScheduleInDB],
    summary="Получить события, которыми я поделился",
)
async def read_shared_by_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить список всех событий, которыми поделился текущий пользователь.
    """
    shared_schedules = await get_shared_schedules_by_owner(
        db=db, user_id=current_user.id
    )
    return shared_schedules


@router.get(
    "/shared-with-me",
    response_model=List[SharedScheduleInDB],
    summary="Получить события, которыми поделились со мной",
)
async def read_shared_with_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить список всех событий, которыми поделились с текущим пользователем.
    """
    shared_schedules = await get_shared_schedules_with_user(
        db=db, user_id=current_user.id
    )
    return shared_schedules

@router.get(
    "/shared-with-me-with-data",
    response_model=List[ScheduleInDB],
    summary="Получение всех событий, которыми поделились с пользователем, включая полные данные о самих событиях",
)
async def read_shared_with_me_with_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить список всех событий, которыми поделились с текущим пользователем, с данными.
    """
    shared_schedules = await get_shared_schedules_with_user_with_data(
        db=db, user_id=current_user.id
    )
    return shared_schedules


@router.post(
    "/", response_model=SharedScheduleInDB, summary="Поделиться событием"
)
async def create_shared(
    shared: SharedScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Поделиться событием с другим пользователем.
    Пользователи должны быть друзьями.
    """
    schedule = await get_schedule(
        db=db, schedule_id=shared.schedule_id, user_id=current_user.id
    )
    if not schedule:
        raise HTTPException(
            status_code=404, detail="Событие не найдено или вам не принадлежит"
        )

    result = await create_shared_schedule(
        db=db, shared_schedule=shared, user_id=current_user.id
    )
    if not result:
        raise HTTPException(
            status_code=400,
            detail="Невозможно поделиться событием. Пользователь должен быть вашим другом.",
        )
    return result


@router.get(
    "/{shared_id}",
    response_model=SharedScheduleInDB,
    summary="Получить информацию об общем событии",
)
async def read_shared(
    shared_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить информацию о конкретном общем событии.
    """
    shared_schedule = await get_shared_schedule(
        db=db, shared_id=shared_id, user_id=current_user.id
    )
    if not shared_schedule:
        raise HTTPException(status_code=404, detail="Общее событие не найдено")
    return shared_schedule


@router.put(
    "/{shared_id}",
    response_model=SharedScheduleInDB,
    summary="Изменить права доступа к событию",
)
async def update_shared(
    shared_id: int,
    shared_update: SharedScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить уровень доступа для общего события.
    Доступно только владельцу события.
    """
    updated_shared = await update_shared_schedule(
        db=db,
        shared_id=shared_id,
        shared_update=shared_update,
        user_id=current_user.id,
    )
    if not updated_shared:
        raise HTTPException(
            status_code=404,
            detail="Общее событие не найдено или у вас нет прав на его изменение",
        )
    return updated_shared


@router.delete("/{shared_id}", summary="Отменить общий доступ к событию")
async def remove_shared(
    shared_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Отменить общий доступ к событию.
    Доступно только владельцу события.
    """
    success = await delete_shared_schedule(
        db=db, shared_id=shared_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Общее событие не найдено или у вас нет прав на его удаление",
        )
    return {"message": "Общий доступ к событию успешно отменен"}
