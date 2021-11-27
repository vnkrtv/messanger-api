import re
from datetime import datetime
from typing import Callable

from aiohttp import web
from messenger.utils.exceptions.auth_exceptions import AccessDeniedError
from messenger.utils.security.auth_utils import AuthUtils
from messenger.apps.base_handler import ErrMsg


@web.middleware
async def auth_middleware(request: web.Request, handler: Callable) -> web.Response:
    """
    Get session_id from Config.Auth.auth_header and validate it
    Add app['user'] context:
    {
        'username': <str>
    }
    """
    session_id = AuthUtils.extract_session_id(request)
    if not session_id:
        # TODO: make login_required decorator and check here access to pages
        if re.match(r"(/v1/auth/(login|register)|/ping_db|/ping)", request.path):
            return await handler(request)
        raise AccessDeniedError(ErrMsg.AUTH_REQUIRED)

    cache = request.app["cache"]
    session_params = await cache.get(session_id.hex)
    if not session_params:
        raise AccessDeniedError(ErrMsg.INVALID_SESSION_ID)

    username = session_params["username"]
    if session_params["expires_at"] < datetime.utcnow():
        await cache.delete(session_id.hex)
        await cache.delete(f"{username}_requests")
        raise AccessDeniedError(ErrMsg.SESSION_ID_EXPIRED)

    request["user"] = {"username": username}

    return await handler(request)
