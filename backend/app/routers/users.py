import hashlib
from typing import Dict
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.database import SessionDep
from app.models import EventMembership, EventRole, User
from app.schemas import UserCreate, UserResponse, UserList
from app.security import is_valid_email

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: SessionDep):
    user = User(id=uuid4(), role=EventRole.user, **user.model_dump())
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest() if user.password else None
    user.password = hashed_password
    if is_valid_email(user.email):
        existing_user = session.exec(select(User).where(User.email == user.email)).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {
        "message": "User created successfully",
        "user": user
    }


@router.get("/{event_id}", response_model=UserList, status_code=status.HTTP_200_OK)
def list_users(event_id: UUID, session: SessionDep):
    users = session.exec(select(User).where(User.role == EventRole.user and EventMembership.user_id == User.id and EventMembership.event_id == event_id)).all()
    return UserList(users=users)


@router.get("/{user_id}", response_model=User, status_code=status.HTTP_200_OK)
def read_user(user_id: UUID, session: SessionDep):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def delete_user(user_id: UUID, session: SessionDep):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}
