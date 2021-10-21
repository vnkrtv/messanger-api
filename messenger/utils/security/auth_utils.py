import re
from typing import Optional, Any
from uuid import UUID

from aiohttp import web

from messenger.settings import Config


class AuthUtils:

    token_re: Any = re.compile(Config.Auth.token_type + r" (.+)")

    @classmethod
    def extract_session_id(cls, request: web.Request) -> Optional[UUID]:
        header_val = request.headers.get(Config.Auth.auth_header)
        if not header_val:
            return None
        res = cls.token_re.findall(header_val)
        try:
            return UUID(res[0])
        except (TypeError, ValueError):
            return None
