import json
import time
import random
from http import HTTPStatus
from typing import Any, Dict

import pytest

from messenger.apps.base_handler import ErrMsg
from messenger.utils.rabbitmq.task import TaskStatus
from tests.functional.conftest import login_client, get_auth_header
from tests.functional.search.utils import create_task, get_task_status
from tests.functional.api.utils import add_user_to_chat, send_message_to_chat


@pytest.fixture
def base_path() -> str:
    return "/v1/chats/search"


@pytest.mark.parametrize(
    "body",
    [
        {"message": "some message"},
        {"message": 123},
        {"message": "some message", "extra_param": 1234},
    ],
)
async def test__create_task__success(client: Any, base_path: str, body: Dict[str, Any]):
    # given
    session_id = await login_client(client)

    # when
    resp = await client.post(
        base_path, data=json.dumps(body), headers=get_auth_header(session_id)
    )
    resp_data = await resp.json()

    # then
    assert resp.status == HTTPStatus.CREATED
    assert isinstance(resp_data.get("task_id"), str)


@pytest.mark.parametrize("body", [{"extra_param": 1234}, {}])
async def test__create_task__failed__bad_body(
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


@pytest.mark.parametrize(
    "body",
    [
        {"message": "some message"},
        {"message": 123},
        {"message": "some message", "extra_param": 1234},
    ],
)
async def test__get_task_status__success(
    client: Any, base_path: str, body: Dict[str, Any]
):
    # given
    session_id = await login_client(client)
    task_id = await create_task(client, session_id, base_path, body)
    path = f"{base_path}/status/{task_id}"

    # when
    resp = await client.get(
        path, headers=get_auth_header(session_id)
    )
    resp_data = await resp.json()

    # then
    assert resp.status == HTTPStatus.OK
    assert isinstance(resp_data.get("status"), str)
    assert resp_data.get("status") in [
        TaskStatus.WAITING,
        TaskStatus.IN_PROGRESS,
        TaskStatus.SUCCESS,
    ]


@pytest.mark.skip()
@pytest.mark.parametrize(
    "message,search_body",
    [
        ("some message", {"message": "some"}),
        ("big small", {"message": "small"}),
        ("some text bla bla", {"message": "bla"}),
    ],
)
async def test__get_task_messages__success(
    client: Any,
    base_path: str,
    message: str,
    search_body: Dict[str, str],
    real_chat_id: str,
    real_username: str,
):
    # given
    session_id = await login_client(client)
    user_id = await add_user_to_chat(client, session_id, real_chat_id, real_username)
    await send_message_to_chat(client, session_id, real_chat_id, user_id, message)
    task_id = await create_task(client, session_id, base_path, search_body)
    task_status = TaskStatus.WAITING
    while task_status != TaskStatus.SUCCESS:
        time.sleep(1 + random.random())
        task_status = await get_task_status(client, session_id, base_path, task_id)
    path = f"{base_path}/{task_id}/messages?limit=1"

    # when
    resp = await client.get(
        path, headers=get_auth_header(session_id)
    )
    resp_data = await resp.json()

    # then
    assert len(resp_data["messages"]) == 1
    assert isinstance(resp_data["next"].get("iterator"), str)
    assert resp_data["messages"] == [message]
