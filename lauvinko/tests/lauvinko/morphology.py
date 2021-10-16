import unittest
from random import randrange

from lauvinko.lang.shared.semantics import KasanicStemCategory
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicMorpheme
from lauvinko.lang.proto_kasanic.transcribe import falavay as pk_falavay
from lauvinko.lang.proto_kasanic.generate import random_pk_lemma
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma, LauvinkoMorpheme
from lauvinko.lang.lauvinko.diachronic.from_pk import ProtoKasanicOrigin


class LauvinkoMorphologyTests(unittest.TestCase):
    def test_join_equivalence(self):
        for _ in range(50):
            pk_lemma_1 = random_pk_lemma(KasanicStemCategory.UNINFLECTED)
            pk_lemma_2 = random_pk_lemma(KasanicStemCategory.UNINFLECTED)
            stressed = randrange(2)
            augment = randrange(2) == 0

            print(augment, stressed)
            print(pk_lemma_1.citation_form().surface_form().broad_transcription())
            print(pk_lemma_2.citation_form().surface_form().broad_transcription())

            joined_pk_form = ProtoKasanicMorpheme.join(
                [
                    pk_lemma_1.citation_form().main_morpheme,
                    pk_lemma_2.citation_form().main_morpheme,
                ],
                stressed=stressed,
            )

            joined_then_evolved = ProtoKasanicOrigin.evolve_surface_form(joined_pk_form, augment=augment)

            print(joined_then_evolved.historical_transcription())

            lv_form_1 = LauvinkoLemma.from_pk(pk_lemma_1).citation_form(augment=augment or (stressed == 1))

            print(lv_form_1.surface_form().historical_transcription())

            lv_form_2 = LauvinkoLemma.from_pk(pk_lemma_2).citation_form(augment=augment or (stressed == 0))

            print(lv_form_2.surface_form().historical_transcription())

            evolved_then_joined = LauvinkoMorpheme.join(
                [lv_form_1, lv_form_2],
                accented=stressed,
            )

            print(evolved_then_joined.historical_transcription())

            self.assertEqual(
                joined_then_evolved.historical_transcription(),
                evolved_then_joined.historical_transcription(),
            )

            self.assertEqual(
                pk_falavay(joined_pk_form),
                lv_form_1.falavay + lv_form_2.falavay,
            )
