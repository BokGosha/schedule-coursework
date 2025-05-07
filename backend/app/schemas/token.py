from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(..., description="Тип токена", example="bearer")
