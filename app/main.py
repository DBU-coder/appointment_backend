from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as v1_router
from app.api.v1.auth.helpers import get_password_hash
from app.api.v1.users.schemas import UserInDB
from app.common import Role
from app.config import settings
from app.database import (
    Database,
    db_connector,
)


async def create_superadmin():
    async with db_connector.session_factory() as session:
        db = Database(session=session)
        superadmin = await db.user.get_superadmin()
        if not superadmin:
            user_data = UserInDB(
                email=settings.SUPERADMIN_EMAIL,
                hashed_pwd=get_password_hash(settings.SUPERADMIN_PASSWORD),
                first_name="Superadmin",
                last_name="Superadmin",
                phone="1234567890",
                role=Role.SUPERADMIN,
            )
            await db.user.new(user_data)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # add your pre-startup operations here
    await create_superadmin()
    yield


app = FastAPI(title="DentistAppointmentAPI", lifespan=lifespan, debug=True)
app.include_router(v1_router, prefix=settings.api_v1_prefix)

origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True, port=8000, host="127.0.0.1")
