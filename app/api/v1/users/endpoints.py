from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.api.v1.auth.dependencies import get_current_user
from app.database import User

from . import schemas

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(http_bearer)])


@router.get("/me", response_model=schemas.User)
async def get_me(
    user: Annotated[User, Depends(get_current_user)],
):
    return user
