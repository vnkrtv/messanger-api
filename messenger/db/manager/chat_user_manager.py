from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncEngine

from messenger.apps.api.schemas.chat_user import ChatUser
from messenger.db.manager.base_manager import BaseModelManager
from messenger.db.schema import chat_users_table


class ChatUserManager(BaseModelManager):
    def __init__(self, engine: AsyncEngine):
        super().__init__(chat_users_table, engine)

    async def create(self, chat_user: ChatUser) -> UUID:
        new_chat_user = chat_user.dict()
        new_chat_user["chat_user_id"] = self._gen_pk()
        await super().create(new_chat_user)
        return new_chat_user["chat_user_id"]

    async def is_in_chat(self, chat_id: UUID, chat_user_id: UUID) -> bool:
        async with self.engine.connect() as conn:
            result = await conn.execute(
                select(self.model_table).where(
                    (
                        and_(
                            self.model_table.c.chat_id == chat_id,
                            self.model_table.c.chat_user_id == chat_user_id,
                        )
                    )
                )
            )
            return len(result.fetchall()) > 0
