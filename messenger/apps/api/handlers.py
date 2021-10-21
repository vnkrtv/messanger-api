import re
from typing import Optional
from http import HTTPStatus
from uuid import UUID

import pydantic
from aiohttp import web, web_exceptions
from aiohttp_cache import cache

from messenger.settings import Config
from messenger.utils.bot.bot_response import Bot, ErrorCase
from messenger.apps.base_handler import BaseHandler, ErrMsg, json_response
from .schemas import (
    ChatCreate,
    MessageCreate,
    Cursor,
    ChatInfo,
    MessageInfo,
    MessagesGet,
    ChatUser,
    ChatUserAdd,
    ChatUserInfo,
    ChatMessageCreate,
)


class CreateChat(BaseHandler):
    async def post(self) -> web.Response:
        """
        /v1/chats
        {
          "chat_name": <str>
        }

        Create new chat with name chat_name
        """
        chat = await self.get_from_request(ChatCreate)
        if not chat:
            raise web_exceptions.HTTPBadRequest(reason=ErrMsg.BAD_PARAMETERS)

        chat.creator_username = self.user["username"]
        chat_id = await self.db.chats.create(chat)

        chat_info = ChatInfo(chat_id=chat_id)
        return json_response(chat_info.dict(), status=HTTPStatus.CREATED)


class AddUserToChat(BaseHandler):
    async def post(self, chat_id: str) -> web.Response:
        """
        /v1/chats/{chat_id}/users
        {
           "user_name": <str>
        }

        Add authenticated user to chat(id=chat_id) with ChatUser(chat_username=user_name)
        """
        try:
            chat_id = UUID(chat_id)
        except (TypeError, ValueError) as e:
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.CHAT_NOT_FOUND) from e

        chat_user = await self.get_from_request(ChatUserAdd)
        if not chat_user:
            raise web_exceptions.HTTPBadRequest(reason=ErrMsg.BAD_PARAMETERS)

        chat = await self.db.chats.get(chat_id=chat_id)
        if not chat:
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.CHAT_NOT_FOUND)

        chat_user_id = await self.db.chat_users.create(
            ChatUser(
                chat_id=chat["chat_id"],
                username=self.user["username"],
                chat_username=chat_user.user_name,
            )
        )
        chat_user_info = ChatUserInfo(user_id=chat_user_id)
        return json_response(chat_user_info.dict(), status=HTTPStatus.CREATED)


class ChatMessages(BaseHandler):
    @cache()
    async def get(self, chat_id: str) -> web.Response:
        """
        /v1/chats/{chat_id}/messages?limit=<int>[&from=<str>]

        Get limit count of messages from chat(id=chat_id) starting with message(id=from)
        """
        try:
            chat_id = UUID(chat_id)
        except (TypeError, ValueError) as e:
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.CHAT_NOT_FOUND) from e

        if not await self.db_is_alive:
            # Return message from bot if DB unavailable
            return web.json_response(
                self.get_bot_messages().dict(), status=HTTPStatus.OK
            )

        limit = self.request.query.get("limit")
        limit = (
            int(limit)
            if limit and not re.sub(r"[\d]+", '', limit)
            else None
        )
        if not limit or limit < 1 or limit > 1000:
            raise web_exceptions.HTTPBadRequest(reason=ErrMsg.BAD_PARAMETERS)

        chat = await self.db.chats.get(chat_id=chat_id)
        if not chat:
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.CHAT_NOT_FOUND)

        cursor = self.get_cursor_from_query()
        messages = await self.db.messages.fetch(
            chat_id=chat_id, limit=limit, cursor=cursor
        )
        if messages is None:
            raise web_exceptions.HTTPBadRequest(reason=ErrMsg.BAD_CURSOR)

        if messages:
            cursor = Cursor(iterator=messages[-1]["message_id"])
        else:
            cursor = Cursor(iterator=Config.default_uuid)

        messages_data = MessagesGet(messages=messages, next=cursor)
        return json_response(messages_data.dict(), status=HTTPStatus.OK)

    async def post(self, chat_id: str) -> web.Response:
        """
        /v1/chats/{chat_id}/messages?user_id=<str>
        {
           "message": <str>
        }

        Create new message in chat(id=chat_id) by user(id=user_id)
        """
        try:
            chat_id = UUID(chat_id)
        except (TypeError, ValueError) as e:
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.CHAT_NOT_FOUND) from e

        try:
            chat_user_id = UUID(self.request.query.get("user_id"))
        except (TypeError, ValueError) as e:
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.USER_NOT_FOUND) from e

        req_message = await self.get_from_request(MessageCreate)
        if not chat_user_id or not req_message:
            raise web_exceptions.HTTPBadRequest(reason=ErrMsg.BAD_PARAMETERS)

        if not await self.db.chats.get(chat_id=chat_id):
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.CHAT_NOT_FOUND)

        if not await self.db.chat_users.is_in_chat(
            chat_id=chat_id, chat_user_id=chat_user_id
        ):
            raise web_exceptions.HTTPNotFound(reason=ErrMsg.USER_NOT_FOUND)

        message_id = await self.db.messages.create(
            ChatMessageCreate(
                text=req_message.message, chat_id=chat_id, chat_user_id=chat_user_id
            )
        )
        if req_message.message and Config.Bot.bot_username in req_message.message:
            # Create bot greeting message if it's mentioned
            await self.create_bot_greeting(chat_id)

        await self.update_cache(str(chat_id))

        message_info = MessageInfo(message_id=message_id)
        return json_response(message_info.dict(), status=HTTPStatus.CREATED)

    def get_bot_messages(self) -> MessagesGet:
        bot_message = Bot.get_message(
            user_settings=self.request.app.get("user_settings"),
            case=ErrorCase.DB_UNAVAILABLE,
        )
        return MessagesGet(
            messages=[{"text": bot_message}], next=Cursor(iterator=Config.default_uuid)
        )

    def get_cursor_from_query(self) -> Optional[Cursor]:
        try:
            return Cursor(iterator=self.request.query.get("from"))
        except pydantic.error_wrappers.ValidationError:
            return None

    async def create_bot_greeting(self, chat_id: UUID):
        bot_greeting = Bot.get_greeting(self.request.app.get("user_settings"))
        await self.db.messages.create(
            ChatMessageCreate(
                text=bot_greeting, chat_id=chat_id, chat_user_id=Config.Bot.bot_id
            )
        )

    async def update_cache(self, chat_id: str):
        # Cached keys for responses with set limit and not set cursor
        cached_keys = await self.cache.get(chat_id)
        if cached_keys:
            for key in cached_keys:
                # Delete cached responses
                await self.cache.delete(key)
            await self.cache.delete(chat_id)


class PingDB(BaseHandler):
    async def get(self) -> web.Response:
        if not await self.db.check_conn():
            raise web_exceptions.HTTPServiceUnavailable
        return web.Response(status=HTTPStatus.OK)


class Ping(BaseHandler):
    async def get(self) -> web.Response:
        return web.Response(status=HTTPStatus.OK)


__all__ = ("CreateChat", "AddUserToChat", "ChatMessages", "PingDB", "Ping")
