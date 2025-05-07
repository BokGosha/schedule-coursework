from pydantic import BaseModel, EmailStr, constr, Field, validator
from typing import Optional
from datetime import datetime
from app.core.config import get_settings
import re

settings = get_settings()


class UserBase(BaseModel):
    email: EmailStr = Field(
        ..., description="Email пользователя", example="user@example.com"
    )
    username: constr(
        min_length=settings.USERNAME_MIN_LENGTH,
        max_length=settings.USERNAME_MAX_LENGTH,
    ) = Field(
        ...,
        description="Имя пользователя",
        example="johndoe",
        min_length=settings.USERNAME_MIN_LENGTH,
        max_length=settings.USERNAME_MAX_LENGTH,
    )
    is_active: bool = Field(
        default=True, description="Активен ли пользователь"
    )
    is_superuser: bool = Field(
        default=False, description="Является ли пользователь администратором"
    )


class UserBasicInfo(BaseModel):
    id: int = Field(..., description="ID пользователя", example=1)
    username: str = Field(
        ..., description="Имя пользователя", example="johndoe"
    )
    email: EmailStr = Field(
        ..., description="Email пользователя", example="user@example.com"
    )

    model_config = {"from_attributes": True}


class UserCreate(UserBase):
    password: constr(min_length=settings.PASSWORD_MIN_LENGTH) = Field(
        ...,
        description="Пароль пользователя",
        example="strongpassword123",
        min_length=settings.PASSWORD_MIN_LENGTH,
    )

    @validator("username")
    def username_alphanumeric(cls, v):
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Имя пользователя должно содержать только буквы, цифры, знаки подчеркивания и дефисы"
            )
        return v

    @validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен содержать не менее 8 символов")
        if not re.search(r"[A-Z]", v):
            raise ValueError(
                "Пароль должен содержать хотя бы одну заглавную букву"
            )
        if not re.search(r"[a-z]", v):
            raise ValueError(
                "Пароль должен содержать хотя бы одну строчную букву"
            )
        if not re.search(r"[0-9]", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class UserUpdate(BaseModel):
    email: EmailStr | None = Field(
        None,
        description="Новый email пользователя",
        example="newemail@example.com",
    )
    username: (
        constr(
            min_length=settings.USERNAME_MIN_LENGTH,
            max_length=settings.USERNAME_MAX_LENGTH,
        )
        | None
    ) = Field(
        None,
        description="Новое имя пользователя",
        example="newusername",
        min_length=settings.USERNAME_MIN_LENGTH,
        max_length=settings.USERNAME_MAX_LENGTH,
    )
    password: constr(min_length=settings.PASSWORD_MIN_LENGTH) | None = Field(
        None,
        description="Новый пароль пользователя",
        example="newstrongpassword123",
        min_length=settings.PASSWORD_MIN_LENGTH,
    )
    is_active: bool | None = Field(
        None, description="Новый статус активности", example=True
    )

    @validator("username")
    def username_alphanumeric(cls, v):
        if v is not None and not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "Имя пользователя должно содержать только буквы, цифры, знаки подчеркивания и дефисы"
            )
        return v

    @validator("password")
    def password_strength(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError("Пароль должен содержать не менее 8 символов")
            if not re.search(r"[A-Z]", v):
                raise ValueError(
                    "Пароль должен содержать хотя бы одну заглавную букву"
                )
            if not re.search(r"[a-z]", v):
                raise ValueError(
                    "Пароль должен содержать хотя бы одну строчную букву"
                )
            if not re.search(r"[0-9]", v):
                raise ValueError("Пароль должен содержать хотя бы одну цифру")
        return v


class UserInDB(UserBase):
    id: int = Field(..., description="ID пользователя", example=1)
    created_at: datetime = Field(
        ...,
        description="Дата создания пользователя",
        example="2024-01-01T00:00:00",
    )
    updated_at: datetime | None = Field(
        None,
        description="Дата последнего обновления",
        example="2024-01-01T00:00:00",
    )

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    class Config:
        from_attributes = True
