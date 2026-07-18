from typing import List

from sqlmodel import SQLModel

from app.users.model import User


class UserCreate(SQLModel):
    name: str
    age: int | None = None
    email: str | None = None
    password: str | None = None


class UserList(SQLModel):
    users: List[User]


class UserResponse(SQLModel):
    message: str
    user: User