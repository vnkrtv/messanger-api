from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from messenger.apps.base_schema import BaseSchema


class ChatCreate(BaseSchema):
    chat_name: str = Field(
        description="Created chat name", example="new chat", max_length=255
    )
    creator_username: Optional[str]


class ChatInfo(BaseSchema):
    chat_id: UUID = Field(description="Chat ID")


class Chat(ChatInfo):
    name: str
    description: str
    created_at: datetime
    is_private: bool
