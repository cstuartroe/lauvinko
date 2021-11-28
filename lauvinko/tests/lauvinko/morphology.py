import unittest
from random import randrange, seed

from lauvinko.lang.lauvinko.diachronic.base import MorphemeContext
from lauvinko.lang.shared.morphology import MorphosyntacticType
from lauvinko.lang.shared.semantics import KasanicStemCategory
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicMorpheme, ProtoKasanicLemma
from lauvinko.lang.proto_kasanic.generate import random_pk_lemma, random_pk_morpheme
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma, LauvinkoMorpheme
from lauvinko.lang.lauvinko.diachronic.from_pk import ProtoKasanicOrigin


seed(3)


class LauvinkoMorphologyTests(unittest.TestCase):
    def test_join_equivalence(self):
        num_trials = 250
        num_mismatched = 0

        for _ in range(num_trials):
            pk_lemma_1 = random_pk_lemma(KasanicStemCategory.UNINFLECTED)
            pk_lemma_2 = random_pk_lemma(KasanicStemCategory.UNINFLECTED)
            augment = randrange(2) == 0

            joined_pk_form = ProtoKasanicMorpheme.join(
                [
                    pk_lemma_1.citation_form().main_morpheme,
                    pk_lemma_2.citation_form().main_morpheme,
                ],
                stressed=1
            )

            joined_then_evolved = ProtoKasanicOrigin.evolve_surface_form(
                joined_pk_form,
                context=MorphemeContext.AUGMENTED if augment else MorphemeContext.NONAUGMENTED,
            )

            lv_form_1 = LauvinkoLemma.from_pk(pk_lemma_1).citation_form(
                context=MorphemeContext.PREFIXED
            )

            lv_form_2 = LauvinkoLemma.from_pk(pk_lemma_2).citation_form(
                context=MorphemeContext.AUGMENTED if augment else MorphemeContext.NONAUGMENTED
            )

            evolved_then_joined = LauvinkoMorpheme.join(
                [lv_form_1, lv_form_2],
                accented=1,
            ).surface_form

            if joined_then_evolved.historical_transcription() != evolved_then_joined.historical_transcription():
                print(f"{pk_lemma_1.citation_form().main_morpheme.surface_form.broad_transcription()} and "
                      f"{pk_lemma_2.citation_form().main_morpheme.surface_form.broad_transcription()} became")
                print(f"{joined_then_evolved.historical_transcription()} when evolved as a single word and")
                print(f"{lv_form_1.surface_form.historical_transcription()} + "
                      f"{lv_form_2.surface_form.historical_transcription()} = "
                      f"{evolved_then_joined.historical_transcription()} when joined synchronically")
                print()
                num_mismatched += 1

            # self.assertEqual(
            #     pk_falavay(joined_pk_form, augment=augment),
            #     lv_form_1.falavay + lv_form_2.falavay,
            # )

        print(f"{num_mismatched}/{num_trials} words are different synchronically than diachronically")
