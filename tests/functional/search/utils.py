import json
from http import HTTPStatus
from typing import Dict, Any

from messenger.utils.rabbitmq.task import TaskStatus
from tests.functional.conftest import get_auth_header


async def create_task(
    client: Any, session_id: str, base_path: str, body: Dict[str, Any]
) -> str:
    resp = await client.post(
        base_path, data=json.dumps(body), headers=get_auth_header(session_id)
    )  # create task
    resp_data = await resp.json()
    assert resp.status == HTTPStatus.CREATED
    assert isinstance(resp_data.get("task_id"), str)
    return resp_data["task_id"]


async def get_task_status(
    client: Any, session_id: str, base_path: str, task_id: str,
) -> str:
    path = f"{base_path}/status/{task_id}"
    resp = await client.get(
        path, headers=get_auth_header(session_id)
    )
    resp_data = await resp.json()

    assert resp.status == HTTPStatus.OK
    assert isinstance(resp_data.get("status"), str)
    assert resp_data.get("status") in [
        TaskStatus.WAITING,
        TaskStatus.IN_PROGRESS,
        TaskStatus.SUCCESS,
    ]

    return resp_data['status']
