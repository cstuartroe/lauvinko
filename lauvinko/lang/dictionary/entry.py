from dataclasses import dataclass
from typing import Optional
import json
import mistletoe
from mistletoe.ast_renderer import ASTRenderer
from lauvinko.lang.shared.semantics import (
    PrimaryTenseAspect,
    PRIMARY_TA_ABBREVIATIONS,
    KasanicStemCategory,
    STEM_CATEGORIES,
    Language, PTA2ABBREV,
)
from lauvinko.lang.shared.morphology import Lemma, MorphosyntacticType
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicMorpheme, ProtoKasanicStem, ProtoKasanicLemma
from lauvinko.lang.lauvinko.phonology import LauvinkoSurfaceForm
from lauvinko.lang.lauvinko.morphology import LauvinkoLemma, LauvinkoMorpheme
from lauvinko.lang.lauvinko.diachronic.base import (
    LauvinkoLemmaOrigin,
    OriginLanguage,
    UnspecifiedOrigin,
    GenericOrigin,
    MorphemeContext,
)


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


CLOSED_CLASSES: set[MorphosyntacticType] = {
    MorphosyntacticType.MODAL_PREFIX,
    MorphosyntacticType.TERTIARY_ASPECT_PREFIX,
    MorphosyntacticType.TOPIC_AGREEMENT_PREFIX,
    MorphosyntacticType.TOPIC_CASE_PREFIX,
    MorphosyntacticType.ADPOSITION,
}


EARLY_LOAN_LANGUAGES = (OriginLanguage.KASANIC, OriginLanguage.SANSKRIT, OriginLanguage.MALAY)
RECENT_LOAN_LANGUAGES = (OriginLanguage.DUTCH, OriginLanguage.ARABIC, OriginLanguage.MALAY)


@dataclass
class DictEntry:
    languages: dict[Language, Lemma]
    ident: str
    category: KasanicStemCategory
    mstype: MorphosyntacticType
    origin: LauvinkoLemmaOrigin

    class MissingData(ValueError):
        pass

    # meant to produce json for the api, not meant to be the reverse of from_json_entry
    def to_json(self):
        languages = {}
        for language, lemma in self.languages.items():
            data = lemma.to_json()
            languages[language.value] = {
                **data,
                "definition": json.loads(mistletoe.markdown(data["definition"], renderer=ASTRenderer))
            }

        olang, oword = self.origin.language_and_word()

        return {
            "languages": languages,
            "citation_form": PTA2ABBREV[self.category.citation_form],
            "alphabetization": self.languages[Language.LAUVINKO].citation_form().virtual_original_form.surface_form.alphabetical_order(),
            "origin": {
                "language": olang.value[0],
                "word": oword,
            },
        }

    @staticmethod
    def from_json_entry(ident: str, json_entry: dict):
        try:
            origin_language: OriginLanguage = OriginLanguage[json_entry["origin"].swapcase()]
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

        if mstype in CLOSED_CLASSES:
            raise ValueError(f"{mstype} is a closed class")

        if Language.PK.value in json_entry["languages"]:
            assert origin_language in EARLY_LOAN_LANGUAGES # TODO: separately handle?
            languages = DictEntry.languages_from_pk_json(
                ident,
                json_entry["languages"],
                category=category,
                mstype=mstype,
                origin_language=origin_language,
            )

        elif origin_language is OriginLanguage.KASANIC:
            languages = DictEntry.languages_from_json_no_source(ident, json_entry["languages"],
                                                                category=category, mstype=mstype)

        else:
            assert category is KasanicStemCategory.UNINFLECTED
            assert mstype is MorphosyntacticType.INDEPENDENT
            # TODO Arabic needs its own treatment
            if origin_language not in RECENT_LOAN_LANGUAGES:
                raise ValueError(f"Language cannot loan word recently: {json_entry}")

            languages = DictEntry.languages_from_recent_loan(
                ident,
                json_entry["languages"],
                origin_language,
            )

        assert languages[Language.LAUVINKO].category is category

        return DictEntry(
            languages=languages,
            ident=ident,
            category=category,
            mstype=mstype,
            origin=languages[Language.LAUVINKO].origin,
        )

    @staticmethod
    def lv_forms_from_json(forms_json: dict) -> dict[tuple[PrimaryTenseAspect, MorphemeContext], LauvinkoMorpheme]:
        lv_forms = {}

        for form_id, form_json in forms_json.items():
            primary_ta, context = parse_lv_form_id(form_id)

            morpheme = LauvinkoMorpheme.from_informal_transcription(
                form_json["phonemic"],
            )
            morpheme.context = context

            if "falavay" in form_json:
                print("Warning: 'falavay' deprecated")

            elif "written_like" in form_json:
                print("Warning: 'written_like' deprecated")

            lv_forms[(primary_ta, context)] = morpheme

        return lv_forms

    @staticmethod
    def languages_from_pk_json(ident: str, languages_json: dict, category: KasanicStemCategory,
                               mstype: MorphosyntacticType, origin_language: OriginLanguage):
        ultimate_origin: Optional[LauvinkoLemmaOrigin] = None
        if origin_language is not OriginLanguage.KASANIC:
            ultimate_origin = GenericOrigin.from_json(origin_language, languages_json)

        pk_lemma = ProtoKasanicLemma(
            ident=ident,
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
            },
            origin=ultimate_origin,
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
    def languages_from_json_no_source(ident: str, languages_json: dict, category: KasanicStemCategory,
                                      mstype: MorphosyntacticType) -> dict[Language, Lemma]:
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
                ident=ident,
                definition=languages_json[Language.LAUVINKO.value]["definition"],
                category=category,
                mstype=mstype,
                forms=forms_given,
                origin=UnspecifiedOrigin(),
            )
        }

    @staticmethod
    def languages_from_recent_loan(ident: str, languages_json: dict, origin_language: OriginLanguage)\
            -> dict[Language, Lemma]:
        forms = languages_json[Language.LAUVINKO.value]["forms"]
        assert len(forms) == 1
        gn_form = LauvinkoMorpheme.from_informal_transcription(forms["gn"]["phonemic"])
        gn_form.context = MorphemeContext.AUGMENTED
        assert gn_form.surface_form.falling_accent is False

        return {
            Language.LAUVINKO: LauvinkoLemma(
                ident=ident,
                definition=languages_json[Language.LAUVINKO.value]["definition"],
                category=KasanicStemCategory.UNINFLECTED,
                mstype=MorphosyntacticType.INDEPENDENT,
                forms={
                    (PrimaryTenseAspect.GENERAL, MorphemeContext.AUGMENTED): gn_form,
                    (PrimaryTenseAspect.GENERAL, MorphemeContext.NONAUGMENTED): LauvinkoMorpheme(
                        lemma=gn_form.lemma,
                        context=MorphemeContext.NONAUGMENTED,
                        surface_form=LauvinkoSurfaceForm(
                            syllables=gn_form.surface_form.syllables,
                            accent_position=gn_form.surface_form.accent_position,
                            falling_accent=True,
                        ),
                        virtual_original_form=gn_form.virtual_original_form,
                    )
                },
                origin=GenericOrigin.from_json(origin_language, languages_json),
            )
        }


