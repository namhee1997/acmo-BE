from fastapi import Depends, HTTPException

from app.shared import request_object, use_case
from app.domain.entity import UserInChange

from typing import Optional

from app.infa.user.user_repository import UserRepository
from app.infa.security.security_service import (
    SecurityService,
)

class ChangeRequestObject(request_object.ValidRequestObject):
    def __init__(self, user_info: UserInChange, domain: Optional[str] = None):
        self.user_info = user_info
        self.domain = domain

    @classmethod
    def builder(cls, data: UserInChange, domain: Optional[str] = None) -> request_object.RequestObject:
        invalid_req = request_object.InvalidRequestObject()
        if not data:
            invalid_req.add_error('body', 'Invalid')

        if invalid_req.has_errors():
            return invalid_req

        return ChangeRequestObject(user_info=data, domain=domain)
    
class ChangeRequestUseCase(use_case.UseCase):
    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        security_service: SecurityService = Depends(SecurityService),
    ):
        self.user_repository = user_repository
        self.security_service = security_service


    def process_request(self, req_object: ChangeRequestObject) -> bool:
        exist_user = self.user_repository.get_by_id(user_id=req_object.user_info.id)
        if not exist_user:
            return HTTPException(status_code=404, detail="ID not already exist.")
        # hash password

        self.user_repository.update(id=exist_user[0]['id'],user_update=req_object.user_info)
        return True
