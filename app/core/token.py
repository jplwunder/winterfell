from datetime import datetime, UTC
from uuid import UUID, uuid4
from pydantic import AliasChoices, EmailStr
from sqlmodel import Field, SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None


class PasswordChangeRequest(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    code: int = Field(index=True)          # the code sent to the user
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime
    used: bool = Field(default=False)

    class ConfigDict:
        arbitrary_types_allowed = True

class ForgotPasswordRequest(SQLModel):
    email: EmailStr = Field(index=True)

class ResetPasswordRequest(SQLModel):
    email: EmailStr = Field(index=True)
    code: int = Field(validation_alias=AliasChoices("code", "token"))
    new_password: str = Field(
        validation_alias=AliasChoices("new_password", "newPassword")
    )