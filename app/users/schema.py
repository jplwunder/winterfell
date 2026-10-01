from sqlmodel import SQLModel

from app.users.model import User, UserPublic


class UserCreate(SQLModel):
    name: str
    email: str
    password: str | None = None


class UserList(SQLModel):
    users: list[User]


class UserResponse(SQLModel):
    message: str
    user: UserPublic
