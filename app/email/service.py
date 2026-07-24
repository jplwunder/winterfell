from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

config = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = os.getenv("MAIL_PORT"),
    MAIL_SERVER = os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
    TEMPLATE_FOLDER=Path(BASE_DIR, "templates")
)

mail = FastMail(config = config)

def create_message(reciepients: list[str], subject: str, body: str):

    message = MessageSchema(
        recipients=reciepients,
        subject=subject,
        body=body,
        subtype="html"
    )
    return message