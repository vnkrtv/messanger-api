import json
from http import HTTPStatus
from typing import Any, Dict

import pytest

from tests.functional.conftest import login_client, get_auth_header


@pytest.fixture
def base_path() -> str:
    return "/v1/auth"


@pytest.mark.parametrize(
    "path",
    [
        "/ping",
        "/ping_db",
    ],
)
async def test__ping_requests(client: Any, path: str):
    # when
    res = await client.get(path)

    # then
    assert res.status == HTTPStatus.OK


@pytest.mark.parametrize(
    "path",
    [
        "/api/chats",
        "/api/some_chat_id/users",
        "/api/some_chat_id/messages",
        "/auth/logout",
        "/chats/search",
    ],
)
async def test__unauthorized_requests(client: Any, path: str):
    # given
    base_path = "/v1"
    path = f"{base_path}/{path}"

    # when
    res = await client.post(path)

    # then
    assert res.status == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize("body", [{"user_name": "some user", "password": "pass"}])
async def test__register__success(client: Any, base_path: str, body: Dict[str, Any]):
    # given
    path = f"{base_path}/register"

    # when
    res = await client.post(path, data=json.dumps(body))

    # then
    assert res.status == HTTPStatus.CREATED


@pytest.mark.parametrize("body", [{"user_name": "another user", "password": "pass"}])
async def test__login__success(client: Any, base_path: str, body: Dict[str, Any]):
    # given
    path = f"{base_path}/register"
    res = await client.post(path, data=json.dumps(body))
    assert res.status == HTTPStatus.CREATED
    path = f"{base_path}/login"

    # when
    res = await client.post(path, data=json.dumps(body))
    res_json = await res.json()

    # then
    assert isinstance(res_json.get("session_id"), str), "auth failed"


async def test__logout__success(client: Any, base_path: str):
    # given
    session_id = await login_client(client)
    path = f"{base_path}/logout"

    # when
    res = await client.post(path, headers=get_auth_header(session_id))

    # then
    assert res.status == HTTPStatus.OK


async def test__logout__failed(client: Any, base_path: str):
    # given
    path = f"{base_path}/logout"

    # when
    res = await client.post(path)

    # then
    assert res.status == HTTPStatus.UNAUTHORIZED
