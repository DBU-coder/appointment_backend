from pydantic import BaseModel

from app.api.v1.users.schemas import UserBase
from app.common import Role


class PatientInDB(UserBase):
    hashed_pwd: str
    role: Role | None = None


class PatientOut(BaseModel):
    id: int
    user_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
