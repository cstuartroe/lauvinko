from dataclasses import dataclass
from typing import List, Optional
import re

from ..shared.semantics import PrimaryTenseAspect, PRIMARY_TA_ABBREVIATIONS, KasanicStemCategory
from ..shared.morphology import Morpheme, Word, MorphosyntacticType
from ..proto_kasanic.morphology import PKWord
from ..proto_kasanic.romanize import romanize as pk_romanize
from ..lauvinko.morphology import LauvinkoWord
from ..lauvinko.diachronic.base import MorphemeContext
from ..lauvinko.romanize import romanize as lv_romanize
from ..dictionary import Dictionary, Language
from ..dictionary.entry import parse_context

dictionary = Dictionary.from_file()


class InvalidGloss(ValueError):
    pass


MC_ABBREVS = {
    MorphemeContext.AUGMENTED: "$au$",
    MorphemeContext.NONAUGMENTED: "$na$",
    MorphemeContext.PREFIXED: "$prefix$",
}


PTA2ABBREV = {
    f"${value}$": key
    for key, value in PRIMARY_TA_ABBREVIATIONS.items()
}


@dataclass
class MorphemeSource:
    name: str
    primary_ta: Optional[PrimaryTenseAspect]
    context: Optional[MorphemeContext]
    language: Language

    def __post_init__(self):
        if self.primary_ta is None:
            lemma = dictionary.by_id(self.name)
            if lemma.category is not KasanicStemCategory.UNINFLECTED:
                raise InvalidGloss(f"Must include primary tense/aspect for {lemma.category.title} stem")
            self.primary_ta = PrimaryTenseAspect.GENERAL

        self.value = self.resolve()

    @classmethod
    def parse(cls, source: str, language: Language):
        pieces = source.split(".")

        name = pieces[0]

        i = 1

        if len(pieces) > i and pieces[i] in PRIMARY_TA_ABBREVIATIONS:
            primary_ta = PRIMARY_TA_ABBREVIATIONS[pieces[i]]
            i += 1
        else:
            primary_ta = None

        if len(pieces) > i:
            context = parse_context(re.fullmatch("\\$([a-z]+)\\$", pieces[i]).group(1))
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
        entry = dictionary.by_id(self.name)
        lemma = entry.languages[Language.LAUVINKO]
        context = self.context or MorphemeContext.PREFIXED
        return lemma.form(
            primary_ta=self.primary_ta,
            context=context,
        )

    def as_str(self):
        out = self.name

        if self.value.lemma.category is not KasanicStemCategory.UNINFLECTED:
            out += f".{PTA2ABBREV[self.primary_ta]}"

        if self.value.lemma.mstype is MorphosyntacticType.INDEPENDENT:
            out += f".{MC_ABBREVS[self.context]}"

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

    def analysis(self) -> str:
        return "-".join(ms.as_str() for ms in self.morpheme_sources)

    def falavay(self) -> str:
        return self.word.falavay()


@dataclass
class GlossPhonologicalWord:
    swords: List[GlossSyntacticWord]
    language: Language

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
        return cls(
            swords=[
                GlossSyntacticWord.parse(sword, language=language)
                for sword in source.split("=")
            ],
            language=language,
        )

    def analysis(self) -> str:
        return "=".join(sword.analysis() for sword in self.swords)

    def broad_transcription(self) -> str:
        if self.language is Language.LAUVINKO:
            return self.surface_form.historical_transcription()
        else:
            return self.surface_form.broad_transcription()

    def narrow_transcription(self) -> str:
        return self.surface_form.narrow_transcription()

    def romanization(self) -> str:
        if self.language is Language.LAUVINKO:
            return lv_romanize(self.surface_form)
        elif self.language is Language.PK:
            return pk_romanize(self.surface_form)
        else:
            raise NotImplementedError

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

    def analysis(self) -> List[str]:
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
