from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.attendees.router import router as attendees_router
from app.core.database import create_db_and_tables
from app.events.router import router as events_router
from app.routers import auth, misc
from app.users.router import router as users_router


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
app.include_router(users_router)
app.include_router(attendees_router)
app.include_router(events_router)
