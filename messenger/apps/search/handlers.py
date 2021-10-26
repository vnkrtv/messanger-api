import re
from http import HTTPStatus
from typing import Optional
from uuid import UUID

import pydantic
from aiohttp import web, web_exceptions
from aiohttp_cache import cache

from messenger.settings import Config
from messenger.utils.rabbitmq import events
from messenger.apps.base_handler import BaseHandler, ErrMsg, json_response
from messenger.apps.api.schemas import Cursor
from .schemas import MessageSearch, TaskCreate, TaskStatusResponse
from .schemas.message import HistoryMessages


class ChatsSearch(BaseHandler):
    async def post(self) -> web.Response:
        """
        /v1/chats/search
        {
          "message": <str>
        }

        Create search task with name chat_name
        """
        msg_search = await self.get_from_request(MessageSearch)
        if not msg_search or len(msg_search.message) <= 3:
            raise web_exceptions.HTTPBadRequest(reason=ErrMsg.BAD_PARAMETERS)

        task_id = await events.create_task(
            app=self.request.app,
            username=self.user["username"],
            search=msg_search.message,
        )

        task_info = TaskCreate(task_id=task_id)
        return json_response(task_info.dict(), status=HTTPStatus.CREATED)


class GetTaskStatus(BaseHandler):
    async def get(self, task_id: str) -> web.Response:
        """
        /v1/chats/search/status/{task_id}

        Get task status
        """
        try:
            task_id = UUID(task_id)
        except (TypeError, ValueError) as e:
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.TASK_NOT_FOUND) from e

        task = await self.task_manager.get(task_id)
        if not task or not task.created_by(self.user["username"]):
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.TASK_NOT_FOUND)

        task_status = TaskStatusResponse(status=task.status)
        return json_response(task_status.dict(), status=HTTPStatus.OK)


class GetTaskMessages(BaseHandler):
    @cache()
    async def get(self, task_id: str) -> web.Response:
        """
        /v1/chats/search/{task_id}/messages?limit=<int>[&from=<str>]

        Get limit count of found messages from task(id=task_id) starting with message(id=from)
        """
        try:
            task_id = UUID(task_id)
        except (TypeError, ValueError) as e:
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.TASK_NOT_FOUND) from e

        limit = self.request.query.get("limit")
        limit = int(limit) if limit and not re.sub(r"[\d]+", "", limit) else None
        if not limit or limit < 1 or limit > 1000:
            raise web_exceptions.HTTPBadRequest(reason=ErrMsg.BAD_PARAMETERS)

        task = await self.task_manager.get(task_id)
        if not task or not task.created_by(self.user["username"]):
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.TASK_NOT_FOUND)

        if not task.is_succeed():
            if task.is_failed():
                raise web_exceptions.HTTPBadRequest(reason=ErrMsg.TASK_FAILED)
            raise web_exceptions.HTTPBadRequest(reason=ErrMsg.TASK_NOT_COMPLETE)

        if task.messages:
            messages_map = {_["message_id"]: _ for _ in task.messages}
            await self.cache.set(task_id.hex, messages_map)
            task.messages = None
            await self.task_manager.put(task)
        else:
            messages_map = await self.cache.get(task_id.hex)

        cursor = self.get_cursor_from_query()
        if cursor:
            if cursor.iterator.hex not in messages_map:
                raise web_exceptions.HTTPBadRequest(reason=ErrMsg.BAD_CURSOR)
            start_with = messages_map[cursor.iterator.hex]
            messages = [start_with]
        else:
            first_key = next(iter(messages_map))
            start_with = messages_map[first_key]
            messages = []

        created_at = start_with["created_at"]
        messages += [
            msg
            for i, msg in enumerate(messages_map.values())
            if msg["created_at"] < created_at and limit > i
        ]

        if messages:
            cursor = Cursor(iterator=messages[-1]["message_id"])
        else:
            cursor = Cursor(iterator=Config.default_uuid)

        messages_data = HistoryMessages(messages=messages, next=cursor)
        return json_response(messages_data.dict(), status=HTTPStatus.OK)

    def get_cursor_from_query(self) -> Optional[Cursor]:
        try:
            return Cursor(iterator=self.request.query.get("from"))
        except pydantic.error_wrappers.ValidationError:
            return None


__all__ = ("ChatsSearch", "GetTaskStatus", "GetTaskMessages")
