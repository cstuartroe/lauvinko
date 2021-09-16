import unittest
from lauvinko.lang.dictionary.dictionary import Dictionary


class DictionaryTests(unittest.TestCase):
    def test_loads(self):
        Dictionary.from_file()