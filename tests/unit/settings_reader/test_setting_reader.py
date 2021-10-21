import json
from datetime import datetime
from typing import Dict

import pytest
import yaml

from messenger.settings import Config
from messenger.utils.settings_reader import (
    YAMLSettingsReader,
    JSONSettingsReader,
    DBSettingsReader,
    UserSettings,
)


@pytest.fixture
def user_id() -> str:
    return "some_user_id"


@pytest.fixture
def yaml_settings_file() -> str:
    return Config.ReadSettingsModule.users_settings_path / "settings.yaml"


@pytest.fixture
def json_settings_file() -> str:
    return Config.ReadSettingsModule.users_settings_path / "settings.json"


@pytest.fixture
def yaml_settings(yaml_settings_file: str) -> str:
    with open(yaml_settings_file, "r") as f:
        return yaml.load(f, Loader=yaml.Loader)


@pytest.fixture
def json_settings(json_settings_file: str) -> str:
    with open(json_settings_file, "r") as f:
        return json.load(f)


async def test__settings_reader__yaml_reader(
    user_id: str, yaml_settings_file: str, yaml_settings: Dict[str, UserSettings]
):
    reader = YAMLSettingsReader(file_name=yaml_settings_file)
    settings = await reader.read_settings(user_id)

    assert settings == yaml_settings.get(user_id)


async def test__settings_reader__json_reader(
    user_id: str, json_settings_file: str, json_settings: Dict[str, UserSettings]
):
    reader = JSONSettingsReader(file_name=json_settings_file)
    settings = await reader.read_settings(user_id)

    assert settings == json_settings.get(user_id)
