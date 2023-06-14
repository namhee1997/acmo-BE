from typing import Optional, Union, List
from pydantic import BaseModel
from app.domain.enum import AuthGrantType
from passlib.context import CryptContext
from app.config import config
from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import Depends, HTTPException, status, Security
from jwt import PyJWTError, ExpiredSignatureError
from app.domain.entity import UserInDB
from datetime import datetime, timedelta
from app.infa.user.user_repository import UserRepository

class Token(BaseModel):
    access_token: Optional[str] = None
    token_type: str = 'bearer'
    verify_token: Optional[str] = None

class TokenData(BaseModel):
    email: str = None
    grant_type: Optional[AuthGrantType] = AuthGrantType.ACCESS_TOKEN
    id: str = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config['API_V1_STR']}/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def verify_token(token: str, grant_type: Optional[AuthGrantType] = None) -> Optional[TokenData]:
    try:
        # decode jwt token
        if token.startswith("Bearer "):
            token = token.split("Bearer ")[1]
        payload = jwt.decode(token, config['SECRET_KEY'], algorithms=[config['ALGORITHM']])
        # get email from decoded token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, id=payload.get('id'), grant_type=payload.get('grant_type'))
        if grant_type and grant_type != token_data.grant_type:
            raise Exception('Invalid Token')
        return token_data
    except ExpiredSignatureError:
        raise Exception('Token Expired')
    except PyJWTError:
        raise Exception('Could not validate credentials')
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def _get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(UserRepository)
) -> UserInDB:
    try:
        # decode jwt token
        payload = jwt.decode(token, config['SECRET_KEY'], algorithms=[config['ALGORITHM']])
        # get email from decoded token
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception

        token_data = TokenData(email=email)
    except PyJWTError:
        raise credentials_exception

    # get user from db by email
    user_in_db = user_repository.get_by_email(email=token_data.email)
    if user_in_db is None:
        raise credentials_exception
    if not user_in_db.is_admin and user_in_db.confirmed == False:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    # return user entity
    return user_in_db


def _get_authorization_header_optional(
    token: Optional[str] = Security(
        OAuth2PasswordBearer(
            tokenUrl=f"{config['API_V1_STR']}/token",
            auto_error=False
        )
    )
) -> str:
    return token if token else None


def _get_current_user_optional(
    user_repository: UserRepository = Depends(UserRepository),
    token: str = Depends(_get_authorization_header_optional)
) -> Optional[UserInDB]:
    if token:
        return _get_current_user(token, user_repository)
    return None


def get_current_active_user(
    current_user: UserInDB = Depends(_get_current_user)
) -> UserInDB:
    if current_user.disabled():
        raise HTTPException(status_code=400, detail="Invalid user")
    return current_user


def get_current_active_superuser(
    current_user: UserInDB = Depends(_get_current_user)
) -> UserInDB:
    if current_user.disabled():
        raise HTTPException(status_code=400, detail="Invalid user")
    if not current_user.is_admin:
        raise HTTPException(status_code=400, detail="Invalid user")
    return current_user


def get_current_active_user_optional(
    current_user: Optional[UserInDB] = Depends(_get_current_user_optional)
) -> Optional[UserInDB]:
    return current_user


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    # clone data
    to_encode = data.copy()
    # set token expire time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config['ACCESS_TOKEN_EXPIRE_MINUTES'])
    to_encode.update({"exp": expire})
    # create jwt token
    encoded_jwt = jwt.encode(to_encode, config['SECRET_KEY'], algorithm=config['ALGORITHM'])
    if isinstance(encoded_jwt, str):
        return encoded_jwt
    else:
        return encoded_jwt.decode('utf-8')

class SecurityService:
    def __init__(self, user_repository: UserRepository = Depends(UserRepository)):
        self.user_repository = user_repository

    def get_user(self, email: str):
        user = self.user_repository.get_by_email(email=email)
        return user

    def authenticate_user(self, email: str, password: str):
        user = self.get_user(email)
        if not user:
            return False
        if not verify_password(password, user[0]['hashed_password']):
            return False
        return user[0]