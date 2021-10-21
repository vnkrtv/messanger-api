import re
from typing import Union

from aiohttp import web
from aiohttp.abc import StreamResponse
from aiohttp.web_response import Response
from aiohttp_cache.middleware import get_original_handler, HandlerType


@web.middleware
async def cache_middleware(
    request: web.Request, handler: HandlerType
) -> Union[Response, StreamResponse]:
    """Caching middleware.

    Identifies if the handler is intended to be cached.
    If yes, it caches the response using the caching
    backend and on the next call retrieve the response
    from the caching backend.
    """

    original_handler = get_original_handler(handler)

    if getattr(original_handler, "cache_enable", False):
        #
        # Cache is disabled?
        #
        if getattr(original_handler, "cache_unless", False) is True:
            return await handler(request)

        cache_backend = request.app["cache"]

        key = await cache_backend.make_key(request)

        cached_response = await cache_backend.get(key)
        if cached_response:
            return web.Response(**cached_response)

        #
        # Generate cache
        #
        original_response = await handler(request)

        data = {
            "status": original_response.status,
            "headers": dict(original_response.headers),
            "body": original_response.body,
        }

        expires = getattr(original_handler, "cache_expires", 300)

        await cache_backend.set(key, data, expires)

        # Here we selectively prescribe a strategy for working
        # with the cache for specific get methods

        # Get messages
        if re.match(r"/v1/chats/[\w]+/messages", request.path):
            # If cursor set, skip
            if not request.query.get("from"):
                chat_id = request.match_info.get("chat_id")

                cached_keys = await cache_backend.get(chat_id)
                if not cached_keys:
                    await cache_backend.set(chat_id, [key], expires)
                else:
                    if key not in cached_keys:
                        await cache_backend.set(chat_id, cached_keys + [key], expires)

        return original_response

    # Not cached
    return await handler(request)
