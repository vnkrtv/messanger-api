import json
import uuid
from typing import Any, Callable, Dict

import pytest

from messenger.app import make_app
from messenger.settings import Config
from tests.fixtures import create_fixtures, fixtures


async def login_client(client: Any) -> str:
    body = {
        "user_name": fixtures["users"][0]["username"],
        "password": fixtures["users"][0]["password"],
    }
    res = await client.post("/v1/auth/login", data=json.dumps(body))
    res_json = await res.json()

    assert res_json.get("session_id") is not None, "auth failed for test client"

    return res_json["session_id"]


def get_auth_header(session_id: str) -> Dict[str, str]:
    return {Config.Auth.auth_header: f"{Config.Auth.token_type} {session_id}"}


@pytest.fixture
def chat_id() -> str:
    return uuid.uuid1().hex


@pytest.fixture
def real_chat_id() -> str:
    return fixtures["chats"][0]["id"].hex


@pytest.fixture
def real_chat_name() -> str:
    return fixtures["chats"][0]["name"]


@pytest.fixture
def real_user_id() -> str:
    return fixtures["users"][0]["id"].hex


@pytest.fixture
def real_username() -> str:
    return fixtures["users"][0]["username"]


@pytest.fixture
async def client(aiohttp_client: Callable) -> Any:
    Config.DB.url = Config.DB.test_url

    app = make_app()
    client = await aiohttp_client(app)
    await create_fixtures(client)

    return client
