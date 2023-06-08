from fastapi import APIRouter, Depends, Body, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.shared.decorator import response_decorator
from app.infa.security.security_service import Token

from app.domain.entity import UserInRegister

from app.use_cases.auth.login import LoginRequestObject, LoginUseCase
from app.use_cases.auth.register import RegisterRequestObject, RegisterUseCase

router = APIRouter()

@router.post("/token", response_model=Token)
@response_decorator()
def login_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    login_use_case: LoginUseCase = Depends(LoginUseCase)
):
    """Get access token from credentials

    Args:
        form_data (OAuth2PasswordRequestForm, required): contains email, password for login
    Returns:
        access_token: str
    """
    login_request_object = LoginRequestObject.builder(
        data=dict(
            username=form_data.username,
            password=form_data.password
        ),
    )
    response = login_use_case.execute(request_object=login_request_object)
    return response


@router.post("/register", response_model=Token)
@response_decorator()
def register(
    request: Request,
    data: UserInRegister = Body(..., title='Register: email, first name, last name'),
    register_use_case: RegisterUseCase = Depends(RegisterUseCase)
):
    """Register new account

    Returns:
        verify_token: str
    """
    reg_w_email_request_object = RegisterRequestObject.builder(data=data)
    response = register_use_case.execute(request_object=reg_w_email_request_object)
    return response