from fastapi import Depends, HTTPException

from app.shared import use_case

from app.infa.user.user_repository import UserRepository
from app.infa.security.security_service import (
    SecurityService,
)
from app.domain.entity import UserMe
    
class MeRequestUseCase(use_case.UseCase):
    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        security_service: SecurityService = Depends(SecurityService),
    ):
        self.user_repository = user_repository
        self.security_service = security_service


    def process_request(self, email) -> UserMe:
        exist_user = self.user_repository.get_by_email(email=email)[0]
        if not exist_user:
            return HTTPException(status_code=404, detail="Email not already exist.")
        # hash password
        exist_user.pop('hashed_password', None) 
        return exist_user
