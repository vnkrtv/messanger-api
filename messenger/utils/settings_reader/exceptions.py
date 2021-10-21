class ReadSettingsException(Exception):
    pass


class UserSettingsNotExist(ReadSettingsException):
    pass


class BadSettingsFileException(ReadSettingsException):
    pass
