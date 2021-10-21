from uuid import UUID

from pydantic import Field

from messenger.apps.base_schema import BaseSchema


class Cursor(BaseSchema):
    iterator: UUID = Field(description="Last sent message ID", example="some UUID")
