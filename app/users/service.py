import hashlib
from typing import Dict
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.config import DOMAIN
from app.core.database import get_session
from app.core.roles import EventRole
from app.email.service import create_message, generate_confirmation_email, mail
from app.users.model import User, UserPublic
from app.users.schema import UserCreate, UserList, UserResponse
from app.core.security import generate_email_token, is_valid_email

router = APIRouter(prefix="/users", tags=["users"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    user = User(id=uuid4(), **user.model_dump())
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
    token = generate_email_token({"email": user.email})
    link = f"http://{DOMAIN}/auth/verify?token={token}"

    html_message = generate_confirmation_email(link)

    message = create_message(
        reciepients=[user.email],
        subject="Confirm your email",
        body=html_message
    )
    await mail.send_message(message)
    return {
        "message": "User created successfully. Check your email to confirm your account",
        "user": user
    }

@router.get("/by-email/{email}", response_model=UserPublic, status_code=status.HTTP_200_OK)
def read_user_by_email(email: str, session: Session = Depends(get_session)):
    user = session.exec(
        select(User).where(User.email == email)
    ).one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"email": user.email, "name": user.name, "id": user.id}


@router.get("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
def read_user(user_id: UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return {"email": user.email, "name": user.name, "id": user.id}


@router.delete("/{user_id}", response_model=Dict[str, str], status_code=status.HTTP_200_OK)
def delete_user(user_id: UUID, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}
