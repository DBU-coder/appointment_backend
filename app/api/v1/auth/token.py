import uuid
from datetime import UTC, datetime, timedelta

from jose import jwt

from app.config import settings
from app.database import User

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def encode_jwt(
    payload: dict,
    expire_minutes: int = settings.JWT_ACCESS_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    if expire_timedelta:
        expire = datetime.now(UTC) + expire_timedelta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
        iat=datetime.now(UTC),
        jti=uuid.uuid4().hex,
    )
    return jwt.encode(
        to_encode, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORYTHM
    )


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_minutes: int = settings.JWT_ACCESS_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None,
) -> str:
    payload = {TOKEN_TYPE_FIELD: token_type}
    payload.update(token_data)
    return encode_jwt(payload, expire_minutes, expire_timedelta)


def create_access_token(user: User) -> str:
    payload = {"sub": str(user.id), "email": user.email}
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=payload,
        expire_minutes=settings.JWT_ACCESS_EXPIRE_MINUTES,
    )


def create_refresh_token(user: User) -> str:
    payload = {"sub": str(user.id)}
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=payload,
        expire_timedelta=timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS),
    )
