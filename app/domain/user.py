from typing import Optional
from pydantic import EmailStr, validator, BaseModel

def transform_email(email: str) -> str:
    return email.lower()


class UserInCreate(BaseModel):
    email: EmailStr
    fullname: str
    hashed_password: str
    address: str
    phone_number: str
    date_of_birth: str
    code: Optional[int]

    _extract_email = validator('email', pre=True, allow_reuse=True)(transform_email)

class PersonalInUpdate(BaseModel):
    email: EmailStr
    fullname: str
    address: str
    phone_number: str
    date_of_birth: str
    code: Optional[int] = None
    token: Optional[str] = None

    