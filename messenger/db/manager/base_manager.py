from datetime import datetime
import uuid
from abc import ABC
from typing import List

from sqlalchemy import Table, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncEngine


class BaseModelManager(ABC):
    engine: AsyncEngine
    model_table: Table

    def __init__(self, model_table: Table, engine: AsyncEngine):
        self.engine = engine
        self.model_table = model_table

    async def all(self) -> List[dict]:
        async with self.engine.connect() as conn:
            result = await conn.execute(select(self.model_table))
            return result.mappings().all()

    async def create(self, obj: dict):
        async with self.engine.connect() as conn:
            await conn.execute(insert(self.model_table).values(**obj))
            await conn.commit()

    @property
    def now(self) -> datetime:
        return datetime.utcnow()

    @staticmethod
    def _gen_pk() -> uuid.UUID:
        """
        Generate UUID1 primary key
        """
        return uuid.uuid1()
