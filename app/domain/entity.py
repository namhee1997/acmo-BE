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
    first_name: str
    last_name: str


class IDModelMixin(BaseModel):
    id: Optional[PydanticObjectId]


class UserBase:
    email: EmailStr
    phone_number: Optional[str] = None
    address: Optional[str] = None
    is_admin: Optional[bool] = None
    # default user status to inactive
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    confirmed: Optional[bool] = False
    balance: Optional[float] = 0


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @validator("created_at", "updated_at", pre=True, always=True)
    def set_datetime_now(cls, value: datetime) -> datetime:
        return value or datetime.utcnow()


class UserInDB(IDModelMixin, DateTimeModelMixin, UserBase):
    hashed_password: Optional[str]
    reset_password_at: Optional[datetime]
    code: Optional[int]

    class Config:
        # orm mode to create model from db orm class instaces
        # https://pydantic-docs.helpmanual.io/usage/models/#orm-mode-aka-arbitrary-class-instances
        orm_mode = True
