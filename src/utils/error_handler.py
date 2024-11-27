from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from typing import Any, Callable


class BaseException(Exception):
    """Base class for all exceptions."""
    pass

class UserAlreadyExists(BaseException):
    """User already exists during sign up."""
    pass

class UserNotFound(BaseException):
    """User Not found"""
    pass

class VerificationError(BaseException):
    """Raised when a verification process encounters an unexpected error."""
    pass

class InvalidTokenError(BaseException):
    """Raised when a token is invalid or malformed."""
    pass


class InvalidCredentials(BaseException):
    """User has provided wrong email or password during log in."""
    pass

class AccessTokenRequired(BaseException):
    """User has provided a refresh token when an access token is needed"""
    pass


class RefreshTokenRequired(BaseException):
    """User has provided an access token when a refresh token is needed"""
    pass



def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: BaseException):

        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler

def register_all_errors(app: FastAPI):
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found",
            },
        ),
    )
    app.add_exception_handler(
        VerificationError,
        create_exception_handler(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            initial_detail={
                "message": "An unexpected error occurred during verification.",
                "error_code": "server_error",
            },
        ),
    )
    app.add_exception_handler(
        InvalidTokenError,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid or malformed token.",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please provide a valid access token",
                "resolution": "Please get an access token",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please provide a valid refresh token",
                "resolution": "Please get an refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )