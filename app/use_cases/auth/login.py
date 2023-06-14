from app.shared import request_object, use_case, response_object
from app.domain.entity import UserInLogin
from typing import Optional
from pydantic import ValidationError
from app.infa.user.user_repository import UserRepository
from app.infa.security.security_service import SecurityService
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta
from app.config import config
from app.domain.enum import AuthGrantType
from app.infa.security.security_service import create_access_token
from app.shared.utils.general import random_code_5
from app.infa.user.email import send_verify_code
from app.infa.security.security_service import Token


class LoginRequestObject(request_object.ValidRequestObject):
    def __init__(self, login_info: UserInLogin, domain: Optional[str] = None):
        self.login_info = login_info
        self.domain = domain

    @classmethod
    def builder(cls, data: dict, domain: Optional[str] = None) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not data:
            invalid_req.add_error('data', 'Invalid')

        try:
            login_info = UserInLogin(**data)
        except ValidationError as e:
            invalid_req.add_error_map(e.errors())

        if invalid_req.has_errors():
            return invalid_req

        return LoginRequestObject(login_info=login_info, domain=domain)
    


class LoginUseCase(use_case.UseCase):
    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        security_service: SecurityService = Depends(SecurityService)
    ):
        self.user_repository = user_repository
        self.security_service = security_service


    def process_request(self, req_object: LoginRequestObject):
        # authenticate user with auth info
        user = self.security_service.authenticate_user(
            email=req_object.login_info.username,
            password=req_object.login_info.password,
        )
        if not user:
            return HTTPException(status_code=404, detail="User not found")
        expires_now = datetime.utcnow() - timedelta(hours=config['EXPIRES_VERIFY_TOKEN_DELTA'])
        data = {
            "sub": user['email'],
            "id": user['id'],
            "grant_type": AuthGrantType.VERIFY_CODE.value
        }
        if not user['role'] == 'admin':
            token = create_access_token(
                # https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#technical-details-about-the-jwt-subject-sub
                data=data
            )
            if user['updatedAt'] and expires_now > user['updatedAt']:
                code = random_code_5()
                token = send_verify_code(email=user['email'], code=code, id=user['id'], domain=req_object.domain, name=user['fullname'])
            return Token(verify_token=token)
        del data['grant_type']
        # create access token from user data
        access_token = create_access_token(
            # https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/#technical-details-about-the-jwt-subject-sub
            data=data
        )
        return Token(
            access_token=access_token,
            token_type="bearer"
        )
