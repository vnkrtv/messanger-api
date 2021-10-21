from uuid import UUID

from messenger.apps.base_schema import BaseSchema


class TaskCreate(BaseSchema):
    task_id: UUID


class TaskStatusResponse(BaseSchema):
    status: str
