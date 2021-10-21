from typing import Any, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from .base_settings_reader import BaseSettingsReader, UserSettings


class DBSettingsReader(BaseSettingsReader):
    engine: AsyncEngine
    settings_table_schema: Dict[str, str]

    def __init__(self, engine: AsyncEngine, schema: Dict[str, str]):
        self.engine = engine
        self.settings_table_schema = schema

    async def read_settings(self, username: str) -> Optional[UserSettings]:
        sql = self._get_settings_query()
        async with self.engine.connect() as conn:
            result = await conn.execute(text(sql), [{"username": username}])
            row = result.fetchone()
        if not row:
            return None
        return self._get_settings_from_query_result(row)

    def _get_settings_query(self) -> str:
        settings_columns = ", ".join(self.settings_table_schema["settings_columns"])
        table_name = self.settings_table_schema["table_name"]
        sql = f"""
            SELECT {settings_columns}
            FROM {table_name}
            WHERE username = :username
        """
        return sql

    def _get_settings_from_query_result(self, row: List[Any]) -> UserSettings:
        settings_columns = self.settings_table_schema["settings_columns"]
        settings = {}
        for prop_name, value in zip(settings_columns, row):
            settings[prop_name] = value
        return settings
