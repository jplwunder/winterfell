from fastapi import APIRouter
from sqlmodel import Session, text

from app.database import engine

router = APIRouter(tags=["misc"])


@router.get("/")
def hello_world():
    return {"message": "Hello World"}


@router.get("/db-check")
async def db_check():
    with Session(engine) as session:
        result = session.exec(text("SELECT 1")).scalar_one()
        return {"database_connected": True, "result": result}
