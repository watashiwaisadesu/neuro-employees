from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from fastapi import status

from src.utils.security import (
    create_token,
    create_url_safe_token,
    decode_url_safe_token,
    verify_password,
)
from src.core.config import Config
from src.auth.schemas import (
    UserCreateModel,
    UserLoginModel
)
from src.tasks.email_tasks import send_email
from src.db.repositories.auth_repository import AuthRepository
from src.utils.error_handler import (
    UserAlreadyExists,
    UserNotFound,
    VerificationError,
    InvalidTokenError,
    InvalidCredentials
)

_auth_repository = AuthRepository()


class AuthService:
    async def create_user_service(self, user_data: UserCreateModel, session: AsyncSession):
        if await _auth_repository.user_exists(user_data.email, session):
            raise UserAlreadyExists()

        new_user = await _auth_repository.create_user(user_data, session)

        token = create_url_safe_token({"email": new_user.email})

        # Generate email verification link
        verification_link = f"http://{Config.APP_NAME}/api/v1/auth/verify/{token}"

        html = f"""
        <h1>Verify your Email</h1>
        <p>Please click this <a href="{verification_link}">link</a> to verify your email</p>
        """

        emails = [new_user.email]
        subject = "Verify Your email"

        # Send the verification email asynchronously
        send_email.delay(emails, subject, html)

        return {
            "message": "Account Created! Check email to verify your account",
            "user": new_user,
        }


    async def verify_user_service(self, token: str, session: AsyncSession):
        try:
            token_data = decode_url_safe_token(token)

            user_email = token_data.get("email")
            if not user_email:
                raise InvalidTokenError()

            user = await _auth_repository.get_user_by_email(user_email, session)
            if not user:
                raise UserNotFound()

            await _auth_repository.update_user(user, {"is_verified": True}, session)

            return JSONResponse(
                content={"message": "Account verified successfully"},
                status_code=status.HTTP_200_OK,
            )
        except InvalidTokenError:
            raise
        except UserNotFound:
            raise
        except Exception:
            raise VerificationError()

    async def login_user(self, login_data: UserLoginModel, session: AsyncSession):
        # Get user from the database
        user = await _auth_repository.get_user_by_email(login_data.email, session)

        # Check if user exists
        if user is None:
            raise UserNotFound()

        # Validate password
        password_valid = verify_password(login_data.password, user.password_hash)
        if not password_valid:
            raise InvalidCredentials()

        # Create tokens
        access_token = create_token(
            user_data={
                "email": user.email,
                "user_uid": str(user.uid),
                "role": user.role,
            }
        )

        refresh_token = create_token(
            user_data={
                "email": user.email,
                "user_uid": str(user.uid),
                "role": user.role,
            },
            refresh=True,
            expiry=timedelta(minutes=Config.REFRESH_TOKEN_EXPIRY_DAYS),
        )

        # Return response
        return JSONResponse(
            content={
                "message": "Login Successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {"email": user.email, "uid": str(user.uid), "role": user.role},
            }
        )
