import json
import re
import inspect
import functools
from http import HTTPStatus
from json import JSONDecodeError
from typing import Optional, Union, Any, List, Callable, Dict
from uuid import UUID

import pydantic
from aiohttp import web, hdrs, web_exceptions
from aiohttp.web_response import StreamResponse
from aiohttp_cache.backends import BaseCache

from messenger.db.db_manager import DBManager
from messenger.settings import Config
from messenger.utils.rabbitmq.task_manager import TaskManager


def _uuid_json(obj):
    if isinstance(obj, UUID):
        return obj.hex
    raise TypeError("Unable to serialize {!r}".format(obj))


def json_response(*args, **kwargs) -> web.Response:
    return web.json_response(
        *args, **kwargs, dumps=functools.partial(json.dumps, default=_uuid_json)
    )


def error_response(
    message: Optional[str] = None, status: int = HTTPStatus.INTERNAL_SERVER_ERROR
) -> web.Response:
    """
    Base error response
    """
    status = HTTPStatus(status)
    body = {"message": message or status.description}
    return web.json_response(body, status=status)


class ErrMsg:
    """
    Class with app error messages
    """

    BAD_PARAMETERS: str = "bad-parameters"
    CHAT_NOT_FOUND: str = "chat-not-found"
    USER_NOT_FOUND: str = "user-not-found"
    USER_ALREADY_EXISTS: str = "user-already-exists"
    BAD_PASSWORD: str = "bad-password"
    INVALID_SESSION_ID: str = "invalid-session-id"
    SESSION_ID_EXPIRED: str = "session-id-expired"
    METHOD_NOT_ALLOWED: str = "method-not-allowed"
    REQUEST_LIMIT_EXCEEDED: str = "request-limit-exceeded"
    BAD_CURSOR: str = "bad-cursor"
    AUTH_REQUIRED: str = "auth-failed"
    TASK_NOT_FOUND: str = "task-not-found"
    TASK_NOT_COMPLETE: str = "task-not-complete"
    TASK_FAILED: str = "task-failed"


class BaseHandler(web.View):
    """
    Base handler with builtin methods for getting data from request and path params inlining
    """

    @property
    def db(self) -> DBManager:
        return DBManager(engine=self.request.app["engine"])

    @property
    def cache(self) -> BaseCache:
        return self.request.app["cache"]

    @property
    def task_manager(self) -> TaskManager:
        return TaskManager(redis=self.request.app["redis"])

    @property
    def user(self) -> Dict[str, Any]:
        return self.request.app["user"]

    @property
    async def db_is_alive(self) -> bool:
        return await self.db.check_conn_with_retries(retries=2, timeout=0.5)

    async def get_from_request(self, obj: Union[str, type]) -> Any:
        """
        Get request body param by it's name or validated pydantic object by it's type

        :param obj: body param name or pydantic object type
        :return: body param or pydantic object
        """
        try:
            req_data = await self.request.json()
            if isinstance(obj, str):
                return req_data.get(obj)
            return obj(**req_data)
        except (pydantic.error_wrappers.ValidationError, JSONDecodeError):
            return None

    def _get_typed_params(self, method: Callable) -> List[Any]:
        path_params = []
        for param_name, param_type in inspect.getfullargspec(
            method
        ).annotations.items():
            if param_name == "return":
                continue
            param = self.request.match_info.get(param_name)
            path_params.append(param_type(param))
        return path_params

    async def _iter(self) -> StreamResponse:
        if self.request.method not in hdrs.METH_ALL:
            self._raise_allowed_methods()
        method = getattr(self, self.request.method.lower(), None)
        if method is None:
            self._raise_allowed_methods()

        # If DB is unavailable and handler is not GET /messages, return 503 error
        # Костыль с 3 ДЗ
        # TODO: remove in next tasks
        if (
            not await self.db_is_alive
            and not re.match(r"/ping", self.request.path)
            and not (
                re.match(r"/v1/chats/[\w]+/messages", self.request.path)
                and self.request.method == "GET"
                and Config.settings_reader_app in Config.apps
            )
        ):
            raise web_exceptions.HTTPServiceUnavailable(reason="db unavailable")

        method_params = self._get_typed_params(method)
        resp = await method(*method_params)
        return resp


__all__ = ("error_response", "ErrMsg", "BaseHandler", "json_response")
