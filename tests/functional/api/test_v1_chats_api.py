import json
from http import HTTPStatus
from typing import Any, Dict

import pytest

from messenger.apps.base_handler import ErrMsg
from tests.functional.conftest import login_client, get_auth_header


@pytest.fixture
def base_path() -> str:
    return "/v1/chats"


@pytest.mark.parametrize(
    "body",
    [
        {"chat_name": "new chat name"},
        {"chat_name": 123},
        {"chat_name": "new chat name", "extra_param": 1234},
    ],
)
async def test__create_chat__success(client: Any, base_path: str, body: Dict[str, Any]):
    # given
    session_id = await login_client(client)

    # when
    resp = await client.post(
        base_path, data=json.dumps(body), headers=get_auth_header(session_id)
    )
    resp_data = await resp.json()

    # then
    assert resp.status == HTTPStatus.CREATED
    assert isinstance(resp_data.get("chat_id"), str)


@pytest.mark.parametrize("body", [{"extra_param": 1234}, {}])
async def test__create_chat__failed__no_chat_name(
    client: Any, base_path: str, body: Dict[str, Any]
):
    # given
    session_id = await login_client(client)

    # when
    resp = await client.post(
        base_path, data=json.dumps(body), headers=get_auth_header(session_id)
    )
    resp_json = await resp.json()

    # then
    assert resp.status == HTTPStatus.BAD_REQUEST
    assert resp_json.get("message") == ErrMsg.BAD_PARAMETERS
