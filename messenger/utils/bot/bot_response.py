from datetime import datetime
from enum import Enum

import pytz

from messenger.settings import Config
from messenger.utils.settings_reader import UserSettings, Optional


class ErrorCase(Enum):
    DB_UNAVAILABLE = 1
    ACCESS_DENIED = 2
    SERVER_ERROR = 3


class Bot:
    @classmethod
    def get_greeting(cls, user_settings: Optional[UserSettings]) -> str:
        if user_settings:
            timezone = pytz.timezone(user_settings.get("timezone"))
        else:
            timezone = pytz.timezone(Config.timezone)

        now = datetime.now(timezone)

        if now.hour < 6 or now.hour > 22:
            greeting = "Good night"
        elif now.hour < 12:
            greeting = "Good morning"
        elif now.hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        if not user_settings:
            return f"{greeting}, anonymous!"

        first_name = user_settings.get("first_name")
        second_name = user_settings.get("second_name")
        return f"{greeting}, {first_name} {second_name}!"

    @classmethod
    def get_message(cls, user_settings: Optional[UserSettings], case: ErrorCase) -> str:
        msg = cls.get_greeting(user_settings)

        if case == ErrorCase.DB_UNAVAILABLE:
            msg += " The service is temporarily unavailable due to technical works :("

        if case == ErrorCase.ACCESS_DENIED:
            msg += " You have not rights to access this :("

        if case == ErrorCase.SERVER_ERROR:
            msg += (
                " The service is temporarily unavailable :("
                "But our specialists are already fully dealing with this 😎"
            )

        if user_settings and user_settings["is_yandex_backend_school_student"]:
            msg += (
                " Hope this will not interfere with your "
                "preparation for backend school in any way :)"
            )

        return msg
