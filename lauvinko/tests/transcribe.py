import unittest

from lauvinko.lang.pk_morphology import pkm
from lauvinko.lang.transcribe import transcribe, falavay


TRANSCRIPTIONS = [
    ('maakina', 'makinə',  'maGkqXn',  'makqXn'),
    ("o'i",     'oi',      'OGI',      'OI'),
    ('ai',      'ai',      'YG',       'Y'),
    ('naatami', 'natəmi',  'naGtqmX',  'natqmX'),
    ("kukkuta", "ku'kutə", 'kZGHkZtq', 'kZHkZtq'),
    ('kanka',   'kəṅkə',   'kqGMkq',   'kqMkq'),
    ("ekkungi", "e'kuṅi",  'EGHkZgi',  'EHkZgi'),
    ('aakaaye', 'akaye',   'AGkaey',   'Akaey'),
    ('kwau',    'kvau',    'pWG',      'pW'),
]


class TranscriptionTests(unittest.TestCase):
    def test_transcription(self):
        for informal_transcription, transcription, augmented_falavay_spelling, falavay_spelling in TRANSCRIPTIONS:
            form = pkm(informal_transcription).surface_form()

            self.assertEqual(transcribe(form), transcription)
            self.assertEqual(falavay(form), falavay_spelling)
            self.assertEqual(falavay(form, augment=True), augmented_falavay_spelling)
