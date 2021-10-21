import uuid
from typing import List, Dict, Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from messenger.apps.api.schemas import ChatCreate
from messenger.db.manager.chat_manager import ChatManager


async def create_chats_fixtures(
    engine: AsyncEngine, fixtures: Dict[str, List[Dict[str, Any]]]
):
    chats = [
        ChatCreate(chat_name=chat["name"], creator_username=user["username"])
        for chat, user in zip(fixtures["chats"], fixtures["users"])
    ]
    manager = ChatManager(engine)
    for chat in chats:
        try:
            await manager.create(chat)
        except IntegrityError:
            # fixture already added
            pass
