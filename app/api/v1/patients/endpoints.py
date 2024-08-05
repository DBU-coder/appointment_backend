from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import text

from app.api.v1.auth.helpers import get_password_hash
from app.api.v1.users import schemas as user_schemas
from app.database import (
    Database,
)
from app.database.dependencies import get_database
from app.exceptions import UserAlreadyExistsException

from . import schemas

router = APIRouter(prefix="/patients", tags=["patients"])


DB_deps = Annotated[Database, Depends(get_database)]


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_patient(
    data: user_schemas.UserCreate,
    db: DB_deps,
):
    existing_user = await db.user.get_by_filter(email=data.email)
    if existing_user:
        raise UserAlreadyExistsException()
    new_data = data.model_dump(exclude={"password"})
    new_data["hashed_pwd"] = get_password_hash(data.password)
    patient = await db.patient.new(schemas.PatientInDB(**new_data))
    return {"patient_id": patient.id}


@router.get("/")
async def patients_list(
    db: DB_deps,
    limit: int | None = None,
):
    patients = await db.patient.get_many(limit)
    return [
        schemas.PatientOut(
            id=patient.id,
            user_id=patient.user_id,
            first_name=patient.user.first_name,
            last_name=patient.user.last_name,
            email=patient.user.email,
            phone=patient.user.phone,
        )
        for patient in patients
    ]
