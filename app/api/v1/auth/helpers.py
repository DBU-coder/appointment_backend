from passlib.context import CryptContext

from app.database import User
from app.database.base import Database
from app.exceptions import IncorrectCredentialsException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(db: Database, email: str, password: str) -> User | None:
    user = await db.user.get_by_filter(email=email)
    if not user:
        raise IncorrectCredentialsException()
    is_verified_password = verify_password(password, user.hashed_pwd)
    return user if is_verified_password else None
