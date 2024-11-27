from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.core.database_setup import get_async_db
from src.auth.service import AuthService
from src.utils.security import create_token
from src.auth.dependencies import (
    AccessTokenBearer,
    RefreshTokenBearer,
    get_current_user
)
from src.auth.schemas import (
    UserCreateModel,
    UserLoginModel,
    UserModel
)
from src.utils.error_handler import (
    UserAlreadyExists,
    InvalidTokenError
)

# Create the auth router
auth_router = APIRouter()
_auth_service = AuthService()


@auth_router.post("/signup")
async def create_user_account(
        user_data: UserCreateModel, session: AsyncSession = Depends(get_async_db)
):
    # If user exists, it will raise a UserAlreadyExists exception
    new_user = await _auth_service.create_user_service(user_data, session)
    return new_user

@auth_router.get("/verify/{token}")
async def verify_user_account(
        token: str, session: AsyncSession = Depends(get_async_db)
):
    response = await _auth_service.verify_user_service(token, session)
    return response

@auth_router.post("/login")
async def login_users(
        login_data: UserLoginModel, session: AsyncSession = Depends(get_async_db)
):
    response = await _auth_service.login_user(login_data, session)
    return response


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_access_token = create_token(user_data=token_details["user"])

        return JSONResponse(content={"access_token": new_access_token})

    raise InvalidTokenError()


@auth_router.get("/me", response_model=UserModel)
async def get_me(
    user=Depends(get_current_user),
    # _: bool = Depends(role_checker)
):
    return user


