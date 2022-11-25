import json
from django.core.management.base import BaseCommand


CONTENTS_FILENAME = "src/contents.json"

KEY_ORDER = {
    "name": 0,
    "title": 1,
    "subsections": 2,
}


def order_dict(d: dict):
    if "subsections" in d:
        d["subsections"] = list(map(order_dict, d["subsections"]))

    return dict(sorted(list(d.items()), key=lambda x: KEY_ORDER[x[0]]))


class Command(BaseCommand):
    help = 'Autoformats the contents file'

    def handle(self, *args, **options):
        with open(CONTENTS_FILENAME, "r") as fh:
            d = json.load(fh)

        with open(CONTENTS_FILENAME, "w") as fh:
            json.dump(order_dict(d), fh, indent=2, sort_keys=False)
