from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from messenger.apps.auth.schemas.user import CreateUser
from messenger.db.manager.base_manager import BaseModelManager
from messenger.db.schema import users_table


class UserManager(BaseModelManager):
    def __init__(self, engine: AsyncEngine):
        super().__init__(users_table, engine)

    async def create(self, user: CreateUser):
        await super().create(user.dict())

    async def get(self, username: str) -> Optional[dict]:
        async with self.engine.connect() as conn:
            result = await conn.execute(
                select(self.model_table).where(self.model_table.c.username == username)
            )
            return result.mappings().first()
