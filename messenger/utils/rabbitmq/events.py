import asyncio
import json
import uuid
import logging
from uuid import UUID
from datetime import datetime
from typing import Dict

import aio_pika
import aiormq
from aiohttp import web

from messenger.settings import Config
from .task import Task, TaskStatus


async def setup_rabbitmq(app: web.Application):
    """
    Open connection to RabbitMQ and declare auth exchange,
    try to reconnect every 10 seconds if there is a problem.
    """
    loop = asyncio.get_event_loop()
    try:
        connection: aio_pika.Connection = await aio_pika.connect_robust(
            Config.RabbitMQ.url, loop=loop
        )
    except (ConnectionError, aiormq.exceptions.IncompatibleProtocolError) as e:
        logging.error("action=setup_rabbitmq, status=fail, retry=10s, %s", e)
        await asyncio.sleep(10)
        await setup_rabbitmq(app)
        return None

    channel = await connection.channel()
    tasks_exchange = await channel.declare_exchange(
        name=Config.RabbitMQ.tasks_exchange_name,
        type=aio_pika.ExchangeType.TOPIC,
        durable=True,
    )

    app["rabbitmq"] = connection
    app["rabbitmq_tasks_exchange"] = tasks_exchange
    logging.info("action=setup_rabbitmq, status=success")


async def close_rabbitmq(app: web.Application):
    if app.get("rabbitmq"):
        await app["rabbitmq"].close()
    logging.info("action=close_rabbitmq, status=success")


async def send_event(task_exchange: aio_pika.Exchange, routing_key: str, message: Dict):
    """Publish a message serialized to json to task exchange"""
    await task_exchange.publish(
        aio_pika.Message(
            body=json.dumps(message).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=routing_key,
    )


async def create_task(app: web.Application, username: str, search: str) -> UUID:
    task = Task(
        task_id=uuid.uuid1(),
        status=TaskStatus.WAITING,
        search=search,
        username=username,
        create_ts=datetime.utcnow().timestamp(),
    )
    await app["redis"].hmset_dict(task.hex_id, task.dict())
    await send_event(
        app["rabbitmq_tasks_exchange"],
        routing_key=Config.RabbitMQ.tasks_routing_key,
        message=task.dict(),
    )
    return task.task_id
