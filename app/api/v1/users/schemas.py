from re import compile

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.database import Role


class UserBase(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    first_name: str
    last_name: str
    email: EmailStr
    phone: str


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        pattern = compile(
            r"^(?=.*[0-9])(?=.*[!@#$%^&*])(?=.*[a-z])(?=.*[A-Z])[0-9a-zA-Z!@#$%^&*]{8,}$"
        )
        if not pattern.match(password):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, one digit, "
                "one special character, and be at least 8 characters long."
            )
        return password


class UserInDB(UserBase):
    hashed_pwd: str
    role: Role | None = None


class User(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
