import asyncio
import json
import logging
import re
from datetime import datetime
from uuid import UUID

import aioredis
import aio_pika
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from aio_pika import Channel

from messenger.settings import Config
from messenger.utils.rabbitmq.task import TaskStatus
from messenger.utils.rabbitmq.task_manager import TaskManager


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex
        if isinstance(obj, datetime):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def prepare_query(query: str) -> str:
    """
    Remove all symbols except letters and numbers
    and return search string for PostgreSQL to_tsquery func
    >>> prepare_query('оченЬ! ЗаГрязненный %% запрос?. !!!')
    ... 'очень<->загрязненный<->запрос'
    """
    q = [
        re.sub(r"[\W]+", "", _).lower()
        for _ in query.split()
        if re.sub(r"[\W]+", "", _)
    ]
    return "<->".join(q)


async def on_task(
    task_manager: TaskManager, engine: AsyncEngine, message: aio_pika.IncomingMessage
):
    async with message.process():
        body = json.loads(message.body)
        task_id = body.get("task_id")

        # Change task status to pending
        task = await task_manager.get(task_id)

        try:
            task.status = TaskStatus.IN_PROGRESS
            await task_manager.put(task)

            sql = """
                SELECT m.*
                FROM to_tsquery(:prepered_query) q,
                     messages m
                JOIN chat_users cu ON m.chat_user_id = cu.chat_user_id
                WHERE to_tsvector(text) @@ q AND cu.username = :username
                ORDER BY created_at DESC
            """
            async with engine.connect() as conn:
                result = await conn.execute(
                    text(sql),
                    {
                        "username": task.username,
                        "prepered_query": prepare_query(task.search),
                    },
                )
                messages = [dict(_) for _ in result.mappings().fetchall()]

            # Change task status to complete
            task.dumped_messages = json.dumps(messages, cls=CustomEncoder)
            task.status = TaskStatus.SUCCESS
        except Exception as e:
            logging.error("error on processing task(task_id=%s)", task_id)
            task.status = TaskStatus.FAILED
            raise Exception(e) from e
        finally:
            logging.info("complete processing task(task_id=%s)", task_id)
            await task_manager.put(task)


async def listen_events(task_manager: TaskManager, engine: AsyncEngine):
    """Declare queue, message binding and start the listener."""
    loop = asyncio.get_event_loop()
    connection: aio_pika.Connection = await aio_pika.connect_robust(
        Config.RabbitMQ.url, loop=loop
    )
    logging.info("opened connection: %s", connection.url)
    try:
        channel: Channel = await connection.channel()
        await channel.set_qos(prefetch_count=100)

        tasks_exchange = await channel.get_exchange(Config.RabbitMQ.tasks_exchange_name)
        queue = await channel.declare_queue(
            name=Config.RabbitMQ.queue_name, durable=True
        )
        await queue.bind(tasks_exchange, routing_key=Config.RabbitMQ.tasks_routing_key)
        logging.info("bind to exchange: %s", Config.RabbitMQ.tasks_exchange_name)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                logging.info("get message: %s", message.body)
                await on_task(task_manager, engine, message)
    except asyncio.CancelledError:
        pass


async def run_consumer():
    engine = create_async_engine(
        f"postgresql+asyncpg://{Config.DB.url}",
        pool_size=Config.DB.consumer_pool_size,
        echo=Config.Logging.DB.echo,
        echo_pool=Config.Logging.DB.echo_pool,
        hide_parameters=True,
    )
    redis = await aioredis.create_redis_pool(
        address=Config.Redis.url,
        db=Config.Redis.db,
        password=Config.Redis.password,
        maxsize=Config.Redis.pool_maxsize,
    )
    task_manager = TaskManager(redis=redis)
    logging.info("created consumer")
    await listen_events(task_manager, engine)
