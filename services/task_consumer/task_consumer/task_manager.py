import json
from typing import Optional, Union
from uuid import UUID

from aioredis import Redis

from .task import Task


class TaskManager:
    redis: Redis

    def __init__(self, redis: Redis):
        self.redis = redis

    async def put(self, task: Task):
        await self.redis.hmset_dict(task.hex_id, task.dict())

    async def get(self, task_id: Union[UUID, str]) -> Optional[Task]:
        task_id = task_id.hex if isinstance(task_id, UUID) else task_id
        task = await self.redis.hgetall(task_id, encoding="utf-8")
        if task and "dumped_messages" in task:
            task["messages"] = json.loads(task["dumped_messages"])
        return Task(**task) if task else None
