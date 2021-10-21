import json
import logging

import aioredis
from aiomisc.log import basic_config
from aiohttp import web
from aiohttp_cache import setup_cache
from sqlalchemy.ext.asyncio import create_async_engine

from .utils.rabbitmq import events
from .routes import register_routes
from .middlewares import get_middlewares
from .settings import Config

basic_config(Config.Logging.level, buffered=True)


async def init_engine(_app: web.Application):
    """
    Create DB schema and return async SQLAlchemy engine
    """
    _app["engine"] = create_async_engine(
        f"postgresql+asyncpg://{Config.DB.url}",
        pool_size=Config.DB.pool_size,
        echo=Config.Logging.DB.echo,
        echo_pool=Config.Logging.DB.echo_pool,
        hide_parameters=True,
    )


async def init_redis(_app: web.Application):
    _app["redis"] = await aioredis.create_redis_pool(
        address=Config.Redis.url,
        db=Config.Redis.db,
        password=Config.Redis.password,
        maxsize=Config.Redis.pool_maxsize,
    )


async def close_engine(base_app: web.Application):
    """
    Close all active connections
    """
    await base_app["engine"].dispose()


async def close_redis(base_app: web.Application):
    """
    Close all active connections
    """
    base_app["redis"].close()


async def init_settings_module(base_app: web.Application):
    if Config.settings_reader_app in Config.apps:
        with open(Config.ReadSettingsModule.table_schema_file, "r") as f:
            base_app["settings_table_schema"] = json.load(f)


def make_app() -> web.Application:
    base_app = web.Application(middlewares=get_middlewares())
    setup_cache(
        base_app,
        cache_type=Config.Cache.cache_type,
        backend_config=Config.Cache.backend_config,
    )
    logging.info("setup cache: %s", Config.Cache.cache_type)

    register_routes(base_app)

    base_app.on_startup.append(init_engine)
    base_app.on_startup.append(init_redis)
    base_app.on_startup.append(init_settings_module)
    base_app.on_startup.append(events.setup_rabbitmq)

    base_app.on_cleanup.append(close_engine)
    base_app.on_cleanup.append(close_redis)
    base_app.on_cleanup.append(events.close_rabbitmq)

    return base_app


app = make_app()
