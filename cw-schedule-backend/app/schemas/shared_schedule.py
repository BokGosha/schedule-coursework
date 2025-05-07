from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SharedScheduleBase(BaseModel):
    schedule_id: int = Field(..., description="ID события, которым делятся")
    shared_with_id: int = Field(
        ..., description="ID пользователя, с которым делятся событием"
    )
    permission_level: str = Field(
        default="view",
        description="Уровень доступа: view (только просмотр), edit (редактирование)",
        example="view",
    )


class SharedScheduleCreate(SharedScheduleBase):
    pass


class SharedScheduleUpdate(BaseModel):
    permission_level: str = Field(
        ...,
        description="Новый уровень доступа: view (только просмотр) или edit (редактирование)",
        example="edit",
    )


class SharedScheduleInDB(SharedScheduleBase):
    id: int = Field(
        ..., description="Уникальный идентификатор записи о совместном доступе"
    )
    user_id: int = Field(
        ..., description="ID пользователя, который поделился событием"
    )
    created_at: datetime = Field(
        ..., description="Дата и время создания записи"
    )
    updated_at: Optional[datetime] = Field(
        None, description="Дата и время последнего обновления"
    )

    class Config:
        orm_mode = True


class SharedSchedule(SharedScheduleInDB):
    pass
