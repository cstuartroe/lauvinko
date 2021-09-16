from typing import List
import json
from lauvinko.lang.dictionary.entry import DictEntry


class Dictionary:
    def __init__(self, entries: List[DictEntry]):
        self.entries = entries

    def where(self, f):
        return Dictionary([
            entry
            for entry in self.entries
            if f(entry)
        ])

    @classmethod
    def from_file(cls, filename="lauvinko/lang/dictionary.json"):
        with open(filename, "r") as fh:
            entries_dict = json.load(fh)

        entries = [
            DictEntry.from_json_entry(ident=ident, json_entry=json_entry)
            for ident, json_entry in entries_dict.items()
            if json_entry["origin"] == "kasanic"  # TODO support other languages
        ]

        return cls(entries)
