import unittest
from lauvinko.lang.shared.semantics import KasanicStemCategory, PrimaryTenseAspect
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicLemma
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma
from lauvinko.lang.dictionary.entry import DictEntry


class DictEntryTests(unittest.TestCase):
    def test_pk_from_json(self):
        entry = DictEntry.from_json_entry(
            ident="foo",
            json_entry={
                "origin": "kasanic",
                "category": "fientive",
                "languages": {
                    "pk": {
                        "definition": "bar",
                        "forms": {
                            "gn": "s~kko",
                            "impt": "poro",
                        }
                    },
                    "lv": {
                        "definition": "baz",
                        "forms": {
                            "inc.na": "se/yo",
                        },
                    },
                },
            },
        )

        pk_lemma: ProtoKasanicLemma = entry.languages["pk"]
        lv_lemma: LauvinkoLemma = entry.languages["lv"]

        self.assertEqual(entry.ident, "foo")
        self.assertIs(entry.category, KasanicStemCategory.FIENTIVE)
        self.assertEqual(pk_lemma.definition, "bar")
        self.assertEqual(lv_lemma.definition, "baz")

        self.assertEqual(
            pk_lemma.form(PrimaryTenseAspect.INCEPTIVE).surface_form().narrow_transcription(),
            "i.ˈsə.ˀko",
        )

        self.assertEqual(
            pk_lemma.form(PrimaryTenseAspect.IMPERFECTIVE_PAST).surface_form().narrow_transcription(),
            "ˈpo.ro",
        )

        self.assertEqual(
            lv_lemma.form(PrimaryTenseAspect.PERFECTIVE, augment=False).surface_form().narrow_transcription(),
            "sɪ́ʔ",
        )

        self.assertEqual(
            lv_lemma.form(PrimaryTenseAspect.IMPERFECTIVE_PAST, augment=False).surface_form().narrow_transcription(),
            "pʊ̂ɽ",
        )

        self.assertEqual(
            lv_lemma.form(PrimaryTenseAspect.INCEPTIVE, augment=False).surface_form().narrow_transcription(),
            "séːjʊ",
        )
