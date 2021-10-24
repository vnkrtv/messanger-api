import asyncio
import logging
import time

import uvloop
from aiomisc.log import basic_config

from messenger.settings import Config
from .consumer import run_consumer


def main():
    basic_config(Config.Logging.level, buffered=True)
    uvloop.install()
    while True:
        try:
            asyncio.run(run_consumer())
        except Exception as e:
            # Wait for db
            logging.error("error on running task consumer: %s", e)
            time.sleep(5)
