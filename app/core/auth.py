import hashlib
from datetime import UTC, datetime, timedelta
from typing import Annotated
from urllib.parse import unquote

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.core.database import get_session
from app.core.security import (
    get_current_user,
)
from app.core.token import ForgotPasswordRequest, PasswordChangeRequest, ResetPasswordRequest
from app.email.model import UserVerificationCode
from app.email.schema import VerifyCodeSchema
from app.email.service import (
    create_message,
    create_user_verification_code,
    generate_password_reset_email,
    generate_verification_code_email,
    mail,
)
from app.users.model import User

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    statement = select(User).where(User.email == form_data.username)

    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado"
        )

    hashed_password = hashlib.sha256(form_data.password.encode()).hexdigest()

    if user.password != hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Senha incorreta"
        )
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {"sub": str(user.id), "exp": expire}

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
async def me(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
):
    if user.is_verified is False:
        await send_verification_code(user.email, session)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not verified. A verification code has been sent to your email.",
        )
    return {"id": str(user.id), "name": user.name, "email": user.email}


@router.post("/send-verification-code/{email}", status_code=status.HTTP_200_OK)
async def send_verification_code(
    email: str, session: Annotated[Session, Depends(get_session)]
):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    code = create_user_verification_code(user.email, session)
    html_message = generate_verification_code_email(code)
    message = create_message(
        reciepients=[user.email], subject="Código de Verificação", body=html_message
    )
    await mail.send_message(message)
    return {"message": "Verification code sent successfully."}


@router.post("/verify-code", status_code=status.HTTP_200_OK)
async def verify_code(
    payload: VerifyCodeSchema, session: Annotated[Session, Depends(get_session)]
):
    cleaned_email = unquote(payload.email)
    user = session.exec(
        select(User).where(User.email == unquote(cleaned_email))
    ).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    verification_code = session.exec(
        select(UserVerificationCode).where(
            UserVerificationCode.email == cleaned_email
            and UserVerificationCode.code == payload.code
        )
    ).first()
    if not verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code"
        )
    if verification_code.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
        session.delete(verification_code)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Code has expired"
        )
    user.is_verified = True
    session.delete(verification_code)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Code verified successfully."}

def create_password_change_request(user: User, session: Session) -> str:
    # Invalidate any previous unused requests for this user
    session.exec(
        select(PasswordChangeRequest)
        .where(PasswordChangeRequest.user_id == user.id, PasswordChangeRequest.used == False)
    ).all()
    for old in _:
        old.used = True
        session.add(old)

    code = create_user_verification_code(user.email, session)   # random, e.g. 6-digit or urlsafe token depending on your UX
    request = PasswordChangeRequest(
        user_id=user.id,
        code=code,       # store hashed, return raw code to the caller
        expires_at=datetime.now(UTC) + timedelta(minutes=30),
    )
    session.add(request)
    session.commit()
    return code  # raw value goes in the email, hash stays in DB

@router.post("/forgot_password", status_code=status.HTTP_200_OK)
async def forgot_password( payload: ForgotPasswordRequest, session: Annotated[Session, Depends(get_session)]):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if user:
        code = create_password_change_request(user, session)
        html_message = generate_password_reset_email(code)
        message = create_message(
            reciepients=[user.email], subject="Password Reset Request", body=html_message
        )
        await mail.send_message(message)
    return {"message": "If the email exists, a password reset link has been sent."}

@router.post("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(
    payload: ResetPasswordRequest, session: Annotated[Session, Depends(get_session)],
):
    user = session.exec(select(User).where(User.email == payload.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    request = session.exec(
        select(PasswordChangeRequest)
        .where(
            PasswordChangeRequest.user_id == user.id,
            PasswordChangeRequest.code == payload.code,
            PasswordChangeRequest.used == False,
            PasswordChangeRequest.expires_at > datetime.now(UTC),
        )
    ).first()
    if not request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid code"
        )
    if request.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
        request.used = True
        session.add(request)
        session.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Code has expired"
        )
    hashed_password = hashlib.sha256(payload.new_password.encode()).hexdigest()
    user.password = hashed_password
    request.used = True
    session.add(user)
    session.add(request)
    session.commit()
    return {"message": "Password reset successfully."}