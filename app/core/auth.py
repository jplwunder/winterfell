import hashlib
from datetime import datetime, timedelta, timezone
from random import random
from typing import Annotated
from urllib.parse import unquote

from itsdangerous import BadSignature, SignatureExpired
import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sentry_sdk import flush
from sqlmodel import Session, select

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.core.database import get_session
from app.email.schema import Email, VerifyCodeSchema
from app.users.model import User
from app.core.security import decode_email_token, get_current_user, oauth2_scheme, require_verified_user
from app.email.service import generate_verification_code_email, mail, create_message, create_user_verification_code
from app.email.model import UserVerificationCode

router = APIRouter(tags=["auth"], prefix="/auth")

@router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    statement = select(User).where(
        User.email == form_data.username and User.is_verified == True
    )

    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )

    hashed_password = hashlib.sha256(
        form_data.password.encode()
    ).hexdigest()

    if user.password != hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha incorreta"
        )
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(user.id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get("/me")
async def me(user=Depends(get_current_user), require_verified: User = Depends(require_verified_user)):
    return {"id": str(user.id), "name": user.name, "email": user.email}

@router.get("/verify")
@router.get("/verify/")
async def verify_email(token: str, session: Session = Depends(get_session)):
    try:
        payload = decode_email_token(token)
        email = payload.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )

        user = session.exec(select(User).where(User.email == email)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.is_verified:
            return {"message": "Email already verified"}

        user.is_verified = True
        session.add(user)
        session.commit()
        session.refresh(user)

        return {"message": "Email verified successfully"}

    except SignatureExpired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token has expired"
        )
    except BadSignature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

@router.post("/send-verification-code/{email}", status_code=status.HTTP_200_OK)
async def send_verification_code(email: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    code = create_user_verification_code(user.email, session)
    html_message = generate_verification_code_email(code)
    message = create_message(
        reciepients=[user.email],
        subject="Código de Verificação",
        body=html_message
    )
    await mail.send_message(message)
    return {"message": "Verification code sent successfully."}

@router.post("/verify-code", status_code=status.HTTP_200_OK)
async def verify_code(payload: VerifyCodeSchema, session: Session = Depends(get_session)):
    cleaned_email = unquote(payload.email)
    user = session.exec(select(User).where(User.email == unquote(cleaned_email))).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    verification_code = session.exec(select(UserVerificationCode).where(UserVerificationCode.email == cleaned_email and UserVerificationCode.code == payload.code)).first()
    if not verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid code"
        )
    expires_at = verification_code.expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code has expired"
        )
    user.is_verified = True
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Code verified successfully."}
