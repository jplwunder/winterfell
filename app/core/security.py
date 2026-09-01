import secrets
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import URLSafeTimedSerializer
from sqlmodel import Session, select

from app.attendees.model import Ticket
from app.core.config import ALGORITHM, SECRET_KEY
from app.core.database import get_session
from app.core.roles import EventRole
from app.users.model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
email_salt = "email-confirmation"

serializer = URLSafeTimedSerializer(SECRET_KEY)


def get_current_user(
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        user_id = UUID(user_id)

        user = session.exec(select(User).where(User.id == user_id)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def get_event_id_from_ticket_code(
    ticket_code: str, session: Annotated[Session, Depends(get_session)]
) -> UUID:
    ticket = session.exec(
        select(Ticket).where(Ticket.ticket_code == ticket_code)
    ).one_or_none()

    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )

    return ticket.event_id

def get_verified_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not verified, Check your email for verification link",
        )
    return current_user


def require_role(*allowed_roles: EventRole):
    def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
        event_id: Annotated[UUID, Depends(get_event_id_from_ticket_code)],
    ) -> User:
        if current_user.get_role(event_id) not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker


def require_event_role(*allowed_roles: EventRole):
    def role_checker(
        event_id: UUID,
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.get_role(event_id) not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker


def generate_ticket_code() -> str:
    return secrets.token_urlsafe(16)


def is_valid_email(email: str) -> bool:
    if not email:
        return False
    return (
        email.count("@") == 1
        and email.count(".") >= 1
        and email.find("@.") == -1
        and email.find(".@") == -1
    )


def generate_email_token(data: dict) -> str:
    email_token = serializer.dumps(data, salt=email_salt)
    return email_token


def decode_email_token(email_token: str, max_age: int = 3600) -> dict:
    return serializer.loads(email_token, salt=email_salt, max_age=max_age)
