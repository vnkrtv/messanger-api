from uuid import UUID

from typing import List

from messenger.apps.api.schemas import Cursor
from messenger.apps.base_schema import BaseSchema


class HistoryMessage(BaseSchema):
    text: str
    chat_id: UUID


class HistoryMessages(BaseSchema):
    messages: List[HistoryMessage]
    next: Cursor


class MessageSearch(BaseSchema):
    message: str
