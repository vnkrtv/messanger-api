from typing import Callable

from aiohttp import web
from sqlalchemy import text
from sqlalchemy.exc import InterfaceError, OperationalError

from messenger.settings import Config
from messenger.utils.settings_reader import DBSettingsReader, JSONSettingsReader


async def check_conn(request: web.Request) -> bool:
    try:
        async with request.app["engine"].connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except (InterfaceError, OperationalError, OSError):
        return False


@web.middleware
async def user_settings_middleware(
    request: web.Request, handler: Callable
) -> web.Response:
    header_name = Config.ReadSettingsModule.user_id_header
    username = request.headers.get(header_name)

    if await check_conn(request):
        reader = DBSettingsReader(
            request.app["engine"], request.app["settings_table_schema"]
        )
    else:
        reader = JSONSettingsReader(file_name=Config.ReadSettingsModule.settings_file)

    settings = await reader.read_settings(username=username)
    request.app["user_settings"] = settings

    return await handler(request)
