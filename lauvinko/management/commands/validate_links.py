import json
import os
import re
import sys
import mistletoe
from mistletoe.ast_renderer import ASTRenderer
from django.core.management.base import BaseCommand
from .clean_contents import CONTENTS_FILENAME
from .clean_dict import DICTIONARY_FILENAME

PAGES_DIR = "pages/"


def get_section_names(d: dict):
    if "name" in d:
        yield d["name"]

    if "subsections" in d:
        for ss in d["subsections"]:
            yield from get_section_names(ss)


def validate_md(md: dict, section_names: set[str]):
    if md["type"] == "Link":
        target = md["target"]
        if not target.startswith("http"):
            m = re.fullmatch("(/)?([a-z_]+)(\\?.*)?", target)

            if m is not None and ((m.group(1) is None) != (len(md["children"]) == 0)):
                print(f"Only empty links may not start with slash: f{target}")

            if m is None or m.group(2) not in section_names:
                print(f"Invalid link: {repr(target)}", file=sys.stderr)

    for child in md.get("children", []):
        validate_md(child, section_names)


class Command(BaseCommand):
    help = 'Validates links in dictionary and content pages'

    def handle(self, *args, **options):
        with open(CONTENTS_FILENAME, 'r') as fh:
            contents = json.load(fh)

        section_names = set(get_section_names(contents))

        with open(DICTIONARY_FILENAME, 'r') as fh:
            dictionary = json.load(fh)

        for entry in dictionary.values():
            for lang in entry["languages"].values():
                if "definition" in lang:
                    definition = json.loads(mistletoe.markdown(lang["definition"], ASTRenderer))
                    validate_md(definition, section_names)

        for file in os.listdir(PAGES_DIR):
            with open(os.path.join(PAGES_DIR, file), 'r') as fh:
                content = json.loads(mistletoe.markdown(fh.read(), ASTRenderer))

            validate_md(content, section_names)
