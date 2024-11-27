import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=10)
    email: EmailStr = Field(max_length=40)
    password: str = Field(min_length=6)

class UserModel(BaseModel):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4)
    username: str = Field(max_length=10)
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    email: EmailStr = Field(max_length=40)
    role: str = Field(max_length=25)

class UserLoginModel(BaseModel):
    email: EmailStr = Field(max_length=40)
    password: str = Field(min_length=6)

class PasswordResetRequestModel(BaseModel):
    email: str

class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str