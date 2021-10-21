import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, InterfaceError
from sqlalchemy.ext.asyncio import AsyncEngine

from messenger.db.manager.chat_manager import ChatManager
from messenger.db.manager.chat_user_manager import ChatUserManager
from messenger.db.manager.message_manager import MessageManager
from messenger.db.manager.session_manager import SessionManager
from messenger.db.manager.user_manager import UserManager


class DBManager:
    engine: AsyncEngine

    def __init__(self, engine: AsyncEngine):
        self.engine = engine

    @property
    def users(self) -> UserManager:
        return UserManager(engine=self.engine)

    @property
    def chats(self) -> ChatManager:
        return ChatManager(engine=self.engine)

    @property
    def sessions(self) -> SessionManager:
        return SessionManager(engine=self.engine)

    @property
    def messages(self) -> MessageManager:
        return MessageManager(engine=self.engine)

    @property
    def chat_users(self) -> ChatUserManager:
        return ChatUserManager(engine=self.engine)

    async def check_conn_with_retries(
        self, retries: int = 5, timeout: float = 1
    ) -> bool:
        while not await self.check_conn() and retries > 0:
            retries -= 1
            time.sleep(timeout)
        return await self.check_conn()

    async def check_conn(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except (InterfaceError, OperationalError, OSError):
            return False
