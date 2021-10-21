from datetime import datetime
from typing import Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncEngine

from messenger.apps.auth.schemas.session import SessionCreate
from messenger.db.manager.base_manager import BaseModelManager
from messenger.db.schema import sessions_table
from messenger.settings import Config


class SessionManager(BaseModelManager):
    def __init__(self, engine: AsyncEngine):
        super().__init__(sessions_table, engine)

    async def create(self, session: SessionCreate) -> Tuple[UUID, datetime]:
        created_at = self.now
        new_session = session.dict()
        new_session["session_id"] = self._gen_pk()
        new_session["created_at"] = created_at
        new_session["expired_at"] = created_at + Config.Auth.token_lifetime
        await super().create(new_session)
        return new_session["session_id"], new_session["expired_at"]
