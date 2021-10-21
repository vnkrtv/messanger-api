from datetime import datetime

from pydantic import Field

from messenger.apps.base_schema import BaseSchema


class UserLogin(BaseSchema):
    user_name: str = Field(max_length=255)
    password: str


class CreateUser(BaseSchema):
    username: str = Field(max_length=255)
    password_hash: str = Field(length=64)
    created_at: datetime
