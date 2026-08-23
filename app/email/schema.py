from pydantic import EmailStr
from sqlmodel import SQLModel


class Email(SQLModel):
    addresses: list[str]


class VerifyCodeSchema(SQLModel):
    email: EmailStr
    code: str
