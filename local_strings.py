import importlib
import locale


DEFAULT_LOCALE = 'en_US'


class LocalStrings(dict):

    def __init__(self, preferred_locale=None):
        self.locale = preferred_locale or locale.getdefaultlocale()[0]

        try:
            self.local = importlib.import_module(f'languages.{self.locale}').local_str
        except ModuleNotFoundError:
            print(f'Locale unavailable: {self.locale}, using {DEFAULT_LOCALE} instead')
            self.locale = DEFAULT_LOCALE
            self.local = importlib.import_module(f'languages.{DEFAULT_LOCALE}').local_str

    def __getitem__(self, key: str):
        return self.local[key]
