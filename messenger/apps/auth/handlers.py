from http import HTTPStatus
from datetime import datetime

from aiohttp import web, web_exceptions

from messenger.settings import Config
from messenger.apps.base_handler import BaseHandler, ErrMsg, json_response
from messenger.utils.exceptions.auth_exceptions import RegisterError, LoginError
from messenger.utils.security.auth_utils import AuthUtils
from messenger.utils.security.password_utils import PasswordUtils
from .schemas import UserLogin, SessionCreate
from .schemas.session import Session
from .schemas.user import CreateUser


class RegisterUser(BaseHandler):
    pass_util: PasswordUtils = PasswordUtils()

    async def post(self) -> web.Response:
        """
        /v1/auth/register
        {
          "user_name": <str>,
          "password": <str>
        }

        Create new user with name user_name and set password
        """
        user_login = await self.get_from_request(UserLogin)
        if not user_login:
            raise web_exceptions.HTTPBadRequest(reason=ErrMsg.BAD_PARAMETERS)

        user = await self.db.users.get(username=user_login.user_name)
        if user:
            raise RegisterError(ErrMsg.USER_ALREADY_EXISTS)

        created_at = datetime.now()
        password_hash = self.pass_util.get_password_hash(
            password=user_login.password, created_at=created_at
        )

        await self.db.users.create(
            CreateUser(
                username=user_login.user_name,
                password_hash=password_hash,
                created_at=created_at,
            )
        )

        return web.Response(status=HTTPStatus.CREATED)


class LoginUser(BaseHandler):
    pass_util: PasswordUtils = PasswordUtils()
    auth_util: AuthUtils = AuthUtils()

    async def post(self) -> web.Response:
        """
        /v1/auth/login
        {
          "user_name": <str>,
          "password": <str>
        }

        Auth user with username user_name by password
        """
        user_login = await self.get_from_request(UserLogin)
        if not user_login:
            raise web_exceptions.HTTPBadRequest(reason=ErrMsg.BAD_PARAMETERS)

        user = await self.db.users.get(username=user_login.user_name)
        if not user:
            raise LoginError(ErrMsg.USER_NOT_FOUND)

        password_hash = self.pass_util.get_password_hash(
            password=user_login.password, created_at=user["created_at"]
        )

        if user["password_hash"] != password_hash:
            raise LoginError(ErrMsg.BAD_PASSWORD)

        session_id, expires_at = await self.db.sessions.create(
            SessionCreate(username=user["username"])
        )

        session_lifetime = Config.Auth.token_lifetime.seconds
        session_info = {"username": user["username"], "expires_at": expires_at}
        await self.cache.set(
            key=session_id.hex, value=session_info, expires=session_lifetime * 2
        )

        session = Session(session_id=session_id)
        return json_response(session.dict(), status=HTTPStatus.OK)


class LogoutUser(BaseHandler):
    auth_utils: AuthUtils = AuthUtils()

    async def post(self) -> web.Response:
        """
        /v1/auth/logout

        Logout user by session_id in auth header
        """

        session_id = self.auth_utils.extract_session_id(self.request)

        await self.cache.delete(session_id.hex)

        return web.Response(status=HTTPStatus.OK)


__all__ = ("RegisterUser", "LoginUser", "LogoutUser")
