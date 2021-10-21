"""
Service settings
"""
import logging
import pathlib
from datetime import timedelta
from os import getenv
from uuid import UUID

import yarl

from aiohttp_cache import RedisConfig


class Config:
    base_path = pathlib.Path(__file__).parent.parent
    data_path = base_path / "data"

    debug = getenv("DEBUG")
    tests = getenv("TESTS")

    host = getenv("HOST", "0.0.0.0")
    port = getenv("PORT", "8080")

    timezone = "Europe/Moscow"
    default_uuid = UUID("00000000-0000-0000-0000-000000000000")

    auth_disabled = getenv("AUTH_DISABLED", False)

    # All apps
    api_app = "api"
    settings_reader_app = "settings_reader"
    cache_app = "cache"
    auth_app = "auth"
    throttling_app = "throttling"  # needed cache app enabled
    search_app = "throttling"

    # Enabled apps
    apps = [api_app, settings_reader_app, cache_app, search_app]

    apps += [auth_app] if not auth_disabled else []

    class Throttling:
        rps_limit = 100
        enabled_by_nginx = bool(getenv("NGINX_THROTTLING", False))
        enabled_by_cache = not enabled_by_nginx

    apps += [throttling_app] if Throttling.enabled_by_cache else []

    class DB:
        config = {
            # asyncpg не может в dsn с несколькими хостами, поэтому костылим
            # https://github.com/MagicStack/asyncpg/issues/352
            "hosts": getenv("POSTGRES_HOSTS", "localhost:5432").split(",")[0],
            "password": getenv("POSTGRES_PWD", "password"),
            "user": getenv("POSTGRES_USER", "root"),
            "database": getenv("POSTGRES_DB", "yandex_messenger"),
        }

        test_config = {
            "hosts": getenv("TEST_POSTGRES_HOSTS", "localhost:5432").split(",")[0],
            "password": getenv("TEST_POSTGRES_PASSWORD", "password"),
            "user": getenv("TEST_POSTGRES_USER", "root"),
            "database": getenv("TEST_POSTGRES_DB", "test"),
        }

        url = "{user}:{password}@{hosts}/{database}".format(**config)
        test_url = "{user}:{password}@{hosts}/{database}".format(**test_config)

        pool_size = int(getenv("POOL_SIZE", 10))
        consumer_pool_size = int(getenv("CONSUMER_POOL_SIZE", 4))

    class Auth:
        auth_header = "Authorization"
        token_type = "session_id"
        token_len = 32  # uuid.hex length
        token_lifetime = timedelta(hours=1)

    class Redis:
        url = getenv("REDIS_URL", "redis://localhost:6379/0")
        db = int(url.split("/")[-1])
        password = getenv("REDIS_PWD")
        pool_maxsize = 10

    class Cache:
        class CacheType:
            memory = "memory"
            redis = "redis"
            all_types = {_: _ for _ in [memory, redis]}

        class RedisConfig:
            url = yarl.URL(getenv("REDIS_URL", "redis://localhost:6379/0"))
            config = RedisConfig(db=int(url.path[1:]), host=url.host, port=url.port)

        cache_type = CacheType.all_types.get(getenv("CACHE_TYPE"), CacheType.memory)
        backend_config = None if cache_type is CacheType.memory else RedisConfig.config

    class RabbitMQ:
        config = {
            "host": getenv("RMQ_HOST", "localhost"),
            "port": getenv("RMQ_PORT", "5672"),
            "user": getenv("RMQ_USER", "guest"),
            "password": getenv("RMQ_PASSWORD", "guest"),
        }
        url = getenv(
            "RMQ_URL", "amqp://{user}:{password}@{host}:{port}".format(**config)
        )
        tasks_exchange_name = "search_tasks_exchange"
        tasks_routing_key = "search_tasks"
        queue_name = "search_tasks_queue"

    class Bot:
        bot_id = UUID("c8138b88-2b8d-11ec-a208-1b50f3f12fcf")
        bot_username = "bot"

    class ReadSettingsModule:
        user_id_header = "X-User"
        users_settings_path = pathlib.Path(__file__).parent.parent / "data" / "settings"
        table_schema_file = users_settings_path / "db_settings_schema.json"
        settings_file = users_settings_path / "settings.json"

    class Logging:
        level = logging.INFO

        class DB:
            echo = bool(getenv("ECHO_DB"))
            echo_pool = bool(getenv("ECHO_POOL"))
