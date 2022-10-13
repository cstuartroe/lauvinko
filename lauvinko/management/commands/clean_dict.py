import json
from typing import Any
from django.core.management.base import BaseCommand
from lauvinko.lang.shared.morphology import MorphosyntacticType
from lauvinko.lang.dictionary.dictionary import DICTIONARY_FILENAME
from lauvinko.lang.lauvinko.morphology import LauvinkoCase

MSTYPE_ORDER = [
    t.value
    for t in MorphosyntacticType
]

PERSON_ORDER = [
    "$1excl$",
    "$1incl$",
    "$2fam$",
    "$2fml$",
    "$2hon$",
    "$3rd$",
    "$hea$",
    "$bra$",
    "$lea$",
    "$rck$",
    "$sea$",
]

NUMBERLESS_PERSONS = {"$2hon$", "$sea$"}

NUMBER_ORDER = ["$sg$", "$du$", "$pl$"]


def key_order(mstype: str, ident: str) -> Any:
    if mstype == MorphosyntacticType.INDEPENDENT.value or mstype == MorphosyntacticType.NUMBER_SUFFIX.value:
        return ident
    elif mstype == MorphosyntacticType.CLASS_WORD.value:
        if ident in NUMBERLESS_PERSONS:
            person, number = ident, "$sg$"
        else:
            person, number = ident.split(".")

        return PERSON_ORDER.index(person), NUMBER_ORDER.index(number)
    elif mstype == MorphosyntacticType.DEFINITE_MARKER.value:
        return None
    else:
        raise NotImplementedError(f"{mstype} ordering not implemented")


def dict_sort(item: tuple[str, dict]) -> tuple[int, Any]:
    ident, entry = item

    mstype = entry.get("mstype", "independent")
    return MSTYPE_ORDER.index(mstype), key_order(mstype, ident)


class Command(BaseCommand):
    help = 'Autoformats the dictionary'

    def handle(self, *args, **options):
        with open(DICTIONARY_FILENAME, "r") as fh:
            d = json.load(fh)

        d = dict(sorted(d.items(), key=dict_sort))

        with open(DICTIONARY_FILENAME, "w") as fh:
            json.dump(d, fh, indent=2, sort_keys=False)
        