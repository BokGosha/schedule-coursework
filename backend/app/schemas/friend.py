from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class FriendBase(BaseModel):
    friend_id: int = Field(
        ..., description="ID пользователя, которого добавляют в друзья"
    )
    status: str = Field(
        default="pending",
        description="Статус дружбы: pending (ожидает подтверждения), accepted (принято), rejected (отклонено)",
        example="pending",
    )


class FriendCreate(FriendBase):
    pass


class FriendRequestByEmail(BaseModel):
    email: EmailStr = Field(
        ...,
        description="Email пользователя, которого нужно добавить в друзья",
        example="friend@example.com",
    )


class FriendUpdate(BaseModel):
    status: str = Field(
        ...,
        description="Новый статус дружбы: accepted (принять) или rejected (отклонить)",
        example="accepted",
    )


class FriendInDB(FriendBase):
    id: int = Field(
        ..., description="Уникальный идентификатор записи о дружбе"
    )
    user_id: int = Field(
        ..., description="ID пользователя, который добавил в друзья"
    )
    created_at: datetime = Field(
        ..., description="Дата и время создания записи"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Дата и время последнего обновления"
    )

    class Config:
        orm_mode = True


class Friend(FriendInDB):
    pass
