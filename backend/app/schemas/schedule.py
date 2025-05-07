from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
import re


class ScheduleBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название события",
        example="Встреча с клиентом",
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Описание события",
        example="Обсуждение нового проекта",
    )
    start_time: datetime = Field(
        ..., description="Время начала события", example="2024-03-20T10:00:00"
    )
    end_time: datetime = Field(
        ...,
        description="Время окончания события",
        example="2024-03-20T11:00:00",
    )
    is_all_day: bool = Field(
        default=False,
        description="Флаг, указывающий, что событие длится весь день",
        example=False,
    )
    location: Optional[str] = Field(
        None,
        max_length=200,
        description="Место проведения события",
        example="Офис, кабинет 305",
    )
    color: Optional[str] = Field(
        None,
        max_length=7,
        description="Цвет события в формате HEX (например, #FF0000)",
        example="#FF0000",
    )
    is_recurring: bool = Field(
        default=False,
        description="Флаг, указывающий, что событие повторяется",
        example=False,
    )
    recurrence_rule: Optional[str] = Field(
        None,
        max_length=100,
        description="Правило повторения события в формате RRULE (RFC 5545)",
        example="FREQ=WEEKLY;BYDAY=MO,WE,FR",
    )
    category_id: Optional[int] = Field(
        None, description="ID категории события", example=1
    )

    @validator("color")
    def validate_color(cls, v):
        if v is not None:
            if not re.match(r"^#[0-9A-Fa-f]{6}$", v):
                raise ValueError(
                    "Цвет должен быть в формате HEX (например, #FF0000)"
                )
        return v

    @validator("end_time")
    def validate_end_time(cls, v, values):
        if "start_time" in values and v < values["start_time"]:
            raise ValueError(
                "Время окончания должно быть позже времени начала"
            )
        return v

    @validator("recurrence_rule")
    def validate_recurrence_rule(cls, v, values):
        if v is not None and not values.get("is_recurring", False):
            raise ValueError(
                "Правило повторения может быть указано только для повторяющихся событий"
            )
        return v


class ScheduleCreate(ScheduleBase):
    pass


class ScheduleUpdate(ScheduleBase):
    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Название события",
        example="Встреча с клиентом",
    )
    start_time: Optional[datetime] = Field(
        None, description="Время начала события", example="2024-03-20T10:00:00"
    )
    end_time: Optional[datetime] = Field(
        None,
        description="Время окончания события",
        example="2024-03-20T11:00:00",
    )


class ScheduleInDB(ScheduleBase):
    id: int = Field(
        ..., description="Уникальный идентификатор события", example=1
    )
    user_id: int = Field(
        ...,
        description="ID пользователя, которому принадлежит событие",
        example=1,
    )
    created_at: datetime = Field(
        ...,
        description="Дата и время создания события",
        example="2024-03-19T15:30:00",
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Дата и время последнего обновления события",
        example="2024-03-19T16:45:00",
    )

    class Config:
        orm_mode = True


class Schedule(ScheduleInDB):
    pass
