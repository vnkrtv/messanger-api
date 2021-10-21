from aiohttp import web

from .apps.api.routes import register_api_routes
from .apps.auth.routes import register_auth_routes
from .apps.search.routes import register_search_routes
from .settings import Config


def register_routes(app: web.Application):
    base_path = "/v1"
    if Config.api_app in Config.apps:
        register_api_routes(app)
    if Config.auth_app in Config.apps:
        register_auth_routes(app, prefix=f"{base_path}/auth")
    if Config.search_app in Config.apps:
        register_search_routes(app, prefix=f"{base_path}/chats/search")
