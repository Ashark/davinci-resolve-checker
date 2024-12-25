import importlib
import pkgutil
import re
import unittest

import languages
import languages.en_US


class TestLanguages(unittest.TestCase):

    def setUp(self):
        self.english_keys = list(languages.en_US.local_str.keys())

    def test_languages_against_english(self):
        for language in pkgutil.iter_modules(languages.__path__):
            if language.name == "en_US":
                continue

            print(f"Checking locale {language.name}")

            lang_module = importlib.import_module(f"languages.{language.name}")

            self.assertListEqual(
                self.english_keys,
                list(lang_module.local_str.keys()),
            )

            self.assertTrue(
                all([isinstance(val, str) for val in lang_module.local_str.values()])
            )

    def test_local_str_references_in_main_script(self):
        with open("davinci-resolve-checker.py", "r") as file:
            main_script = file.read()

        matches = re.finditer('local_str\["([^".]+)"\]', main_script)

        for match in matches:
            self.assertIn(match.groups()[0], self.english_keys)


if __name__ == "__main__":
    unittest.main()
