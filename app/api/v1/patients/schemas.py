

from app.api.v1.users.schemas import UserBase
from app.database import Role


class PatientInDB(UserBase):
    hashed_pwd: str
    role: Role | None = None
