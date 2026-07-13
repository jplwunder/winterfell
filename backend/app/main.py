from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import create_db_and_tables
from app.core.auth import router as auth_router
from app.core.misc import router as misc_router
from app.attendees.service import router as attendees_router
from app.events.service import router as events_router
from app.users.service import router as users_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(misc_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(attendees_router)
app.include_router(events_router)
