from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from app.api.v1.auth.dependencies import (
    PermissionChecker,
    get_current_user,
)
from app.api.v1.auth.helpers import get_password_hash
from app.database import (
    Database,
    Role,
    User,
)
from app.database.dependencies import get_database
from app.exceptions import UserAlreadyExistsException

from . import schemas

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(http_bearer)])


DB_deps = Annotated[Database, Depends(get_database)]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    user_data: schemas.UserCreate,
    db: DB_deps,
    authorize: Annotated[
        bool, Depends(PermissionChecker(required_roles=[Role.ADMIN, Role.SUPERADMIN]))
    ],
):
    existing_user = await db.user.get_by_filter(email=user_data.email)
    if existing_user:
        raise UserAlreadyExistsException()
    new_data = user_data.model_dump(exclude={"password"})
    new_data["hashed_pwd"] = get_password_hash(user_data.password)
    new_user = await db.user.new(schemas.UserInDB(**new_data))
    return {"user_id": new_user.id}


@router.get("/me", response_model=schemas.User)
async def get_me(
    user: Annotated[User, Depends(get_current_user)],
):
    return user
