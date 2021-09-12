import unittest

from lauvinko.lang.shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from lauvinko.lang.shared.morphology import Lemma
from lauvinko.lang.proto_kasanic.morphology import (
    pkm,
    ProtoKasanicStem,
    ProtoKasanicLemma,
    AblautMismatch,
    PKModalPrefix,
    PKTertiaryAspectPrefix,
    PKTopicAgreementPrefix,
    PKTopicCasePrefix,
    PKWord,
)


class ProtoKasanicMorphologyTests(unittest.TestCase):
    def test_fientive_form_generation(self):
        lemma = ProtoKasanicLemma(
            definition="",
            category=KasanicStemCategory.FIENTIVE,
            generic_morph=pkm("t~ru"),
            forms={},
        )

        form_inc: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.INCEPTIVE)
        self.assertEqual(form_inc.surface_form(), pkm("intaru").surface_form(1))

        form_fqnp: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.FREQUENTATIVE_NONPAST)
        self.assertEqual(form_fqnp.surface_form(), pkm("titiru").surface_form(1))

        with self.assertRaises(lemma.NonexistentForm):
            lemma.form(PrimaryTenseAspect.GENERAL)

    def test_punctual_form_generation(self):
        lemma = ProtoKasanicLemma(
            definition="",
            category=KasanicStemCategory.PUNCTUAL,
            generic_morph=pkm("kk@"),
            forms={},
        )

        form_np: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.NONPAST)
        self.assertEqual(form_np.surface_form(), pkm("kke").surface_form())

        form_fqpt: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.FREQUENTATIVE_PAST)
        self.assertEqual(form_fqpt.surface_form(), pkm("kkokko").surface_form(1))

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
            definition="",
            category=KasanicStemCategory.FIENTIVE,
            generic_morph=pkm("t@"),
            forms={
                PrimaryTenseAspect.IMPERFECTIVE_NONPAST: ProtoKasanicStem(
                    primary_prefix=None,
                    main_morpheme=pkm("tai"),
                ),
            }
        )

        form_impt: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.IMPERFECTIVE_PAST)
        self.assertEqual(form_impt.surface_form(), pkm("to").surface_form())

        form_imnp: ProtoKasanicStem = lemma.form(PrimaryTenseAspect.IMPERFECTIVE_NONPAST)
        self.assertEqual(form_imnp.surface_form(), pkm("tai").surface_form())

        with self.assertRaises(Lemma.NonexistentForm):
            ProtoKasanicLemma(
                definition="",
                category=KasanicStemCategory.FIENTIVE,
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
                definition="",
                category=KasanicStemCategory.FIENTIVE,
                generic_morph=pkm("ta"),
                forms={}
            )

        with self.assertRaises(AblautMismatch):
            ProtoKasanicLemma(
                definition="",
                category=KasanicStemCategory.STATIVE,
                generic_morph=pkm("t@"),
                forms={}
            )

    def test_bucket_prefixes(self):
        bucketed = PKWord.bucket_prefixes([
            PKModalPrefix.AFTER,
            PKModalPrefix.SWRF_,
            PKTertiaryAspectPrefix.PRO_,
            PKTopicAgreementPrefix.T3AP_,
            PKTopicCasePrefix.TDAT_,
        ])

        self.assertEqual(bucketed, {
            "modal_prefixes": [PKModalPrefix.AFTER, PKModalPrefix.SWRF_],
            "tertiary_aspect": PKTertiaryAspectPrefix.PRO_,
            "topic_agreement": PKTopicAgreementPrefix.T3AP_,
            "topic_case": PKTopicCasePrefix.TDAT_,
        })

        bucketed = PKWord.bucket_prefixes([
            PKModalPrefix.IF,
            PKTopicAgreementPrefix.T1S_,
        ])

        self.assertEqual(bucketed, {
            "modal_prefixes": [PKModalPrefix.IF],
            "tertiary_aspect": None,
            "topic_agreement": PKTopicAgreementPrefix.T1S_,
            "topic_case": None,
        })

        with self.assertRaises(PKWord.MorphemeOrderError):
            PKWord.bucket_prefixes([PKTopicCasePrefix.DEP_, PKTopicAgreementPrefix.T3IS_])

        with self.assertRaises(PKWord.MorphemeOrderError):
            PKWord.bucket_prefixes([PKTertiaryAspectPrefix.EXP_, PKModalPrefix.MUST])

    def test_gloss_keyword(self):
        self.assertEqual(PKTopicAgreementPrefix.T2P_.gloss_keyname(), "$t2p$")
