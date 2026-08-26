import hashlib
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import (
    get_current_user,
    get_verified_user,
    is_valid_email,
)
from app.email.service import (
    create_message,
    create_user_verification_code,
    generate_verification_code_email,
    mail,
)
from app.users.model import User, UserPublic
from app.users.schema import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_payload: UserCreate, session: Annotated[Session, Depends(get_session)]
):
    user = User(id=uuid4(), **user_payload.model_dump(exclude={"password"}))

    hashed_password = (
        hashlib.sha256(user_payload.password.encode()).hexdigest()
        if user_payload.password
        else None
    )
    user.password = hashed_password

    if is_valid_email(user.email):
        existing_user = session.exec(
            select(User).where(User.email == user.email)
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email já registrado."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Formato de e-mail inválido"
        )

    code = create_user_verification_code(user.email, session)
    html_message = generate_verification_code_email(code)
    message = create_message(
        reciepients=[user.email],
        subject="[Dois ou Mais] Verifique o seu endereço de e-mail",
        body=html_message,
    )
    await mail.send_message(message)

    session.add(user)
    session.commit()

    return {
        "message": "User created successfully. Waiting for e-mail confirmation.",
        "user": user,
    }


@router.get(
    "/by-email/{email}",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
)
def read_user_by_email(
    email: str,
    session: Annotated[Session, Depends(get_session)],
    require_verified: Annotated[User, Depends(get_verified_user)],
):
    user = session.exec(select(User).where(User.email == email)).one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"email": user.email, "name": user.name, "id": user.id}


@router.get("/{user_id}", response_model=UserPublic, status_code=status.HTTP_200_OK)
def read_user(user_id: UUID, session: Session = Depends(get_session), current_user: User = Depends(get_current_user), require_verified: User = Depends(get_verified_user)):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return {"email": user.email, "name": user.name, "id": user.id}

@router.delete(
    "/{user_id}", response_model=dict[str, str], status_code=status.HTTP_200_OK
)
def delete_user(
    user_id: UUID,
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    require_verified: Annotated[User, Depends(get_verified_user)],
):
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}
