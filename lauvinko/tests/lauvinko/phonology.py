import unittest

from lauvinko.lang.proto_kasanic.phonology import ProtoKasanicOnset, ProtoKasanicMutation
from lauvinko.lang.lauvinko.morphology import LauvinkoMorpheme


lm = LauvinkoMorpheme.from_informal_transcription


TESTS: list[tuple[LauvinkoMorpheme, str, str, str, ProtoKasanicOnset, ProtoKasanicMutation]] = [
    (lm("se\\anor+F"), 'sêɐ̯.nol', 'sêɐ̯.nol', 'sɛ̂ɐ̯nʊɽ', ProtoKasanicOnset.S, ProtoKasanicMutation.FORTITION),
    (lm("nca/ye+L"), 'an.t͡sá.je', 'an.t͡sá.je', 'ɐnt͡sɑ́ːjɪ', ProtoKasanicOnset.NC, ProtoKasanicMutation.LENITION),
    (lm('ttayno+N'), 'taj.no', 'taj.no', 'tɐjnʊ', ProtoKasanicOnset.TT, ProtoKasanicMutation.NASALIZATION),
    (lm('socya\\ng+N'), 'sot͡s.jâŋ', 'sot͡s.jân', 'sʊtt͡ɕɐ̂ŋ', ProtoKasanicOnset.S, ProtoKasanicMutation.NASALIZATION),
    (lm('voh'), 'ʋok', 'ʋoh', 'ʋʊʔ', ProtoKasanicOnset.W, None),
    (lm('lahma'), 'lak.ma', 'lah.ma', 'lɐɦmɐ', ProtoKasanicOnset.R, None),
    (lm('allo/'), 'al.ló', 'al.ló', 'ɐɭɭóː', None, None),
    (lm('arna'), 'al.na', 'al.na', 'ɐɳɳɐ', None, None),
    (lm('apsa'), 'ap.sa', 'ah.sa', 'ɐssɐ', None, None),
    (lm('acca'), 'at͡s.t͡sa', 'at͡s.t͡sa', 'ɐst͡sɐ', None, None),
    (lm('apca'), 'ap.t͡sa', 'ah.t͡sa', 'ɐtt͡sɐ', None, None),
    (lm('acta'), 'at͡s.ta', 'at͡s.ta', 'ɐstɐ', None, None),
]


class LauvinkoPhonologyTests(unittest.TestCase):
    def test_historical_transcription(self):
        for morpheme, historical_transcription, _, _, _, _ in TESTS:
            self.assertEqual(
                morpheme.surface_form.historical_transcription(),
                historical_transcription,
            )

    def test_broad_transcription(self):
        for morpheme, _, broad_transcription, _, _, _ in TESTS:
            self.assertEqual(
                morpheme.surface_form.broad_transcription(),
                broad_transcription,
            )

    def test_narrow_transcription(self):
        for morpheme, _, _, narrow_transcription, _, _ in TESTS:
            self.assertEqual(
                morpheme.surface_form.narrow_transcription(),
                narrow_transcription,
            )

    def test_original_initial(self):
        for morpheme, _, _, _, original_initial_consonant, _ in TESTS:
            self.assertIs(
                morpheme.original_initial_consonant(),
                original_initial_consonant,
            )

    def test_mutation_parsing(self):
        for morpheme, _, _, _, _, mutation in TESTS:
            self.assertIs(
                morpheme.virtual_original_form.end_mutation,
                mutation,
            )
