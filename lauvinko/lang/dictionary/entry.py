from dataclasses import dataclass
import itertools
from lauvinko.lang.shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from lauvinko.lang.shared.morphology import Lemma
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicMorpheme, ProtoKasanicStem, ProtoKasanicLemma
from lauvinko.lang.proto_kasanic.transcribe import falavay as pk_falavay
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma, LauvinkoMorpheme
from lauvinko.lang.lauvinko.diachronic.base import LauvinkoLemmaOrigin, OriginLanguage, UnspecifiedOrigin


STEM_CATEGORIES = {
    category.name.lower(): category
    for category in KasanicStemCategory
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
    origin: OriginLanguage

    class MissingData(ValueError):
        pass

    @staticmethod
    def from_json_entry(ident: str, json_entry: dict):
        try:
            origin: OriginLanguage = OriginLanguage[json_entry["origin"].swapcase()]
        except KeyError:
            raise LauvinkoLemmaOrigin.InvalidOrigin(f"Invalid word origin: {repr(json_entry.get('origin'))}")

        if json_entry["category"] in STEM_CATEGORIES:
            category = STEM_CATEGORIES[json_entry["category"]]
        else:
            raise KasanicStemCategory.InvalidStemCategory("Invalid stem category: " + json_entry["category"])

        if origin is OriginLanguage.KASANIC:
            languages = DictEntry.languages_from_pk_json(json_entry["languages"], category=category)
        else:
            raise NotImplementedError

        assert languages["lv"].category is category

        return DictEntry(
            languages=languages,
            ident=ident,
            category=category,
            origin=origin,
        )

    @staticmethod
    def lv_forms_from_json(forms_json: dict) -> dict[tuple[PrimaryTenseAspect, bool], LauvinkoMorpheme]:
        lv_forms = {}

        for form_id, form_json in forms_json.items():
            primary_ta, augment = parse_lv_form_id(form_id)

            morpheme = LauvinkoMorpheme.from_informal_transcription(
                form_json["phonemic"],
            )

            if "falavay" in form_json:
                morpheme.falavay = form_json["falavay"]

            elif "written_like" in form_json:
                morpheme.falavay = pk_falavay(
                    ProtoKasanicMorpheme.from_informal_transcription(
                        form_json["written_like"]
                    ).surface_form(0)
                )

            lv_forms[(primary_ta, augment)] = morpheme

        return lv_forms


    @staticmethod
    def languages_from_pk_json(languages_json: dict, category: KasanicStemCategory):
        if "pk" not in languages_json:
            return DictEntry.languages_from_json_no_source(languages_json, category=category)

        pk_lemma = ProtoKasanicLemma(
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
        )

        languages = {"pk": pk_lemma}

        lv_definition = pk_lemma.definition
        lv_forms = {}

        if "lv" in languages_json:
            if "definition" in languages_json["lv"]:
                lv_definition = languages_json["lv"]["definition"]

            if "forms" in languages_json["lv"]:
                lv_forms = DictEntry.lv_forms_from_json(languages_json["lv"]["forms"])
                for (primary_ta, augment), form in lv_forms.items():
                    if form.falavay is None:
                        form.falavay = pk_falavay(pk_lemma.form(primary_ta).surface_form(), augment=augment)

        languages["lv"] = LauvinkoLemma.from_pk(
            pk_lemma=languages["pk"],
            definition=lv_definition,
            forms=lv_forms
        )

        return languages

    @staticmethod
    def languages_from_json_no_source(languages_json: dict, category: KasanicStemCategory):
        forms_given = DictEntry.lv_forms_from_json(languages_json["lv"]["forms"])

        if set(forms_given.keys()) != set(itertools.product(category.primary_aspects, [True, False])):
            raise DictEntry.MissingData("Not all forms given")

        return {
            "lv": LauvinkoLemma(
                category=category,
                definition=languages_json["lv"]["definition"],
                forms=forms_given,
                origin=UnspecifiedOrigin(),
            )
        }
