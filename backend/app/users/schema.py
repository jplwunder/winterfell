from app.schemas import UserCreate, UserList, UserResponse
from backend.app.users.model import User
from sqlmodel import SQLModel
from typing import List

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