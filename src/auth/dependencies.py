from fastapi import Request, Depends
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database_setup import get_async_db
from src.db.redis import token_in_blocklist
from src.db.repositories.auth_repository import AuthRepository
from src.utils.error_handler import (
    InvalidTokenError,
    AccessTokenRequired,
    RefreshTokenRequired,
)
from src.utils.security import decode_token


_auth_repository = AuthRepository()

class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        print(request)
        creds = await super().__call__(request)

        if not creds:
            raise InvalidTokenError()
        token = creds.credentials
        print(token)

        if not self.token_valid(token):
            raise InvalidTokenError()

        token_data = decode_token(token)
        print(token_data)

        if await token_in_blocklist(token_data["jti"]):
            raise InvalidTokenError()

        self.verify_token_data(token_data)

        return token_data

    def token_valid(self, token):
        try:
            token_data = decode_token(token)
            return token_data is not None
        except Exception:
            return False

    def verify_token_data(self, token):
        raise NotImplementedError("Please Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict):
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()

class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_async_db),
):
    user_email = token_details["user"]["email"]

    user = await _auth_repository.get_user_by_email(user_email, session)

    return user

# class RoleChecker:
#     def __init__(self, allowed_roles: List[str]) -> None:
#         self.allowed_roles = allowed_roles
#
#     def __call__(self, current_user: User = Depends(get_current_user)) -> Any:
#         if not current_user.is_verified:
#             raise AccountNotVerified()
#         if current_user.role in self.allowed_roles:
#             return True
#
#         raise InsufficientPermission()
