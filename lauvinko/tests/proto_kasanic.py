import unittest

from lauvinko.lang.pk_phonology import (
    ProtoKasanicOnset,
    ProtoKasanicVowel,
    ProtoKasanicMutation, ProtoKasanicSyllable,
)
from lauvinko.lang.pk_morphology import pkm, ProtoKasanicMorpheme


class ProtoKasanicTests(unittest.TestCase):
    def test_phonemes(self):
        m = pkm("siruwai+N")
        self.assertIs(m.syllables[1].onset, ProtoKasanicOnset.R)
        self.assertIs(m.syllables[2].vowel, ProtoKasanicVowel.AI)

        m = pkm("kwaasa")
        self.assertIs(m.syllables[0].vowel, ProtoKasanicVowel.AA)
        self.assertIs(m.syllables[1].vowel, ProtoKasanicVowel.A)

        m = pkm("tt@+L")
        self.assertIs(m.syllables[0].onset, ProtoKasanicOnset.TT)
        self.assertIs(m.syllables[0].vowel, ProtoKasanicVowel.LOW)

        m = pkm("ngw~")
        self.assertIs(m.syllables[0].onset, ProtoKasanicOnset.NGW)
        self.assertIs(m.syllables[0].vowel, ProtoKasanicVowel.HIGH)

        m = pkm("a'a")
        self.assertIs(m.syllables[0].onset, None)
        self.assertIs(m.syllables[1].onset, None)

    def test_mutation_parsing(self):
        m = pkm("ma+L")
        self.assertIs(m.end_mutation, ProtoKasanicMutation.LENITION)

        m = pkm("sitaimo+F")
        self.assertIs(m.end_mutation, ProtoKasanicMutation.FORTITION)

        m = pkm("rauwaso+N")
        self.assertIs(m.end_mutation, ProtoKasanicMutation.NASALIZATION)

    def test_zero_morpheme(self):
        m = pkm("")
        assert m.syllables == []
        assert m.end_mutation is None

        m = pkm("+F")
        assert m.syllables == []
        assert m.end_mutation is ProtoKasanicMutation.FORTITION

    def test_invalid_transcriptions(self):
        invalids = ["mmo", "mii", "ssu", "roi", "laala", "va", "umti", "ba", "da", "ga", "anwa", "ap"]

        for t in invalids:
            with self.assertRaises(ProtoKasanicMorpheme.InvalidTranscription):
                pkm(t)

    def test_invalid_morphemes(self):
        with self.assertRaises(ProtoKasanicSyllable.InvalidSyllable) as e:
            pkm("wuri")

        self.assertEqual(str(e.exception), "wu")

        with self.assertRaises(ProtoKasanicSyllable.InvalidSyllable) as e:
            pkm("ruyi")

        self.assertEqual(str(e.exception), "yi")

        with self.assertRaises(ProtoKasanicSyllable.InvalidSyllable):
            pkm("war@")

    def test_mutations(self):
        mutations = [
            ("a+F", "sa",   "aca"),
            ("a+F", "ta",   "atta"),
            ("a+F", "cca",  "acca"),
            ("a+F", "nkwa", "ankwa"),
            ("a+F", "ra",   "ara"),

            ("a+L", "ha",   "aha"),
            ("a+L", "pa",   "awa"),
            ("a+L", "kkwa", "akwa"),
            ("a+L", "mpa",  "ama"),
            ("a+L", "nga",  "anga"),

            ("a+N", "sa",   "asa"),
            ("a+N", "ca",   "anca"),
            ("a+N", "ppa",  "appa"),
            ("a+N", "nta",  "anta"),
            ("a+N", "ngwa", "angwa"),
            ("a+N", "ra",   "ana"),
            ("a+N", "ya",   "anya"),
            ("a+N", "wa",   "angwa"),
        ]

        for m1, m2, joined in mutations:
            sf = ProtoKasanicMorpheme.join(
                [pkm(m1), pkm(m2)],
                0,
            )

            self.assertEqual(sf, pkm(joined).surface_form())

