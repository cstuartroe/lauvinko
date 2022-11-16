import unittest
from random import randrange, seed

from lauvinko.lang.lauvinko.diachronic.base import MorphemeContext
from lauvinko.lang.shared.morphology import MorphosyntacticType
from lauvinko.lang.shared.semantics import KasanicStemCategory
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicMorpheme, pkm, ProtoKasanicLemma
from lauvinko.lang.proto_kasanic.generate import random_pk_lemma
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma, LauvinkoMorpheme, LauvinkoWord, LauvinkoContentWord
from lauvinko.lang.lauvinko.diachronic.from_pk import ProtoKasanicOrigin

lm = LauvinkoMorpheme.from_informal_transcription


# seed(3)

PK_JOINS: list[tuple[ProtoKasanicMorpheme, ProtoKasanicMorpheme, LauvinkoMorpheme]] = [
    (pkm("ttu"), pkm("inkwa/kitaa"), lm("ttavinpe/t")),
    (pkm("poha"), pkm("ita"), lm("povi/r")),
]

JOINS: list[tuple[LauvinkoMorpheme, LauvinkoMorpheme, int, LauvinkoMorpheme]] = [
    (lm("po/a"), lm("tta/"), 1, lm("povatta/")),
]

CLITICS: list[tuple[LauvinkoMorpheme, LauvinkoMorpheme, int, LauvinkoMorpheme]] = [
    (lm("po/a"), lm("i/r"), 0, lm("po/ayir")),
    (lm("po/a"), lm("a/r"), 0, lm("po/var")),
]


class LauvinkoMorphologyTests(unittest.TestCase):
    def test_specific_joins(self):
        for m1, m2, accented, expected_join in JOINS:
            actual_join = LauvinkoMorpheme.join([m1, m2], accented)

            self.assertEqual(
                expected_join.romanization(),
                actual_join.romanization(),
            )

    def test_diachronic_join_equivalence(self):
        for pk_morph_1, pk_morph_2, lv_morph in PK_JOINS:
            kwargs = {
                "ident": "",
                "definition": "",
                "category": KasanicStemCategory.UNINFLECTED,
                "mstype": MorphosyntacticType.INDEPENDENT,
                "forms": {},
            }
            pk_lemma_1 = ProtoKasanicLemma(generic_morph=pk_morph_1, **kwargs)
            pk_lemma_2 = ProtoKasanicLemma(generic_morph=pk_morph_2, **kwargs)

            lv_morph_1 = LauvinkoLemma.from_pk(pk_lemma_1).citation_form(MorphemeContext.PREFIXED)
            lv_morph_2 = LauvinkoLemma.from_pk(pk_lemma_2).citation_form(MorphemeContext.NONAUGMENTED)

            joined_pk_form = ProtoKasanicMorpheme.join(
                [
                    pk_lemma_1.citation_form().main_morpheme,
                    pk_lemma_2.citation_form().main_morpheme,
                ],
                stressed=1
            )

            joined_then_evolved = ProtoKasanicOrigin.evolve_surface_form(
                joined_pk_form,
                context=MorphemeContext.NONAUGMENTED,
            )

            self.assertEqual(
                joined_then_evolved.broad_transcription(),
                lv_morph.surface_form.broad_transcription(),
            )

            self.assertEqual(
                LauvinkoMorpheme.join([lv_morph_1, lv_morph_2], 1).surface_form.broad_transcription(),
                lv_morph.surface_form.broad_transcription(),
            )

    def test_join_equivalence(self):
        num_trials = 100000
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

            if joined_then_evolved.broad_transcription() != evolved_then_joined.broad_transcription():
                num_mismatched += 1

                if num_mismatched <= 50:
                    print(f"{pk_lemma_1.citation_form().main_morpheme.surface_form.broad_transcription()} and "
                          f"{pk_lemma_2.citation_form().main_morpheme.surface_form.broad_transcription()} became")
                    print(f"{joined_then_evolved.broad_transcription()} when evolved as a single word and")
                    print(f"{lv_form_1.surface_form.broad_transcription()} + "
                          f"{lv_form_2.surface_form.broad_transcription()} = "
                          f"{evolved_then_joined.broad_transcription()} when joined synchronically")
                    print()

            # self.assertEqual(
            #     pk_falavay(joined_pk_form, augment=augment),
            #     lv_form_1.falavay + lv_form_2.falavay,
            # )

        print(f"{num_mismatched}/{num_trials} words are different synchronically than diachronically")

    def test_clitic(self):
        for lv_morph_1, lv_morph_2, accented, expected_joined in CLITICS:
            def make_word(m: LauvinkoMorpheme):
                m.lemma = LauvinkoLemma("", "", KasanicStemCategory.UNINFLECTED, MorphosyntacticType.INDEPENDENT,
                                        {}, None)
                return LauvinkoContentWord([], None, None, None, stem=m)

            words = list(map(make_word, (lv_morph_1, lv_morph_2)))

            actual_joined = LauvinkoWord.cliticize(words, accented)

            self.assertEqual(actual_joined.broad_transcription(), expected_joined.surface_form.broad_transcription())

