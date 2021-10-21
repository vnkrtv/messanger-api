from uuid import UUID

from pydantic import Field

from messenger.apps.base_schema import BaseSchema


class ChatUserAdd(BaseSchema):
    user_name: str = Field(
        description="User name", example="Vasya Pupkin", max_length=255
    )


class ChatUserInfo(BaseSchema):
    user_id: UUID = Field(description="User ID in chat")


class ChatUser(BaseSchema):
    chat_id: UUID
    username: str
    chat_username: str
    is_admin: bool = Field(default=False)
