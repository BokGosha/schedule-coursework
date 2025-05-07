from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserInDB, UserBasicInfo
from app.services.user import (
    get_user,
    get_users,
    create_user,
    update_user,
    delete_user,
    get_user_by_email,
)
from app.core.logger import logger

router = APIRouter()


@router.get(
    "/", response_model=List[UserInDB], summary="Получить список пользователей"
)
async def read_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
):
    """
    Получить список всех пользователей.
    """
    users = await get_users(db=db, skip=skip, limit=limit)
    return users


@router.post(
    "/", response_model=UserInDB, summary="Создать нового пользователя"
)
async def create_user_endpoint(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Создать нового пользователя.
    """
    return await create_user(db=db, user=user)


@router.get(
    "/me", response_model=UserInDB, summary="Получить информацию о себе"
)
async def read_user_me(
    current_user: User = Depends(get_current_user),
):
    """
    Получить информацию о текущем пользователе.
    """
    return current_user


@router.get(
    "/by-email",
    response_model=UserBasicInfo,
    summary="Найти пользователя по email",
)
async def find_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Найти пользователя по email адресу.

    Этот метод позволяет найти пользователя, указав его email адрес.
    Результат содержит только базовую информацию: id, username и email.

    Параметры:
    - **email**: Email пользователя для поиска (например, user@example.com)

    Возвращает объект с информацией о найденном пользователе или ошибку 404,
    если пользователь с указанным email не найден.

    Пример ответа:
    ```json
    {
        "id": 123,
        "username": "johndoe",
        "email": "user@example.com"
    }
    ```
    """
    logger.info(f"Поиск пользователя по email: {email}")

    user = await get_user_by_email(db=db, email=email)
    if not user:
        raise HTTPException(
            status_code=404, detail="Пользователь с указанным email не найден"
        )

    logger.info(f"Пользователь найден: ID={user.id}, username={user.username}")
    return user


@router.get(
    "/{user_id}",
    response_model=UserInDB,
    summary="Получить информацию о пользователе",
)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить информацию о конкретном пользователе по ID.
    """
    user = await get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.put("/me", response_model=UserInDB, summary="Обновить свои данные")
async def update_user_me(
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить данные текущего пользователя.
    """
    return await update_user(db=db, user_id=current_user.id, user=user)


@router.put(
    "/{user_id}", response_model=UserInDB, summary="Обновить пользователя"
)
async def update_user_endpoint(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить данные пользователя по ID.
    """
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для выполнения операции"
        )

    updated_user = await update_user(db=db, user_id=user_id, user=user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return updated_user


@router.delete("/{user_id}", summary="Удалить пользователя")
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Удалить пользователя по ID.
    """
    if current_user.id != user_id and not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Недостаточно прав для выполнения операции"
        )

    success = await delete_user(db=db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return {"message": "Пользователь успешно удален"}
