from gunicorn.app.base import Application
from aiomisc.log import basic_config

from messenger.app import make_app
from messenger.settings import Config


class MessengerApplication(Application):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def main():
    options = {
        "bind": "%s:%s" % (Config.host, Config.port),
        "workers": Config.workers_num,
        "worker_class": "aiohttp.GunicornWebWorker",
    }
    basic_config(Config.Logging.level, buffered=True)
    MessengerApplication(make_app(), options).run()
