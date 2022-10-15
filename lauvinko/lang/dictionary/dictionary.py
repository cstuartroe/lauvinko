import json

from lauvinko.lang.lauvinko.morphology import LauvinkoLemma, LauvinkoCase
from lauvinko.lang.shared.morphology import MorphosyntacticType
from lauvinko.lang.shared.semantics import KasanicStemCategory, Language
from lauvinko.lang.proto_kasanic.morphology import pkm, ProtoKasanicLemma
from lauvinko.lang.lauvinko.diachronic.base import OriginLanguage
from lauvinko.lang.dictionary.entry import DictEntry

MODAL_PREFIXES = {
    "if": "tti+L",
    "in_order": "ki+L",
    "thus": "iwo+F",
    "after": "ngi",
    "$swrf$": "o+N",
    "after:$swrf$": "nyo+N",
    "not": "aara",
    "again": "tere",
    "want": "ewa",
    "like": "mika",
    "can": "so+N",
    "must": "nosa+L",
    "very": "kora",
    "but": "caa",
}


TERTIARY_ASPECT_PREFIXES = {
    "pro": "mpi",
    "exp": "raa+F",
}


TOPIC_AGREEMENT_PREFIXES = {
    "t1s": "na",
    "t1p": "ta",
    "t2s": "i+F",
    "t2p": "e+F",
    "t3as": "",
    "t3ap": "aa",
    "t3is": "sa",
    "t3ip": "aasa",
}


TOPIC_CASE_PREFIXES = {
    "tvol": "",
    "tdat": "pa+N",
    "tloc": "posa",
    "dep": "eta",
}

ADPOSITIONS = [
    (LauvinkoCase.VOLITIVE, "maa"),
    (LauvinkoCase.INSTRUMENTAL, "oka"),
    (LauvinkoCase.PATIENTIVE, ""),
    (LauvinkoCase.DATIVE, "ni"),
    (LauvinkoCase.ALLATIVE, "ai"),
    (LauvinkoCase.LOCATIVE, "po"),
    (LauvinkoCase.ABLATIVE, "aapo"),
    (LauvinkoCase.PERLATIVE, "moko"),
    (LauvinkoCase.PARTITIVE, "e"),

    ("and", "naa"),
]

DICTIONARY_FILENAME = "lauvinko/lang/dictionary.json"


class Dictionary:
    def __init__(self, entries: dict[str, DictEntry]):
        self.entries = entries
        self.fill_in_closed_classes()

    def by_id(self, ident: str) -> DictEntry:
        return self.entries.get(ident)

    def where(self, f):
        return Dictionary({
            ident: entry
            for ident, entry in self.entries.items()
            if f(entry)
        })

    @classmethod
    def from_file(cls, filename=DICTIONARY_FILENAME):
        with open(filename, "r") as fh:
            entries_dict = json.load(fh)

        entries = {
            ident: DictEntry.from_json_entry(ident=ident, json_entry=json_entry)
            for ident, json_entry in entries_dict.items()
            if json_entry["origin"] in ["kasanic", "sanskrit"]  # TODO support other languages
        }

        return cls(entries)

    def fill_in_closed_classes(self):
        self.fill_in_prefix_set(
            MODAL_PREFIXES,
            MorphosyntacticType.MODAL_PREFIX,
            wrap_ident=False,
        )
        self.fill_in_prefix_set(
            TERTIARY_ASPECT_PREFIXES,
            MorphosyntacticType.TERTIARY_ASPECT_PREFIX,
        )
        self.fill_in_prefix_set(
            TOPIC_AGREEMENT_PREFIXES,
            MorphosyntacticType.TOPIC_AGREEMENT_PREFIX,
        )
        self.fill_in_prefix_set(
            TOPIC_CASE_PREFIXES,
            MorphosyntacticType.TOPIC_CASE_PREFIX,
        )

        self.fill_in_adpositions()

    def fill_in_prefix_set(self, prefix_set: dict[str, str], mstype: MorphosyntacticType, wrap_ident: bool = True):
        for ident, informal_transcription in prefix_set.items():
            if wrap_ident:
                ident = f"${ident}$"

            pk_lemma = ProtoKasanicLemma(
                ident=ident,
                definition="",
                category=KasanicStemCategory.UNINFLECTED,
                mstype=mstype,
                forms={},
                generic_morph=pkm(informal_transcription)
            )

            lv_lemma = LauvinkoLemma.from_pk(pk_lemma)

            self.entries[ident] = DictEntry(
                languages={
                    Language.PK: pk_lemma,
                    Language.LAUVINKO: lv_lemma,
                },
                ident=ident,
                category=KasanicStemCategory.UNINFLECTED,
                mstype=mstype,
                origin=OriginLanguage.KASANIC
            )

    def fill_in_adpositions(self):
        for case, informal_transcription in ADPOSITIONS:
            if isinstance(case, str):
                ident = case
                definition = case.title() + "."
            else:
                ident = f"${case.abbreviation}$"
                definition = f"{case.name.title()} adposition"

            pk_lemma = ProtoKasanicLemma(
                ident=ident,
                definition=definition,
                category=KasanicStemCategory.UNINFLECTED,
                mstype=MorphosyntacticType.ADPOSITION,
                forms={},
                generic_morph=pkm(informal_transcription),
            )

            lv_lemma = LauvinkoLemma.from_pk(pk_lemma)

            self.entries[ident] = DictEntry(
                languages={
                    Language.PK: pk_lemma,
                    Language.LAUVINKO: lv_lemma,
                },
                ident=ident,
                category=KasanicStemCategory.UNINFLECTED,
                mstype=MorphosyntacticType.ADPOSITION,
                origin=OriginLanguage.KASANIC,
            )

    def to_json(self):
        return {
            ident: entry.to_json()
            for ident, entry in self.entries.items()
            if entry.mstype is MorphosyntacticType.INDEPENDENT
        }
