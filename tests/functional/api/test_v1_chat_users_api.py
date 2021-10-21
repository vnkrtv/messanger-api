import json
from http import HTTPStatus
from typing import Any, Dict

import pytest

from messenger.apps.base_handler import ErrMsg
from tests.functional.conftest import login_client, get_auth_header


@pytest.fixture
def base_path(real_chat_id: str) -> str:
    return f"/v1/chats/{real_chat_id}/users"


async def test__add_user_to_chat__success(
    client: Any, base_path: str, real_username: str
):
    # given
    session_id = await login_client(client)
    body = {"user_name": real_username}

    # when
    resp = await client.post(
        base_path, data=json.dumps(body), headers=get_auth_header(session_id)
    )
    resp_data = await resp.json()

    # then
    assert resp.status == HTTPStatus.CREATED
    assert isinstance(resp_data.get("user_id"), str)


@pytest.mark.parametrize("body", [{"extra_param": "param"}, {}])
async def test__add_user_to_chat__failed(
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
