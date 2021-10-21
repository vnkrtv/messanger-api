import json
from http import HTTPStatus
from typing import Dict, Any

from tests.functional.conftest import get_auth_header


async def add_user_to_chat(
    client: Any, session_id: str, chat_id: str, username: str
) -> str:
    add_user_body = {"user_name": username}
    path = f"/v1/chats/{chat_id}/users"
    resp = await client.post(
        path, data=json.dumps(add_user_body), headers=get_auth_header(session_id)
    )  # Add user to chat
    resp_data = await resp.json()

    assert resp.status == HTTPStatus.CREATED, "failed on adding user to chat"
    assert isinstance(resp_data.get("user_id"), str), "failed on adding user to chat"

    return resp_data["user_id"]


async def send_message_to_chat(
    client: Any, session_id: str, chat_id: str, user_id: str, message: str
) -> None:
    path = f"/v1/chats/{chat_id}/messages?user_id={user_id}"
    body = {"message": message}
    resp = await client.post(
        path, data=json.dumps(body), headers=get_auth_header(session_id)
    )
    resp_data = await resp.json()

    assert resp.status == HTTPStatus.CREATED, "error on sending message to chat"
    assert isinstance(resp_data.get("message_id"), str)
