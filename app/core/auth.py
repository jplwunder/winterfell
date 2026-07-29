import hashlib
from datetime import datetime, timedelta, timezone
from typing import Annotated

from itsdangerous import BadSignature, SignatureExpired
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sentry_sdk import flush
from sqlmodel import Session, select

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.core.database import get_session
from app.email.schema import Email
from app.users.model import User
from app.core.security import decode_email_token, get_current_user, oauth2_scheme, require_verified_user
from app.email.service import mail, create_message


router = APIRouter(tags=["auth"])

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

@router.post('/send-mail')
async def send_mail(emails: Email):
    emails = emails.addresses

    html = "<h1>Olá,</h1><p>Este é um email de teste.</p>"

    message = create_message(
        reciepients=emails,
        subject="Welcome",
        body=html
    )

    await mail.send_message(message)

    return {"message": "Email sent successfully"}

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