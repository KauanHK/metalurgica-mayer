from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.actors.roles import UserRole

Name = Annotated[str, Field(min_length=2, max_length=150)]
Phone = Annotated[str, Field(max_length=20)]
NewPassword = Annotated[str, Field(min_length=8, max_length=72)]


def _blank_to_none(value: str | None) -> str | None:
    """Trata string vazia como ausência, como em `clients`."""

    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class LoginRequest(BaseModel):
    """Corpo do `POST /auth/login`."""

    email: EmailStr
    password: Annotated[str, Field(min_length=1)]

    @field_validator("email", mode="after")
    @classmethod
    def _normalize_email(cls, value: str) -> str:
        return value.lower()


class RefreshRequest(BaseModel):
    """Corpo do `POST /auth/refresh`."""

    refresh_token: Annotated[str, Field(min_length=1)]


class UserRead(BaseModel):
    """Usuário como a API o devolve — nunca inclui o hash da senha."""

    id: UUID
    name: str
    email: str
    phone: str | None
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    """Corpo devolvido por um login bem-sucedido."""

    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserRead


class AccessTokenResponse(BaseModel):
    """Corpo devolvido por `POST /auth/refresh`."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class ProfileUpdate(BaseModel):
    """Corpo do `PATCH /users/me`. Campo ausente não é tocado."""

    name: Name | None = None
    phone: Phone | None = None

    @field_validator("phone", mode="before")
    @classmethod
    def _empty_phone_to_none(cls, value: str | None) -> str | None:
        return _blank_to_none(value)


class PasswordChange(BaseModel):
    """Corpo do `POST /users/me/password`."""

    current_password: Annotated[str, Field(min_length=1)]
    new_password: NewPassword
