from app.api.v1.users.schemas import UserBase
from app.common import Role


class PatientInDB(UserBase):
    hashed_pwd: str
    role: Role | None = None
