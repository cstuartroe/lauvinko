import unittest

from lauvinko.lang.shared.semantics import KasanicStemCategory
from lauvinko.lang.proto_kasanic.generate import random_pk_lemma
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma


class PKGenerationTests(unittest.TestCase):
    def test_generation(self):
        for _ in range(10):
            pk_lemma = random_pk_lemma(KasanicStemCategory.UNINFLECTED)
            LauvinkoLemma.from_pk(pk_lemma)
