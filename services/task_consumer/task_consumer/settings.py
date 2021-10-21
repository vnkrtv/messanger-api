"""
Service settings
"""
import logging
from os import getenv


class Config:
    class DB:
        config = {
            # asyncpg не может в dsn с несколькими хостами, поэтому костылим
            # https://github.com/MagicStack/asyncpg/issues/352
            "hosts": getenv("POSTGRES_HOSTS", "localhost:5432").split(",")[0],
            "password": getenv("POSTGRES_PWD", "password"),
            "user": getenv("POSTGRES_USER", "root"),
            "database": getenv("POSTGRES_DB", "yandex_messenger"),
        }
        url = "{user}:{password}@{hosts}/{database}".format(**config)

        consumer_pool_size = int(getenv("CONSUMER_POOL_SIZE", 4))

    class Redis:
        url = getenv("REDIS_URL", "redis://localhost:6379/0")
        db = int(url.split("/")[-1])
        password = getenv("REDIS_PWD")
        pool_maxsize = 10

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

    class Logging:
        level = logging.INFO

        class DB:
            echo = bool(getenv("ECHO_DB"))
            echo_pool = bool(getenv("ECHO_POOL"))
