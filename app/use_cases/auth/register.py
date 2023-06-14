from fastapi import Depends, HTTPException

from app.shared import request_object, response_object, use_case
from app.domain.entity import UserInRegister
from app.domain.user import UserInCreate

from typing import Optional

from app.infa.user.user_repository import UserRepository
from app.infa.security.security_service import (
    Token,
    SecurityService,
    get_password_hash,
)
from app.shared.utils.general import random_code_5
from app.infa.user.email import send_verify_code, send_welcome_email

class RegisterRequestObject(request_object.ValidRequestObject):
    def __init__(self, user_info: UserInRegister, domain: Optional[str] = None):
        self.user_info = user_info
        self.domain = domain

    @classmethod
    def builder(cls, data: UserInRegister, domain: Optional[str] = None) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not data:
            invalid_req.add_error('body', 'Invalid')

        if invalid_req.has_errors():
            return invalid_req

        return RegisterRequestObject(user_info=data, domain=domain)


class RegisterUseCase(use_case.UseCase):
    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        security_service: SecurityService = Depends(SecurityService),
    ):
        self.user_repository = user_repository
        self.security_service = security_service


    def process_request(self, req_object: RegisterRequestObject) -> Token:
        user_info = req_object.user_info
        domain = req_object.domain
        exist_user = self.user_repository.get_by_email(email=user_info.email)
        if exist_user:
            return HTTPException(status_code=404, detail="Email already exist.")
        # hash password
        hashed_password = get_password_hash(password=user_info.password)
        code = random_code_5()
        user_register_info = UserInCreate(
            **user_info.dict(),
            hashed_password=hashed_password,
            code=code
        )
        entity = self.user_repository.create(user=user_register_info)
        token = send_verify_code(email=entity['email'],code=code, id=entity['id'], domain=domain, name=entity['fullname'])
        send_welcome_email(email=entity['email'], name=entity['fullname'], domain=domain)
        return Token(verify_token=token)
