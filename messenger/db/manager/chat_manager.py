from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from messenger.apps.api.schemas import ChatCreate
from messenger.db.manager.base_manager import BaseModelManager
from messenger.db.schema import chats_table


class ChatManager(BaseModelManager):
    def __init__(self, engine: AsyncEngine):
        super().__init__(chats_table, engine)

    async def create(self, chat: ChatCreate) -> UUID:
        new_chat = {
            "creator_username": chat.creator_username,
            "created_at": self.now,
            "name": chat.chat_name,
            "chat_id": self._gen_pk(),
        }
        await super().create(new_chat)
        return new_chat["chat_id"]

    async def get(
        self, chat_id: Optional[UUID] = None, name: Optional[str] = None
    ) -> Optional[dict]:
        if not chat_id and not name:
            raise ValueError

        stmt = select(self.model_table).where(
            self.model_table.c.chat_id == chat_id
            if chat_id
            else self.model_table.c.name == name
        )

        async with self.engine.connect() as conn:
            result = await conn.execute(stmt)
            return result.mappings().first()
