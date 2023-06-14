from fastapi import APIRouter, Depends, Body, Request, HTTPException, Security

from app.shared.decorator import response_decorator

from app.domain.entity import UserInChange
from app.infa.security.security_service import verify_token

from app.use_cases.user.change import ChangeRequestObject, ChangeRequestUseCase
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@router.patch("/", response_model=bool, dependencies=[Security(oauth2_scheme)])
@response_decorator()
def change(
    request: Request,
    data: UserInChange = Body(..., title="Change info user"),
    register_use_case: ChangeRequestUseCase = Depends(ChangeRequestUseCase),
):
    """Change info user

    Returns:
        bool
    """
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        return HTTPException(status_code=404, detail="Invalid Token")
    data_token = verify_token(authorization_header)
    reg_w_email_request_object = ChangeRequestObject.builder(data=data)
    if not data_token.id == reg_w_email_request_object.user_info.id:
        return HTTPException(status_code=404, detail="Invalid Token")
    response = register_use_case.process_request(req_object=reg_w_email_request_object)
    return response
