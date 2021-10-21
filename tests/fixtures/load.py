import uuid
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import create_async_engine

from messenger.db.manager.base_manager import BaseModelManager
from messenger.db.schema import metadata
from messenger.settings import Config

from .users import create_users_fixtures
from .chats import create_chats_fixtures

chats = [
    {"id": UUID("11000000-0000-0000-0000-000000000000"), "name": "chat_name"},
    {"id": UUID("12000000-0000-0000-0000-000000000000"), "name": "some_chat_name"},
]

users = [
    {
        "id": UUID("21000000-0000-0000-0000-000000000000"),
        "username": "test user",
        "password": "password",
    },
    {
        "id": UUID("22000000-0000-0000-0000-000000000000"),
        "username": "some_username",
        "password": "password",
    },
]

fixtures = {"chats": chats, "users": users}
chat_ids = [_["id"] for _ in fixtures["chats"]]
user_ids = [_["id"] for _ in fixtures["users"]]


def gen_pk_mock(*args) -> UUID:
    return next(uuid_id for uuid_id in chat_ids + user_ids)


async def create_fixtures(client: Any):
    engine = create_async_engine(
        f"postgresql+asyncpg://{Config.DB.test_url}", pool_size=1
    )

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    # Mock function, generating ids
    BaseModelManager._gen_pk = gen_pk_mock

    await create_users_fixtures(client, fixtures)
    await create_chats_fixtures(engine, fixtures)

    BaseModelManager._gen_pk = lambda x: uuid.uuid1()

    await engine.dispose()
