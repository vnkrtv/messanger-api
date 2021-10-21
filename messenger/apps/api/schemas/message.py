from typing import List, Optional
from uuid import UUID

from messenger.apps.base_schema import BaseSchema
from messenger.apps.api.schemas.cursor import Cursor


class MessageCreate(BaseSchema):
    message: str


class ChatMessageCreate(BaseSchema):
    text: str
    chat_user_id: UUID
    chat_id: UUID


class MessageGet(BaseSchema):
    text: str


class MessageInfo(BaseSchema):
    message_id: UUID


class MessagesGet(BaseSchema):
    messages: List[MessageGet]
    next: Optional[Cursor]
