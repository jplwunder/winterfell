from sqlmodel import SQLModel

class Email(SQLModel):
    addresses: list[str]