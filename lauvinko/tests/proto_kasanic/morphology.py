import unittest

from lauvinko.lang.shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from lauvinko.lang.shared.morphology import Lemma, MorphosyntacticType
from lauvinko.lang.proto_kasanic.morphology import (
    pkm,
    ProtoKasanicStem,
    ProtoKasanicLemma,
    AblautMismatch,
    PKWord,
)


class ProtoKasanicMorphologyTests(unittest.TestCase):
    def test_fientive_form_generation(self):
        lemma = ProtoKasanicLemma(
            ident="",
            definition="",
            category=KasanicStemCategory.FIENTIVE,
            mstype=MorphosyntacticType.INDEPENDENT,
            generic_morph=pkm("t~ru"),
            forms={},
        )

        form_inc: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.INCEPTIVE)
        self.assertEqual(form_inc.surface_form(), pkm("intaru", stress_position=1).surface_form)

        form_fqnp: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.FREQUENTATIVE_NONPAST)
        self.assertEqual(form_fqnp.surface_form(), pkm("titiru", stress_position=1).surface_form)

        with self.assertRaises(lemma.NonexistentForm):
            lemma.form(PrimaryTenseAspect.GENERAL)

    def test_punctual_form_generation(self):
        lemma = ProtoKasanicLemma(
            ident="",
            definition="",
            category=KasanicStemCategory.PUNCTUAL,
            mstype=MorphosyntacticType.INDEPENDENT,
            generic_morph=pkm("kk@"),
            forms={},
        )

        form_np: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.NONPAST)
        self.assertEqual(form_np.surface_form(), pkm("kke").surface_form)

        form_fqpt: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.FREQUENTATIVE_PAST)
        self.assertEqual(form_fqpt.surface_form(), pkm("kkokko", stress_position=1).surface_form)

        with self.assertRaises(lemma.NonexistentForm):
            lemma.form(PrimaryTenseAspect.INCEPTIVE)

        with self.assertRaises(lemma.NonexistentForm):
            lemma.form(PrimaryTenseAspect.GENERAL)

        with self.assertRaises(lemma.NonexistentForm):
            lemma.form(PrimaryTenseAspect.PERFECTIVE)

        with self.assertRaises(lemma.NonexistentForm):
            lemma.form(PrimaryTenseAspect.IMPERFECTIVE_NONPAST)

    def test_form_override(self):
        lemma = ProtoKasanicLemma(
            ident="",
            definition="",
            category=KasanicStemCategory.FIENTIVE,
            mstype=MorphosyntacticType.INDEPENDENT,
            generic_morph=pkm("t@"),
            forms={
                PrimaryTenseAspect.IMPERFECTIVE_NONPAST: ProtoKasanicStem(
                    primary_prefix=None,
                    main_morpheme=pkm("tai"),
                ),
            }
        )

        form_impt: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.IMPERFECTIVE_PAST)
        self.assertEqual(form_impt.surface_form(), pkm("to").surface_form)

        form_imnp: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.IMPERFECTIVE_NONPAST)
        self.assertEqual(form_imnp.surface_form(), pkm("tai").surface_form)

        with self.assertRaises(Lemma.NonexistentForm):
            ProtoKasanicLemma(
                ident="",
                definition="",
                category=KasanicStemCategory.FIENTIVE,
                mstype=MorphosyntacticType.INDEPENDENT,
                generic_morph=pkm("t@"),
                forms={
                    PrimaryTenseAspect.NONPAST: ProtoKasanicStem(
                        primary_prefix=None,
                        main_morpheme=pkm("tai"),
                    ),
                }
            ).form(PrimaryTenseAspect.NONPAST)

    def test_underspecified_vowels(self):
        with self.assertRaises(AblautMismatch):
            ProtoKasanicLemma(
                ident="",
                definition="",
                category=KasanicStemCategory.FIENTIVE,
                mstype=MorphosyntacticType.INDEPENDENT,
                generic_morph=pkm("ta"),
                forms={}
            )

        with self.assertRaises(AblautMismatch):
            ProtoKasanicLemma(
                ident="",
                definition="",
                category=KasanicStemCategory.STATIVE,
                mstype=MorphosyntacticType.INDEPENDENT,
                generic_morph=pkm("t@"),
                forms={}
            )
