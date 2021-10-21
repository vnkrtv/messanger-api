from uuid import UUID

from pydantic import Field

from messenger.apps.base_schema import BaseSchema


class SessionCreate(BaseSchema):
    username: str


class Session(BaseSchema):
    session_id: UUID = Field(description="Token")
