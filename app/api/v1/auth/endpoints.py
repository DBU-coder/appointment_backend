from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from starlette.responses import Response

from app.api.v1.auth.dependencies import get_current_user, get_current_user_for_refresh
from app.api.v1.auth.helpers import authenticate_user
from app.api.v1.auth.token import create_access_token, create_refresh_token
from app.database import Database, User
from app.database.dependencies import get_database
from app.exceptions import IncorrectCredentialsException

from . import schemas

http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(http_bearer)])

DB_deps = Annotated[Database, Depends(get_database)]


@router.post("/login", response_model=schemas.TokenInfo)
async def login(
    response: Response,
    credentials: schemas.UserLogin,
    db: DB_deps,
):
    user = await authenticate_user(
        db,
        email=credentials.email,
        password=credentials.password,
    )
    access_token = create_access_token(user)  # type: ignore
    refresh_token = create_refresh_token(user)  # type: ignore
    response.headers["Authorization"] = f"Bearer {access_token}"
    response.set_cookie("refresh_token", refresh_token, httponly=True)

    return schemas.TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/refresh",
    response_model=schemas.TokenInfo,
    response_model_exclude_none=True,
)
async def refresh_access_token(
    user: Annotated[User, Depends(get_current_user_for_refresh)],
):
    access_token = create_access_token(user)
    return schemas.TokenInfo(
        access_token=access_token,
    )


@router.get("/logout")
async def logout(
    response: Response,
    user: Annotated[User, Depends(get_current_user)],
):
    if not user:
        raise IncorrectCredentialsException()
    response.delete_cookie("refresh_token")
    del response.headers["Authorization"]
    return {"message": "Successfully logged out."}
