from aiohttp import web
from .handlers import ChatsSearch, GetTaskStatus, GetTaskMessages


def register_search_routes(app: web.Application, prefix: str = ""):
    app.router.add_view(prefix, ChatsSearch)
    app.router.add_view(prefix + r"/status/{task_id:\w+}", GetTaskStatus)
    app.router.add_view(prefix + r"/{task_id:\w+}/messages", GetTaskMessages)
