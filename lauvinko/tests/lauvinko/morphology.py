import unittest
from random import randrange, seed

from lauvinko.lang.lauvinko.diachronic.base import MorphemeContext
from lauvinko.lang.shared.semantics import KasanicStemCategory
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicMorpheme, ProtoKasanicLemma
from lauvinko.lang.proto_kasanic.transcribe import falavay as pk_falavay
from lauvinko.lang.proto_kasanic.generate import random_pk_lemma, random_pk_morpheme
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma, LauvinkoMorpheme
from lauvinko.lang.lauvinko.diachronic.from_pk import ProtoKasanicOrigin


seed(3)


class LauvinkoMorphologyTests(unittest.TestCase):
    def test_join_equivalence(self):
        for _ in range(50):
            pk_lemma_1 = ProtoKasanicLemma(
                generic_morph=random_pk_morpheme(),
                category=KasanicStemCategory.UNINFLECTED,
                definition="",
                forms={},
            )
            pk_lemma_2 = random_pk_lemma(KasanicStemCategory.UNINFLECTED)
            augment = randrange(2) == 0

            print(augment)
            print(pk_lemma_1.citation_form().surface_form().broad_transcription())
            print(pk_lemma_2.citation_form().surface_form().broad_transcription())

            joined_pk_form = ProtoKasanicMorpheme.join(
                [
                    pk_lemma_1.citation_form().main_morpheme,
                    pk_lemma_2.citation_form().main_morpheme,
                ],
                stressed=1
            )

            print(joined_pk_form.broad_transcription())

            joined_then_evolved = ProtoKasanicOrigin.evolve_surface_form(
                joined_pk_form,
                context=MorphemeContext.AUGMENTED if augment else MorphemeContext.NONAUGMENTED,
            )

            print(joined_then_evolved.historical_transcription())

            lv_form_1 = LauvinkoLemma.from_pk(pk_lemma_1).citation_form(
                context=MorphemeContext.PREFIXED
            )

            print(lv_form_1.surface_form.historical_transcription())

            lv_form_2 = LauvinkoLemma.from_pk(pk_lemma_2).citation_form(
                context=MorphemeContext.AUGMENTED if augment else MorphemeContext.NONAUGMENTED
            )

            print(lv_form_2.surface_form.historical_transcription())

            evolved_then_joined = LauvinkoMorpheme.join(
                [lv_form_1, lv_form_2],
                accented=1,
            )

            print(evolved_then_joined.historical_transcription())

            self.assertEqual(
                joined_then_evolved.historical_transcription(),
                evolved_then_joined.historical_transcription(),
            )

            # self.assertEqual(
            #     pk_falavay(joined_pk_form, augment=augment),
            #     lv_form_1.falavay + lv_form_2.falavay,
            # )
