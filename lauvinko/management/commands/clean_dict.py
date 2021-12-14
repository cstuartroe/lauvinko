from django.core.management.base import BaseCommand
from lauvinko.lang.dictionary.dictionary import DICTIONARY_FILENAME
import json


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        with open(DICTIONARY_FILENAME, "r") as fh:
            d = json.load(fh)

        with open(DICTIONARY_FILENAME, "w") as fh:
            json.dump(d, fh, indent=2, sort_keys=True)
        