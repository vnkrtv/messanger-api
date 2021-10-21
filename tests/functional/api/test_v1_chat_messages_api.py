import json
from http import HTTPStatus
from typing import Any, Optional, Dict

import pytest

from messenger.apps.base_handler import ErrMsg
from tests.functional.api.utils import add_user_to_chat
from tests.functional.conftest import login_client, get_auth_header


@pytest.fixture
def base_path(real_chat_id: str) -> str:
    return f"/v1/chats/{real_chat_id}/messages"


@pytest.mark.parametrize(["limit", "cursor"], [(1, None), (1000, None), (123, None)])
async def test__get_chat_messages__success(
    client: Any, base_path: str, limit: int, cursor: Optional[str]
):
    # given
    session_id = await login_client(client)
    path = f"{base_path}?limit={limit}" + (f"&from={cursor}" if cursor else "")

    # when
    resp = await client.get(path, headers=get_auth_header(session_id))
    resp_data = await resp.json()

    # then
    assert resp.status == HTTPStatus.OK
    assert isinstance(resp_data.get("messages"), list) and isinstance(
        resp_data.get("next"), dict
    )
    assert len(resp_data["messages"]) <= limit
    assert isinstance(resp_data["next"].get("iterator"), str)


@pytest.mark.parametrize("limit", [0, 1001, None])
async def test__get_chat_messages__failed(
    client: Any, base_path: str, limit: Optional[int]
):
    # given
    session_id = await login_client(client)
    path = base_path + (f"?limit={limit}" if limit else "")

    # when
    resp = await client.get(path, headers=get_auth_header(session_id))
    resp_json = await resp.json()

    # then
    assert resp.status == HTTPStatus.BAD_REQUEST
    assert resp_json.get("message") == ErrMsg.BAD_PARAMETERS


@pytest.mark.parametrize(
    "body",
    [
        {"message": "Some message"},
        {"message": 123},
        {"message": "Some message", "extra_param": 1234},
    ],
)
async def test__send_message__success(
    client: Any,
    base_path: str,
    body: Dict[str, Any],
    real_username: str,
    real_chat_id: str,
):
    # given
    session_id = await login_client(client)
    user_id = await add_user_to_chat(client, session_id, real_chat_id, real_username)
    path = f"{base_path}?user_id={user_id}"

    # when
    resp = await client.post(
        path, data=json.dumps(body), headers=get_auth_header(session_id)
    )
    resp_data = await resp.json()

    # then
    assert resp.status == HTTPStatus.CREATED
    assert isinstance(resp_data.get("message_id"), str)


@pytest.mark.parametrize("body", [{}, {"bad_message_key": 123}])
async def test__send_message__failed(
    client: Any, base_path: str, body: Dict[str, Any], real_user_id: str
):
    # given
    session_id = await login_client(client)
    path = f"{base_path}?user_id={real_user_id}"

    # when
    resp = await client.post(
        path, data=json.dumps(body), headers=get_auth_header(session_id)
    )
    resp_json = await resp.json()

    # then
    assert resp.status == HTTPStatus.BAD_REQUEST
    assert resp_json.get("message") == ErrMsg.BAD_PARAMETERS
