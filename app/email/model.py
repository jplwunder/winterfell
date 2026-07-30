from datetime import datetime
from sqlmodel import Field, SQLModel


class UserVerificationCode(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    code: str = Field(index=True)
    expires_at: datetime = Field(index=True)
