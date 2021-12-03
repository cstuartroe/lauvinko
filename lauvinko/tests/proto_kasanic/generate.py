import unittest

from lauvinko.lang.shared.semantics import KasanicStemCategory
from lauvinko.lang.proto_kasanic.generate import random_pk_lemma
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma
from lauvinko.lang.lauvinko.romanize import romanize as lv_romanize


class PKGenerationTests(unittest.TestCase):
    def test_generation(self):
        for _ in range(10):
            pk_lemma = random_pk_lemma(KasanicStemCategory.UNINFLECTED)
            # print(pk_lemma.generic_morph.surface_form)
            lv_lemma = LauvinkoLemma.from_pk(pk_lemma)
            # print(lv_romanize(lv_lemma.citation_form().surface_form))
