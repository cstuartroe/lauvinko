import unittest

from lauvinko.lang.lauvinko.diachronic.base import MorphemeContext
from lauvinko.lang.shared.semantics import KasanicStemCategory, PrimaryTenseAspect
from lauvinko.lang.proto_kasanic.generate import random_pk_lemma
from lauvinko.lang.proto_kasanic.transcribe import transcribe as pk_transcribe
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma
from lauvinko.lang.lauvinko.transcribe import transcribe as lv_transcribe


class PKGenerationTests(unittest.TestCase):
    def test_generation(self):
        for _ in range(10):
            pk_lemma = random_pk_lemma(KasanicStemCategory.UNINFLECTED)
            lv_lemma = LauvinkoLemma.from_pk(pk_lemma)

            print(
                pk_transcribe(pk_lemma.form(PrimaryTenseAspect.GENERAL).surface_form()),
                lv_transcribe(lv_lemma.form(PrimaryTenseAspect.GENERAL, context=MorphemeContext.AUGMENTED).surface_form()),
                lv_transcribe(lv_lemma.form(PrimaryTenseAspect.GENERAL, context=MorphemeContext.NONAUGMENTED).surface_form()),
            )
