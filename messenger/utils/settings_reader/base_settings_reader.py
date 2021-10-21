from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

UserSettings = Dict[str, Any]


class BaseSettingsReader(ABC):
    @abstractmethod
    async def read_settings(self, username: str) -> Optional[UserSettings]:
        raise NotImplementedError


__all__ = ("UserSettings", "BaseSettingsReader")
