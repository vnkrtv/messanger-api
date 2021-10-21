import json
from http import HTTPStatus
from typing import List, Dict, Any


async def create_users_fixtures(client: Any, fixtures: Dict[str, List[Dict[str, Any]]]):
    for user in fixtures["users"]:
        res = await client.post(
            "/v1/auth/register",
            data=json.dumps(
                {"user_name": user["username"], "password": user["password"]}
            ),
        )
        assert res.status == HTTPStatus.CREATED, "failed on registering test users"
