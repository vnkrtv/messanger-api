from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, desc
from sqlalchemy.ext.asyncio import AsyncEngine

from messenger.apps.api.schemas import Cursor
from messenger.apps.api.schemas.message import ChatMessageCreate
from messenger.db.manager.base_manager import BaseModelManager
from messenger.db.schema import messages_table


class MessageManager(BaseModelManager):
    def __init__(self, engine: AsyncEngine):
        super().__init__(messages_table, engine)

    async def create(self, message: ChatMessageCreate) -> UUID:
        created_at = self.now
        new_message = message.dict()
        new_message["message_id"] = self._gen_pk()
        new_message["created_at"] = created_at
        new_message["updated_at"] = created_at
        await super().create(new_message)
        return new_message["message_id"]

    async def fetch(
        self, chat_id: UUID, limit: int, cursor: Optional[Cursor]
    ) -> Optional[List[dict]]:
        async with self.engine.connect() as conn:
            if not cursor:
                result = await conn.execute(
                    select(self.model_table)
                    .where(self.model_table.c.chat_id == chat_id)
                    .order_by(desc(self.model_table.c.created_at))
                    .limit(limit)
                )
                return result.mappings().all()

            result = await conn.execute(
                select(self.model_table).where(
                    self.model_table.c.message_id == cursor.iterator
                )
            )
            message = result.mappings().first()
            if not message:
                return None

            result = await conn.execute(
                select(self.model_table)
                .where(
                    and_(
                        self.model_table.c.chat_id == chat_id,
                        self.model_table.c.created_at < message["created_at"],
                    )
                )
                .order_by(desc(self.model_table.c.created_at))
                .limit(limit)
            )
            return result.mappings().all()
