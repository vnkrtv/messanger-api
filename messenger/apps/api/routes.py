from aiohttp import web
from .handlers import CreateChat, AddUserToChat, ChatMessages, Ping, PingDB


def register_api_routes(app: web.Application, prefix: str = ""):
    app.router.add_view(prefix + r"/v1/chats", CreateChat)
    app.router.add_view(prefix + r"/v1/chats/{chat_id:\w+}/users", AddUserToChat)
    app.router.add_view(prefix + r"/v1/chats/{chat_id:\w+}/messages", ChatMessages)
    app.router.add_view(prefix + r"/ping_db", PingDB)
    app.router.add_view(prefix + r"/ping", Ping)
