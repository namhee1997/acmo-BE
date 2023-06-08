# from app.shared.utils.general import ExtendedEnum
from enum import Enum

class UserStatus(Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    DELETED = 'deleted'

class AuthGrantType(Enum):
    RESET_PASSWORD = 'reset_password'
    VERIFY_CODE = 'verify_code'
    ACCESS_TOKEN = 'access_token'