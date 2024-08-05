from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends, Request
from jose import JWTError, jwt

from app.api.v1.auth.token import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    TOKEN_TYPE_FIELD,
)
from app.common import Role
from app.config import settings
from app.database import (
    Database,
    User,
)
from app.database.dependencies import get_database
from app.exceptions import (
    ExpiredTokenException,
    IncorrectCredentialsException,
    InvalidTokenException,
    InvalidTokenTypeException,
    NoPermissionsException,
)


def get_token(request: Request) -> str:
    token = request.headers.get("Authorization")
    if not token:
        raise InvalidTokenException()
    return token.removeprefix("Bearer ")


def get_token_payload(token: Annotated[str, Depends(get_token)]) -> dict:
    print("get_token_payload")
    try:
        payload = jwt.decode(
            token,
            key=settings.JWT_SECRET_KEY,
            algorithms=settings.JWT_ALGORYTHM,
        )
    except JWTError as err:
        raise InvalidTokenException() from err
    return payload


def validate_token_type(payload: dict, token_type: str) -> bool:
    current_type = payload.get(TOKEN_TYPE_FIELD)
    if current_type == token_type:
        return True
    exception = InvalidTokenTypeException()
    exception.detail = (
        f"Invalid token type. Expected {token_type!r}, got {current_type!r}."
    )
    raise exception


def token_is_expired(payload: dict) -> bool:
    expire = payload.get("exp")
    if (expire is None) or (datetime.now(UTC) > datetime.fromtimestamp(expire, UTC)):
        raise ExpiredTokenException()
    return False


async def get_user_from_token_sub(
    payload: dict,
    db: Annotated[Database, Depends(get_database)],
) -> User:
    print("get_user_from_token_sub")
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenException()
    if user := await db.user.get(int(user_id)):
        return user
    raise IncorrectCredentialsException()


class UserGetterFromToken:

    def __init__(self, token_type: str):
        self.token_type = token_type

    async def __call__(
        self,
        db: Annotated[Database, Depends(get_database)],
        payload: Annotated[dict, Depends(get_token_payload)],
    ):
        validate_token_type(payload, self.token_type)
        token_is_expired(payload)
        user = await get_user_from_token_sub(payload, db)
        return user


class PermissionChecker:

    def __init__(self, required_roles: list[Role]):
        self.required_roles = required_roles

    def __call__(
        self,
        user: Annotated[User, Depends(UserGetterFromToken(ACCESS_TOKEN_TYPE))],
    ) -> bool:
        if user.role not in self.required_roles:
            raise NoPermissionsException()
        return True


get_current_user = UserGetterFromToken(ACCESS_TOKEN_TYPE)
get_current_user_for_refresh = UserGetterFromToken(REFRESH_TOKEN_TYPE)
