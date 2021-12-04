from dataclasses import dataclass
from lauvinko.lang.shared.semantics import (
    PrimaryTenseAspect,
    PRIMARY_TA_ABBREVIATIONS,
    KasanicStemCategory,
    STEM_CATEGORIES,
    Language, PTA2ABBREV,
)
from lauvinko.lang.shared.morphology import Lemma, MorphosyntacticType
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicMorpheme, ProtoKasanicStem, ProtoKasanicLemma
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma, LauvinkoMorpheme
from lauvinko.lang.lauvinko.diachronic.base import LauvinkoLemmaOrigin, OriginLanguage, UnspecifiedOrigin, \
    MorphemeContext


def parse_context(s) -> MorphemeContext:
    if s == "au":
        return MorphemeContext.AUGMENTED
    elif s == "na":
        return MorphemeContext.NONAUGMENTED
    elif s == "prefix":
        return MorphemeContext.PREFIXED
    else:
        raise ValueError


def parse_lv_form_id(form_id: str):
    pta, con = form_id.split(".")

    return PRIMARY_TA_ABBREVIATIONS[pta], parse_context(con)


@dataclass
class DictEntry:
    languages: dict[Language, Lemma]
    ident: str
    category: KasanicStemCategory
    mstype: MorphosyntacticType
    origin: OriginLanguage

    class MissingData(ValueError):
        pass

    # meant to produce json for the api, not meant to be the reverse of from_json_entry
    def to_json(self):
        languages = {
            language.value: lemma.to_json()
            for language, lemma in self.languages.items()
        }

        return {
            "languages": languages,
            "citation_form": PTA2ABBREV[self.category.citation_form],
            "alphabetization": None,
            "origin": self.origin.value,
        }

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

        mstype_name = json_entry.get("mstype", "independent").upper().replace(' ', '_')

        if mstype_name not in MorphosyntacticType.__members__:
            raise MorphosyntacticType.InvalidMSType(f"Invalid morphosyntactic type: {mstype_name}")

        mstype = MorphosyntacticType[mstype_name]

        if origin is OriginLanguage.KASANIC or origin is OriginLanguage.SANSKRIT:  # TODO: separately handle sanskrit
            languages = DictEntry.languages_from_pk_json(json_entry["languages"], category=category, mstype=mstype)
        else:
            raise NotImplementedError

        assert languages[Language.LAUVINKO].category is category

        return DictEntry(
            languages=languages,
            ident=ident,
            category=category,
            mstype=mstype,
            origin=origin,
        )

    @staticmethod
    def lv_forms_from_json(forms_json: dict) -> dict[tuple[PrimaryTenseAspect, MorphemeContext], LauvinkoMorpheme]:
        lv_forms = {}

        for form_id, form_json in forms_json.items():
            primary_ta, context = parse_lv_form_id(form_id)

            morpheme = LauvinkoMorpheme.from_informal_transcription(
                form_json["phonemic"],
            )

            if "falavay" in form_json:
                print("Warning: 'falavay' deprecated")

            elif "written_like" in form_json:
                print("Warning: 'written_like deprecated'")

            lv_forms[(primary_ta, context)] = morpheme

        return lv_forms


    @staticmethod
    def languages_from_pk_json(languages_json: dict, category: KasanicStemCategory, mstype: MorphosyntacticType):
        if Language.PK.value not in languages_json:
            return DictEntry.languages_from_json_no_source(languages_json, category=category, mstype=mstype)

        pk_lemma = ProtoKasanicLemma(
            definition=languages_json[Language.PK.value]["definition"],
            category=category,
            mstype=mstype,
            generic_morph=ProtoKasanicMorpheme.from_informal_transcription(languages_json[Language.PK.value]["forms"]["gn"]),
            forms={
                PRIMARY_TA_ABBREVIATIONS[pta]: ProtoKasanicStem(
                    primary_prefix=None,
                    main_morpheme=ProtoKasanicMorpheme.from_informal_transcription(transcription)
                )
                for pta, transcription in languages_json[Language.PK.value]["forms"].items()
                if pta != "gn"
            }
        )

        languages = {Language.PK: pk_lemma}

        lv_definition = pk_lemma.definition
        lv_forms = {}

        if Language.LAUVINKO.value in languages_json:
            if "definition" in languages_json[Language.LAUVINKO.value]:
                lv_definition = languages_json[Language.LAUVINKO.value]["definition"]

            if "forms" in languages_json[Language.LAUVINKO.value]:
                lv_forms = DictEntry.lv_forms_from_json(languages_json[Language.LAUVINKO.value]["forms"])

        languages[Language.LAUVINKO] = LauvinkoLemma.from_pk(
            pk_lemma=languages[Language.PK],
            definition=lv_definition,
            forms=lv_forms
        )

        return languages

    @staticmethod
    def languages_from_json_no_source(languages_json: dict, category: KasanicStemCategory, mstype: MorphosyntacticType)\
            -> dict[Language, Lemma]:
        forms_given = DictEntry.lv_forms_from_json(languages_json[Language.LAUVINKO.value]["forms"])

        expected_forms = {
            (pta, context)
            for pta in category.primary_aspects
            for context in MorphemeContext
            if context is not MorphemeContext.PREFIXED  # TODO is this a good assumption?
        }

        if set(forms_given.keys()) != expected_forms:
            raise DictEntry.MissingData("Not all forms given")

        return {
            Language.LAUVINKO: LauvinkoLemma(
                definition=languages_json[Language.LAUVINKO.value]["definition"],
                category=category,
                mstype=mstype,
                forms=forms_given,
                origin=UnspecifiedOrigin(),
            )
        }
