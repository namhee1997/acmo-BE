from pydantic import EmailStr, constr, validator, BaseModel, BaseConfig
from typing import Optional
from datetime import datetime, timezone
from app.domain.field import PydanticObjectId


class BaseEntity(BaseModel):
    class Config(BaseConfig):
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda dt: dt.replace(tzinfo=timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        }


class AuthInfo(BaseEntity):
    password: constr(min_length=8)


class UserInLogin(AuthInfo):
    username: EmailStr


class UserInRegister(AuthInfo):
    email: EmailStr
    fullname: str
    date_of_birth: str
    phone_number: str
    address: str
    role: str = None


class UserInChange(BaseEntity):
    email: EmailStr
    fullname: str
    date_of_birth: str
    phone_number: str
    address: str
    id: str
    role: str = None

class IDModelMixin(BaseModel):
    id: Optional[PydanticObjectId]


class UserBase:
    email: EmailStr
    phone_number: Optional[str] = None
    address: Optional[str] = None
    # default user status to inactive
    username: Optional[str] = None
    date_of_birth: str
    fullname: Optional[str] = None


class DateTimeModelMixin(BaseModel):
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]

    @validator("createdAt", "updatedAt", pre=True, always=True)
    def set_datetime_now(cls, value: datetime) -> datetime:
        return value or datetime.utcnow()

class UserMe(DateTimeModelMixin):
    id: int
    email: EmailStr
    phone_number: Optional[str]
    address: Optional[str]
    # default user status to inactive
    role: Optional[bool] = None
    date_of_birth: str
    fullname: Optional[str]

class UserInDB(IDModelMixin, DateTimeModelMixin, UserBase):
    hashed_password: Optional[str]
    role: Optional[str]
    reset_password_at: Optional[datetime]
    code: Optional[int]

    class Config:
        # orm mode to create model from db orm class instaces
        # https://pydantic-docs.helpmanual.io/usage/models/#orm-mode-aka-arbitrary-class-instances
        orm_mode = True
