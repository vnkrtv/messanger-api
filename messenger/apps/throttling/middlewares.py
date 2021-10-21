from datetime import datetime
from typing import Callable

from aiohttp import web, web_exceptions

from messenger.settings import Config


@web.middleware
async def throttling_middleware(
    request: web.Request, handler: Callable
) -> web.Response:
    cache = request.app["cache"]
    user = request.app.get("user")
    if not user:
        # Auth routes
        key = request.remote
    else:
        key = user["username"] + "_requests"

    user_requests = await cache.get(key)

    timestamp = datetime.now().timestamp()
    threshold = timestamp - 1  # count requests per second

    if not user_requests:
        await cache.set(key=key, value={"timestamps": [timestamp]}, expires=2)
        return await handler(request)

    new_requests_timestamps = [_ for _ in user_requests["timestamps"] if _ >= threshold]
    new_requests_timestamps.append(timestamp)

    if len(new_requests_timestamps) >= Config.Throttling.rps_limit:
        requests_from = f'user(username={user["username"]}' if user else request.remote
        reason = f"too many requests from {requests_from}"
        raise web_exceptions.HTTPTooManyRequests(reason=reason)

    await cache.set(key, {"timestamps": new_requests_timestamps})

    return await handler(request)
