import hashlib
from datetime import datetime, timedelta, timezone
from random import random
from typing import Annotated
from urllib.parse import unquote

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from itsdangerous import BadSignature, SignatureExpired
from sentry_sdk import flush
from sqlmodel import Session, select

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.core.database import get_session
from app.core.security import (
    decode_email_token,
    get_current_user,
    get_verified_user,
    oauth2_scheme,
)
from app.email.model import UserVerificationCode
from app.email.schema import Email, VerifyCodeSchema
from app.email.service import (
    create_message,
    create_user_verification_code,
    generate_verification_code_email,
    mail,
)
from app.users.model import User

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session),
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
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

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
async def send_verification_code(email: str, session: Session = Depends(get_session)):
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
    payload: VerifyCodeSchema, session: Session = Depends(get_session)
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
    if verification_code.expires_at.replace(tzinfo=timezone.utc) < datetime.now(
        timezone.utc
    ):
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
