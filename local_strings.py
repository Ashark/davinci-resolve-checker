import importlib
import locale
from typing import Optional


DEFAULT_LOCALE = 'en_US'


class LocalStrings(dict):

    def __init__(self, preferred_locale: Optional[str] = None) -> None:
        self.locale: str = preferred_locale or locale.getdefaultlocale()[0]

        self.local: dict = importlib.import_module(f'languages.{self.locale}').local_str

    def __getitem__(self, key: str) -> str:
        return self.local[key]
