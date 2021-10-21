from aiohttp import web
from .handlers import LoginUser, RegisterUser, LogoutUser


def register_auth_routes(app: web.Application, prefix: str = ""):
    app.router.add_view(prefix + r"/login", LoginUser)
    app.router.add_view(prefix + r"/register", RegisterUser)
    app.router.add_view(prefix + r"/logout", LogoutUser)
