from typing import List, Dict, Any, Optional, Union
from uuid import UUID

from attr import dataclass, field


class TaskStatus:
    WAITING: str = "WAITING"
    IN_PROGRESS: str = "IN_PROCESS"
    SUCCESS: str = "SUCCESS"
    FAILED: str = "FAILED"


@dataclass
class Task:
    task_id: Union[UUID, str]
    status: str
    search: str
    username: str
    create_ts: float
    messages: Optional[List[Dict[str, Any]]] = field(default=None)
    dumped_messages: Optional[str] = field(default=None)

    @property
    def hex_id(self) -> str:
        return self.task_id.hex if isinstance(self.task_id, UUID) else self.task_id

    def dict(self) -> Dict[str, Any]:
        task = {
            "task_id": self.hex_id,
            "status": self.status,
            "search": self.search,
            "username": self.username,
            "create_ts": self.create_ts,
        }
        if self.messages:
            task["messages"] = self.messages
        if self.dumped_messages:
            task["dumped_messages"] = self.dumped_messages

        return task

    def created_by(self, username: str) -> bool:
        return self.username == username

    def is_succeed(self) -> bool:
        return self.status == TaskStatus.SUCCESS

    def is_failed(self) -> bool:
        return self.status == TaskStatus.FAILED
