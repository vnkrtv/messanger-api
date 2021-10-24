"""
Base middlewares for app
"""
import logging
from http import HTTPStatus
from typing import List, Callable

from aiohttp import web, web_exceptions

from messenger.apps.base_handler import error_response, ErrMsg
from messenger.settings import Config
from messenger.apps.settings_reader.middlewares import user_settings_middleware
from messenger.apps.cache.middlewares import cache_middleware
from messenger.apps.auth.middlewares import auth_middleware
from messenger.apps.throttling.middlewares import throttling_middleware
from messenger.utils.exceptions.auth_exceptions import (
    LoginError,
    RegisterError,
    AccessDeniedError,
)


def get_middlewares() -> List[Callable]:
    middlewares = [exception_middleware]

    cache_enabled = Config.cache_app in Config.apps
    auth_enabled = Config.auth_app in Config.apps

    if cache_enabled:
        middlewares.append(cache_middleware)
    if cache_enabled and auth_enabled:
        middlewares.append(auth_middleware)
    if cache_enabled and auth_enabled and Config.throttling_app in Config.apps:
        middlewares.append(throttling_middleware)
    if Config.settings_reader_app in Config.apps:
        middlewares.append(user_settings_middleware)

    return middlewares


@web.middleware
async def exception_middleware(request: web.Request, handler: Callable) -> web.Response:
    try:
        response = await handler(request)
    except web_exceptions.HTTPBadRequest:
        err_msg = ErrMsg.BAD_PARAMETERS
        response = error_response(
            message=ErrMsg.BAD_PARAMETERS, status=HTTPStatus.BAD_REQUEST
        )

    except web_exceptions.HTTPNotFound as e:
        err_msg = e.reason
        response = error_response(message=err_msg, status=HTTPStatus.NOT_FOUND)

    except web_exceptions.HTTPMethodNotAllowed:
        err_msg = HTTPStatus.METHOD_NOT_ALLOWED.description
        response = error_response(message=err_msg, status=HTTPStatus.METHOD_NOT_ALLOWED)

    except (LoginError, RegisterError) as e:
        err_msg = str(e)
        response = error_response(message=err_msg, status=HTTPStatus.BAD_REQUEST)

    except AccessDeniedError as e:
        err_msg = str(e) or HTTPStatus.UNAUTHORIZED.description
        response = error_response(message=err_msg, status=HTTPStatus.UNAUTHORIZED)

    except web_exceptions.HTTPTooManyRequests as e:
        err_msg = e.reason
        response = error_response(
            message=ErrMsg.REQUEST_LIMIT_EXCEEDED, status=HTTPStatus.TOO_MANY_REQUESTS
        )

    except web_exceptions.HTTPServiceUnavailable as e:
        err_msg = e.reason
        response = error_response(
            message=HTTPStatus.SERVICE_UNAVAILABLE.description,
            status=HTTPStatus.SERVICE_UNAVAILABLE,
        )

    except Exception as e:
        err_msg = str(e)
        response = error_response()

    finally:
        if response.status < 400:
            logging.info(
                "%s %s %s %s",
                request.method,
                request.path,
                response.status,
                request.remote,
            )
        else:
            logging.error(
                "%s %s %s %s %s",
                request.method,
                request.path,
                response.status,
                request.remote,
                err_msg,
            )

    return response
