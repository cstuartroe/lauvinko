from dataclasses import dataclass
from typing import List, Optional
import re

from ..shared.semantics import PrimaryTenseAspect, PRIMARY_TA_ABBREVIATIONS, KasanicStemCategory, PTA2ABBREV
from ..shared.morphology import Morpheme, Word, MorphosyntacticType
from ..proto_kasanic.morphology import PKWord
from ..proto_kasanic.romanize import romanize as pk_romanize
from ..lauvinko.morphology import LauvinkoWord
from ..lauvinko.diachronic.base import MorphemeContext, OriginLanguage
from ..lauvinko.romanize import romanize as lv_romanize
from ..dictionary import Dictionary, Language
from ..dictionary.entry import parse_context


class InvalidGloss(ValueError):
    pass


MC_ABBREVS = {
    MorphemeContext.AUGMENTED: "$au$",
    MorphemeContext.NONAUGMENTED: "$na$",
    MorphemeContext.PREFIXED: "$prefix$",
}


def parse_gloss_tag(gloss_tag: str):
    return re.fullmatch("\\$([a-z]+)\\$", gloss_tag).group(1)


def normalize_word(word: str):
    m = re.search("([a-z\u0300\u0301]+)", word.lower())
    return m.group(0)


ACCENTLESS_TYPES = (
    MorphosyntacticType.MODAL_PREFIX,
    MorphosyntacticType.TERTIARY_ASPECT_PREFIX,
    MorphosyntacticType.TOPIC_AGREEMENT_PREFIX,
    MorphosyntacticType.TOPIC_CASE_PREFIX,
    MorphosyntacticType.ADPOSITION,
    MorphosyntacticType.PARTICLE,
)


PARTICLE_LINKS = {
    "$int$": "questions",
    "and:$st$": "conjunction",
    "and:$swrf$": "conjunction",
    "or": "conjunction",
}


@dataclass
class MorphemeSource:
    name: str
    primary_ta: Optional[PrimaryTenseAspect]
    context: Optional[MorphemeContext]
    language: Language

    def __post_init__(self):
        lemma = Dictionary.main_by_id(self.name)

        if lemma is None:
            raise InvalidGloss(f"No lemma with name {self.name}")

        if self.primary_ta is None:
            if lemma.category is not KasanicStemCategory.UNINFLECTED:
                raise InvalidGloss(f"Must include primary tense/aspect for {lemma.category.title} stem")

            self.primary_ta = PrimaryTenseAspect.GENERAL

        self.value = self.resolve()

    @classmethod
    def parse(cls, source: str, language: Language):
        pieces = source.split(".")

        if len(pieces) > 1 and pieces[1] in {"$sg$", "$du$", "$pl$"}:
            name = '.'.join(pieces[:2])
            i = 2
        else:
            name = pieces[0]
            i = 1

        if len(pieces) > i and parse_gloss_tag(pieces[i]) in PRIMARY_TA_ABBREVIATIONS:
            primary_ta = PRIMARY_TA_ABBREVIATIONS[parse_gloss_tag(pieces[i])]
            i += 1
        else:
            primary_ta = None

        if len(pieces) > i:
            context = parse_context(parse_gloss_tag(pieces[i]))
            i += 1
        else:
            context = None

        if len(pieces) > i:
            raise InvalidGloss(f"Too many pieces: {source}")

        return cls(
            name,
            primary_ta,
            context,
            language=language,
        )

    def resolve(self) -> Morpheme:
        if self.language is Language.LAUVINKO:
            return self.resolve_lauvinko()
        else:
            raise NotImplementedError

    def resolve_lauvinko(self) -> Morpheme:
        entry = Dictionary.main_by_id(self.name)
        lemma = entry.languages[Language.LAUVINKO]
        if self.context:
            context = self.context
        elif lemma.mstype in ACCENTLESS_TYPES:
            context = MorphemeContext.PREFIXED
        else:
            context = MorphemeContext.NONAUGMENTED
        return lemma.form(
            primary_ta=self.primary_ta,
            context=context,
        )

    def analysis(self, index: int):
        morpheme = self.resolve()
        if morpheme.lemma.mstype is MorphosyntacticType.INDEPENDENT:
            lang, _ = morpheme.lemma.origin.language_and_word()
            if lang is OriginLanguage.KASANIC:
                page = f"kasanic_dictionary?q=@{self.name}"
            else:
                page = f"loanword_dictionary?q=@{self.name}"
        elif morpheme.lemma.mstype is MorphosyntacticType.CLASS_WORD:
            page = "class"
        elif morpheme.lemma.mstype in (MorphosyntacticType.TOPIC_AGREEMENT_PREFIX, MorphosyntacticType.TOPIC_CASE_PREFIX):
            page = "trigger_agreement"
        elif morpheme.lemma.mstype is MorphosyntacticType.TERTIARY_ASPECT_PREFIX:
            page = "tertiary"
        elif morpheme.lemma.mstype is MorphosyntacticType.MODAL_PREFIX:
            page = "modals"
        elif morpheme.lemma.mstype is MorphosyntacticType.DEFINITE_MARKER:
            page = "partitive"
        elif morpheme.lemma.mstype is MorphosyntacticType.NUMBER_SUFFIX:
            page = "number_suffixes"
        elif morpheme.lemma.mstype is MorphosyntacticType.SEX_SUFFIX:
            page = "sex_suffix"
        elif morpheme.lemma.mstype is MorphosyntacticType.ADPOSITION:
            page = "applicatives" if index == 0 else "/cases"
        elif morpheme.lemma.mstype in (MorphosyntacticType.ADVERB, MorphosyntacticType.PARTICLE):
            page = PARTICLE_LINKS.get(morpheme.lemma.ident, "adverbs")
        else:
            raise ValueError

        out = [{
            "text": self.name,
            "link": "/" + page,
        }]

        if self.value.lemma.category is not KasanicStemCategory.UNINFLECTED:
            out += [
                ".",
                {
                    "text": f"${PTA2ABBREV[self.primary_ta]}$",
                    "link": "/primary",
                },
            ]

        if self.value.lemma.mstype in (MorphosyntacticType.INDEPENDENT, MorphosyntacticType.CLASS_WORD):
            out += [
                ".",
                {
                    "text": f"{MC_ABBREVS[self.context]}",
                    "link": "/augment",
                },
            ]

        return out


WORD_CLASSES = {
    Language.PK: PKWord,
    Language.LAUVINKO: LauvinkoWord,
}


@dataclass
class GlossSyntacticWord:
    morpheme_sources: List[MorphemeSource]
    word: Word
    language: Language

    @classmethod
    def parse(cls, source: str, language: Language):
        ms = [
            MorphemeSource.parse(s, language)
            for s in source.split("-")
        ]

        morphemes = [
            m.value
            for m in ms
        ]

        word = WORD_CLASSES[language].from_morphemes(morphemes)

        return cls(
            morpheme_sources=ms,
            word=word,
            language=language,
        )

    def analysis(self):
        out = []
        for i, ms in enumerate(self.morpheme_sources):
            if i > 0:
                out.append('-')

            out += ms.analysis(i)

        return out

    def falavay(self) -> str:
        return self.word.falavay()


@dataclass
class GlossPhonologicalWord:
    swords: List[GlossSyntacticWord]
    language: Language
    capitalize: bool
    front_matter: str
    back_matter: str

    def __post_init__(self):
        if self.language is Language.LAUVINKO:
            self.surface_form = LauvinkoWord.join_syntactic_words(
                words=[
                    sword.word
                    for sword in self.swords
                ],
            )
        else:
            raise NotImplementedError

    @classmethod
    def parse(cls, source: str, language: Language):
        front_matter = re.match("^[^a-zA-Z0-9$]*", source).group()
        back_matter = re.search("[^a-zA-Z0-9$]*$", source).group()

        source = source[len(front_matter):]
        if back_matter:
            source = source[:-len(back_matter)]

        first_letter = re.search("[a-zA-Z]", source).group()

        return cls(
            swords=[
                GlossSyntacticWord.parse(sword, language=language)
                for sword in source.lower().split("=")
            ],
            language=language,
            capitalize=first_letter.isupper(),
            front_matter=front_matter,
            back_matter=back_matter,
        )

    def analysis(self):
        out = []
        for i, sword in enumerate(self.swords):
            if i > 0:
                out.append("=")
            out += sword.analysis()
        return out

    def broad_transcription(self) -> str:
        return self.surface_form.broad_transcription()

    def narrow_transcription(self) -> str:
        return self.surface_form.narrow_transcription()

    def romanization(self) -> str:
        if self.language is Language.LAUVINKO:
            out = lv_romanize(self.surface_form)
        elif self.language is Language.PK:
            out = pk_romanize(self.surface_form)
        else:
            raise NotImplementedError

        if self.capitalize:
            out = out[0].upper() + out[1:]

        return self.front_matter + out + self.back_matter

    def falavay(self) -> str:
        return "".join(sword.falavay() for sword in self.swords)


@dataclass
class Gloss:
    pwords: List[GlossPhonologicalWord]
    language: Language

    @classmethod
    def parse(cls, source: str, language: Language):
        return cls(
            pwords=[
                GlossPhonologicalWord.parse(word, language=language)
                for word in source.split()
            ],
            language=language,
        )

    def analysis(self):
        return [pword.analysis() for pword in self.pwords]

    def broad_transcription(self) -> List[str]:
        return [pword.broad_transcription() for pword in self.pwords]

    def narrow_transcription(self) -> List[str]:
        return [pword.narrow_transcription() for pword in self.pwords]

    def romanization(self) -> List[str]:
        return [pword.romanization() for pword in self.pwords]

    def falavay(self) -> List[str]:
        return [pword.falavay() for pword in self.pwords]

    def as_json(self):
        return {
            "analysis": self.analysis(),
            "broad_transcription": self.broad_transcription(),
            "narrow_transcription": self.narrow_transcription(),
            "romanization": self.romanization(),
            "falavay": self.falavay(),
        }
