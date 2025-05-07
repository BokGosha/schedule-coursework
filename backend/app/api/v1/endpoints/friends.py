from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.friend import (
    FriendCreate,
    FriendUpdate,
    FriendInDB,
    FriendRequestByEmail,
)
from app.services.friend import (
    get_friend,
    get_all_friends,
    create_friend_request,
    create_friend_request_by_email,
    update_friend_status,
    delete_friend,
)
from app.core.logger import logger

router = APIRouter()


@router.get(
    "/", response_model=List[FriendInDB], summary="Получить список друзей"
)
async def read_friends(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = Query(
        None, description="Фильтр по статусу: pending, accepted, rejected"
    ),
):
    """
    Получить список всех друзей текущего пользователя.
    Можно фильтровать по статусу: pending (ожидает), accepted (принято), rejected (отклонено).
    """
    friends = await get_all_friends(
        db=db, user_id=current_user.id, status=status
    )
    return friends


@router.post(
    "/", response_model=FriendInDB, summary="Отправить запрос в друзья"
)
async def create_friend(
    friend: FriendCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Отправить запрос на добавление в друзья.
    """
    if friend.friend_id == current_user.id:
        raise HTTPException(
            status_code=400, detail="Нельзя добавить себя в друзья"
        )

    from app.services.user import get_user

    target_user = await get_user(db=db, user_id=friend.friend_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return await create_friend_request(
        db=db, friend=friend, user_id=current_user.id
    )


@router.post(
    "/by-email",
    response_model=FriendInDB,
    summary="Отправить запрос в друзья по email",
)
async def create_friend_by_email(
    friend_request: FriendRequestByEmail,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Отправить запрос на добавление в друзья по email.

    Данный метод позволяет отправить запрос дружбы, указав email пользователя
    вместо его ID. Это удобно, когда вы знаете email друга, но не знаете его ID.

    - **email**: Email пользователя, которого нужно добавить в друзья

    При успешном выполнении возвращает созданный запрос дружбы со статусом "pending".
    """
    logger.info(f"Запрос на добавление друга по email: {friend_request.email}")

    if friend_request.email == current_user.email:
        raise HTTPException(
            status_code=400, detail="Нельзя добавить себя в друзья"
        )

    friend_relation = await create_friend_request_by_email(
        db=db, email=friend_request.email, user_id=current_user.id
    )

    if not friend_relation:
        raise HTTPException(
            status_code=404, detail="Пользователь с указанным email не найден"
        )

    return friend_relation


@router.get(
    "/{friend_id}",
    response_model=FriendInDB,
    summary="Получить информацию о друге",
)
async def read_friend(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить информацию о конкретном друге.
    """
    friend = await get_friend(
        db=db, friend_relation_id=friend_id, user_id=current_user.id
    )
    if not friend:
        raise HTTPException(status_code=404, detail="Друг не найден")
    return friend


@router.put(
    "/{friend_id}",
    response_model=FriendInDB,
    summary="Ответить на запрос дружбы",
)
async def update_friend(
    friend_id: int,
    friend_update: FriendUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить статус дружбы (принять или отклонить запрос).

    Данный метод позволяет изменить статус отношения дружбы:
    - Принять запрос дружбы (status = "accepted")
    - Отклонить запрос дружбы (status = "rejected")

    **Важно:** Этот метод доступен только получателю запроса.
    Отправитель запроса не может изменить его статус.

    Параметры:
    - **friend_id**: ID записи о дружбе (не ID пользователя-друга)
    - **friend_update**: Объект с новым статусом дружбы

    Пример запроса для принятия дружбы:
    ```json
    {
        "status": "accepted"
    }
    ```

    Пример запроса для отклонения дружбы:
    ```json
    {
        "status": "rejected"
    }
    ```
    """
    updated_friend = await update_friend_status(
        db=db,
        friend_relation_id=friend_id,
        friend_update=friend_update,
        user_id=current_user.id,
    )
    if not updated_friend:
        raise HTTPException(
            status_code=404,
            detail="Друг не найден или у вас нет прав на изменение статуса",
        )
    return updated_friend


@router.delete("/{friend_id}", summary="Удалить из друзей")
async def remove_friend(
    friend_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Удалить друга.
    """
    success = await delete_friend(
        db=db, friend_relation_id=friend_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Друг не найден")
    return {"message": "Друг успешно удален"}
