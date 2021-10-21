import json
from typing import Callable, Optional

import yaml

from .base_settings_reader import BaseSettingsReader, UserSettings


class FileSettingsReader(BaseSettingsReader):
    file_name: str
    loader: Callable

    def __init__(self, file_name: str, loader: Callable = lambda f: f.read()):
        self.file_name = file_name
        self.loader = loader

    async def read_settings(self, username: str) -> Optional[UserSettings]:
        with open(self.file_name, "r", encoding="utf-8") as f:
            return self.loader(f).get(username)


class JSONSettingsReader(FileSettingsReader):
    def __init__(self, file_name: str):
        super().__init__(file_name, loader=json.load)


class YAMLSettingsReader(FileSettingsReader):
    def __init__(self, file_name: str):
        super().__init__(file_name, loader=yaml.load)
