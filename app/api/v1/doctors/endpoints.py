from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer

from app.api.v1.auth.dependencies import (
    PermissionChecker,
)
from app.api.v1.auth.helpers import get_password_hash
from app.api.v1.users import schemas as user_schemas
from app.database import (
    Database,
    Role,
)
from app.database.dependencies import get_database
from app.exceptions import UserAlreadyExistsException

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix="/doctors", tags=["doctors"], dependencies=[Depends(http_bearer)]
)


DB_deps = Annotated[Database, Depends(get_database)]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: user_schemas.UserCreate,
    db: DB_deps,
    authorize: Annotated[
        bool, Depends(PermissionChecker(required_roles=[Role.ADMIN, Role.SUPERADMIN]))
    ],
):
    existing_user = await db.user.get_by_filter(email=data.email)
    if existing_user:
        raise UserAlreadyExistsException()
    new_data = data.model_dump(exclude={"password"})
    new_data["hashed_pwd"] = get_password_hash(data.password)
    new_user = await db.user.new(user_schemas.UserInDB(**new_data))
    return {"user_id": new_user.id}
