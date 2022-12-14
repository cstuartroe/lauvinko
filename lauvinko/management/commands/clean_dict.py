import json
from typing import Any
from django.core.management.base import BaseCommand
from lauvinko.lang.shared.morphology import MorphosyntacticType
from lauvinko.lang.dictionary.dictionary import DICTIONARY_FILENAME

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
    "$refl$",
]

NUMBER_ORDER = [None, "$sg$", "$du$", "$pl$"]

KEY_ORDERABLE_MSTYPES = (
    MorphosyntacticType.INDEPENDENT.value,
    MorphosyntacticType.NUMBER_SUFFIX.value,
    MorphosyntacticType.PARTICLE.value,
    MorphosyntacticType.ADVERB.value,
)


def key_order(mstype: str, ident: str) -> Any:
    if mstype in KEY_ORDERABLE_MSTYPES:
        return ident
    elif mstype == MorphosyntacticType.CLASS_WORD.value:
        if '.' in ident:
            person, number = ident.split(".")
        else:
            person, number = ident, None

        if person in PERSON_ORDER:
            pix = PERSON_ORDER.index(person)
        else:
            pix = len(person)

        return pix, person, NUMBER_ORDER.index(number)
    elif mstype == MorphosyntacticType.DEFINITE_MARKER.value:
        return None
    else:
        raise NotImplementedError(f"{mstype} ordering not implemented")


def dict_sort(item: tuple[str, dict]) -> tuple[int, Any]:
    ident, entry = item

    mstype = entry.get("mstype", "independent")
    return MSTYPE_ORDER.index(mstype), key_order(mstype, ident)


def order_dict(d: dict) -> dict:
    return dict(sorted(d.items(), key=dict_sort))


class Command(BaseCommand):
    help = 'Autoformats the dictionary'

    def handle(self, *args, **options):
        with open(DICTIONARY_FILENAME, "r") as fh:
            d = json.load(fh)

        ordered = order_dict(d)

        with open(DICTIONARY_FILENAME, "w") as fh:
            json.dump(ordered, fh, indent=2, sort_keys=False)
        