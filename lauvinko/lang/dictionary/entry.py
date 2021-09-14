from dataclasses import dataclass

from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicMorpheme, ProtoKasanicStem, ProtoKasanicLemma
from lauvinko.lang.shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from lauvinko.lang.shared.morphology import Lemma
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma, LauvinkoMorpheme
from lauvinko.lang.lauvinko.diachronic.base import LauvinkoLemmaOrigin


ORIGIN_LANGUAGES = {
    "kasanic": (LauvinkoLemma.from_pk, "pk"),
}

STEM_CATEGORIES = {
    "fientive": KasanicStemCategory.FIENTIVE,
    "punctual": KasanicStemCategory.PUNCTUAL,
    "stative": KasanicStemCategory.STATIVE,
    "uninflected": KasanicStemCategory.UNINFLECTED,
}

PRIMARY_TA_ABBREVIATIONS = {
    "gn": PrimaryTenseAspect.GENERAL,
    "np": PrimaryTenseAspect.NONPAST,
    "pt": PrimaryTenseAspect.PAST,
    "imnp": PrimaryTenseAspect.IMPERFECTIVE_NONPAST,
    "impt": PrimaryTenseAspect.IMPERFECTIVE_PAST,
    "pf": PrimaryTenseAspect.PERFECTIVE,
    "inc": PrimaryTenseAspect.INCEPTIVE,
    "fqnp": PrimaryTenseAspect.FREQUENTATIVE_NONPAST,
    "fqpt": PrimaryTenseAspect.FREQUENTATIVE_PAST,
}


def parse_lv_form_id(form_id: str):
    pta, aug = form_id.split(".")
    if aug == "au":
        augment = True
    elif aug == "na":
        augment = False
    else:
        raise ValueError

    return PRIMARY_TA_ABBREVIATIONS[pta], augment


@dataclass
class DictEntry:
    languages: dict[str, Lemma]
    ident: str
    category: KasanicStemCategory

    @staticmethod
    def from_json_entry(ident: str, json_entry: dict):
        if json_entry["origin"] in ORIGIN_LANGUAGES:
            deriving_function, origin = ORIGIN_LANGUAGES[json_entry["origin"]]
        else:
            raise LauvinkoLemmaOrigin.InvalidOrigin("Invalid word origin: " + json_entry["origin"])

        if origin not in json_entry["languages"]:
            raise ValueError(f"Information for origin {repr(origin)} missing: entry id {ident}")

        if json_entry["category"] in STEM_CATEGORIES:
            category = STEM_CATEGORIES[json_entry["category"]]
        else:
            raise KasanicStemCategory.InvalidStemCategory("Invalid stem category: " + json_entry["category"])

        if origin == "pk":
            languages = DictEntry.languages_from_pk_json(json_entry["languages"], category=category)
        else:
            raise NotImplementedError

        assert languages["lv"].category is category

        return DictEntry(
            languages=languages,
            ident=ident,
            category=category,
        )

    @staticmethod
    def languages_from_pk_json(languages_json: dict, category: KasanicStemCategory):
        languages = {"pk": ProtoKasanicLemma(
            category=category,
            definition=languages_json["pk"]["definition"],
            generic_morph=ProtoKasanicMorpheme.from_informal_transcription(languages_json["pk"]["forms"]["gn"]),
            forms={
                PRIMARY_TA_ABBREVIATIONS[pta]: ProtoKasanicStem(
                    primary_prefix=None,
                    main_morpheme=ProtoKasanicMorpheme.from_informal_transcription(transcription)
                )
                for pta, transcription in languages_json["pk"]["forms"].items()
                if pta != "gn"
            }
        )}

        languages["lv"] = LauvinkoLemma.from_pk(
            pk_lemma=languages["pk"],
            definition=languages_json["lv"].get("definition"),
            forms={
                parse_lv_form_id(form_id): LauvinkoMorpheme.from_informal_transcription(transcription)
                for form_id, transcription in languages_json["lv"]["forms"].items()
            }
        )

        return languages
