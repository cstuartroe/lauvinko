import unittest

from lauvinko.lang.proto_kasanic.phonology import ProtoKasanicOnset, ProtoKasanicMutation
from lauvinko.lang.lauvinko.morphology import LauvinkoMorpheme


lm = LauvinkoMorpheme.from_informal_transcription


TESTS: list[tuple[LauvinkoMorpheme, str, str, ProtoKasanicOnset, ProtoKasanicMutation]] = [
    (lm("se\\anor+F"), 'sêɐ̯.nol', 'sɛ̂ɐ̯nʊɽ', ProtoKasanicOnset.S, ProtoKasanicMutation.FORTITION),
    (lm("nca/ye+L"), 'an.t͡sá.je', 'ɐnt͡sɑ́ːjɛ', ProtoKasanicOnset.NC, ProtoKasanicMutation.LENITION),
    (lm('ttayno+N'), 'taj.no', 'tɐjnʊ', ProtoKasanicOnset.TT, ProtoKasanicMutation.NASALIZATION),
    (lm('socya\\ng+N'), 'sot͡s.jâŋ', 'sʊtː͡ɕɐ̂ŋ', ProtoKasanicOnset.S, ProtoKasanicMutation.NASALIZATION),
    (lm('voh'), 'ʋok', 'ʋʊʔ', ProtoKasanicOnset.W, None),
    (lm('lahma'), 'lak.ma', 'lɐɦmɐ', ProtoKasanicOnset.R, None),
    (lm('allo/'), 'al.ló', 'ɐɭːóː', None, None),
    (lm('arna'), 'al.na', 'ɐɳːɐ', None, None),
    (lm('apsa'), 'ap.sa', 'ɐsːɐ', None, None),
    (lm('acca'), 'at͡s.t͡sa', 'ɐst͡sɐ', None, None),
    (lm('apca'), 'ap.t͡sa', 'ɐtː͡sɐ', None, None),
    (lm('acta'), 'at͡s.ta', 'ɐstɐ', None, None),
]


class LauvinkoPhonologyTests(unittest.TestCase):
    def test_broad_transcription(self):
        for morpheme, broad_transcription, _, _, _ in TESTS:
            self.assertEqual(
                morpheme.surface_form.broad_transcription(),
                broad_transcription,
            )

    def test_narrow_transcription(self):
        for morpheme, _, narrow_transcription, _, _ in TESTS:
            self.assertEqual(
                morpheme.surface_form.narrow_transcription(),
                narrow_transcription,
            )

    def test_original_initial(self):
        for morpheme, _, _, original_initial_consonant, _ in TESTS:
            self.assertIs(
                morpheme.original_initial_consonant(),
                original_initial_consonant,
            )

    def test_mutation_parsing(self):
        for morpheme, _, _, _, mutation in TESTS:
            self.assertIs(
                morpheme.virtual_original_form.end_mutation,
                mutation,
            )
