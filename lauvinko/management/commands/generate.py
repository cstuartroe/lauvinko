import json
import argparse
from typing import Optional
from django.core.management.base import BaseCommand
from lauvinko.lang.shared.semantics import KasanicStemCategory
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicMorpheme
from lauvinko.lang.proto_kasanic.generate import random_pk_lemma
from lauvinko.lang.proto_kasanic.romanize import romanize
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma
from lauvinko.lang.lauvinko.diachronic.base import MorphemeContext
from .clean_dict import DICTIONARY_FILENAME, order_dict


def get_lemma(category: KasanicStemCategory, ident: str, definition: str, form: Optional[str]):
    while True:
        pk_lemma = random_pk_lemma(category)
        pk_lemma.ident = ident
        pk_lemma.definition = definition

        if form:
            pk_lemma.generic_morph = ProtoKasanicMorpheme.from_informal_transcription(form)
            return pk_lemma

        print("Proto-Kasanic morph:  ", romanize(pk_lemma.citation_form().surface_form()))

        lv_lemma = LauvinkoLemma.from_pk(pk_lemma)
        for pta in category.primary_aspects:
            na = lv_lemma.form(pta, MorphemeContext.NONAUGMENTED)
            au = lv_lemma.form(pta, MorphemeContext.AUGMENTED)

            print(pta.name.ljust(22, ' '), au.romanization(), na.romanization())

        if input("Accept? ") == 'y':
            return pk_lemma


class Command(BaseCommand):
    help = 'Autoformats the dictionary'

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument('ident', type=str)
        parser.add_argument('category', type=str)
        parser.add_argument('definition', type=str)
        parser.add_argument('--mstype', '-m', type=str)
        parser.add_argument('--form', '-f', type=str)

    def handle(self, *args, **options):
        with open(DICTIONARY_FILENAME, "r") as fh:
            d = json.load(fh)

        category = KasanicStemCategory[options['category'].upper()]
        ident, definition = options['ident'], options['definition']

        if ident in d:
            print("ID already in use.")
            return

        pk_lemma = get_lemma(category, ident, definition, options.get('form', None))

        lemma = {
            "category": category.name.lower(),
            "languages": {
                "pk": {
                    "definition": definition,
                    "forms": {
                        "gn": pk_lemma.generic_morph.informal_transcription(),
                    },
                },
            },
            "origin": "kasanic",
        }

        if options["mstype"]:
            lemma["mstype"] = options["mstype"]

        d[ident] = lemma

        with open(DICTIONARY_FILENAME, "w") as fh:
            json.dump(order_dict(d), fh, indent=2, sort_keys=False)
