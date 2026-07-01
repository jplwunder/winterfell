from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import attendees, auth, misc, users, events


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True}
)

app.include_router(misc.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(attendees.router)
app.include_router(events.router)
