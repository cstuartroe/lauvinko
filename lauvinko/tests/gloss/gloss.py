from typing import List, Tuple
from unittest import TestCase

from lauvinko.lang.shared.semantics import Language
from lauvinko.lang.gloss.gloss import Gloss

TESTS: List[Tuple[str, List[str], List[str], List[str], List[str]]] = [
    # ("see.impt.na", "jôj.ŋa", "jʊ̂jŋɐ", "eyohqXga", "yòynga"),
    (
        "if-want-$pro$-$t1s$-$tgen$-cross.$fqnp$.$na$",
        ["ti.je.ʋon.pi.na.pa.nek.kék.ŋi"],
        ["tɪjɛʋʊmpɪnɐpɐnɛkːɛ́ɦŋɪ"],
        ["HtqXEvMpinpenHekqHkZgi"],
        ["tiyevompinapanekkéhngi"],
    ),
    (
        "before-$t3as$-$tage$-pull.$inc$.$na$",
        ["ta.ʋin.pét"],
        ["tɐʋɪmpɛ́ʔ"],
        ["HtZIMpkqXta"],
        ["tavimpéh"],
    ),
]


class GlossingTests(TestCase):
    def test_broad_transcriptions(self):
        for source, broad_transcription, _, _, _ in TESTS:
            gloss = Gloss.parse(source, language=Language.LAUVINKO)

            self.assertEqual(
                gloss.broad_transcription(),
                broad_transcription,
            )

    def test_narrow_transcriptions(self):
        for source, _, narrow_transcription, _, _ in TESTS:
            gloss = Gloss.parse(source, language=Language.LAUVINKO)

            self.assertEqual(
                gloss.narrow_transcription(),
                narrow_transcription,
            )

    def test_falavay(self):
        for source, _, _, falavay, _ in TESTS:
            gloss = Gloss.parse(source, language=Language.LAUVINKO)

            self.assertEqual(
                gloss.falavay(),
                falavay,
            )

    def test_romanization(self):
        for source, _, _, _, romanization in TESTS:
            gloss = Gloss.parse(source, language=Language.LAUVINKO)

            self.assertEqual(
                gloss.romanization(),
                romanization,
            )
