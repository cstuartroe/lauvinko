from dataclasses import dataclass
from typing import List, Optional

from ..shared.semantics import PrimaryTenseAspect, PRIMARY_TA_ABBREVIATIONS, KasanicStemCategory, PTA2ABBREV
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
    MorphemeContext.AUGMENTED: "au",
    MorphemeContext.NONAUGMENTED: "na",
    MorphemeContext.PREFIXED: "prefix",
}


@dataclass
class MorphemeSource:
    name: str
    primary_ta: Optional[PrimaryTenseAspect]
    context: Optional[MorphemeContext]
    language: Language

    def __post_init__(self):
        self.value = self.resolve()

    @classmethod
    def parse(cls, source: str, language: Language):
        pieces = source.split(".")

        name = pieces[0]

        if len(pieces) > 1:
            primary_ta = PRIMARY_TA_ABBREVIATIONS[pieces[1]]
        else:
            primary_ta = None

        if len(pieces) > 2:
            context = parse_context(pieces[2])
        else:
            context = None

        if len(pieces) > 3:
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
        primary_ta = self.primary_ta or PrimaryTenseAspect.GENERAL
        context = self.context or MorphemeContext.PREFIXED
        return lemma.form(
            primary_ta=primary_ta,
            context=context,
        )

    def as_str(self):
        out = self.name

        if self.value.lemma.category is not KasanicStemCategory.UNINFLECTED:
            out += f".${PTA2ABBREV[self.primary_ta]}$"

        if self.value.lemma.mstype is MorphosyntacticType.INDEPENDENT:
            out += f".${MC_ABBREVS[self.context]}$"

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

    def broad_transcription(self) -> str:
        sf = self.word.surface_form()

        if self.language is Language.LAUVINKO:
            return sf.historical_transcription()
        else:
            return sf.broad_transcription()

    def narrow_transcription(self) -> str:
        return self.word.surface_form().narrow_transcription()

    def romanization(self) -> str:
        sf = self.word.surface_form()

        if self.language is Language.LAUVINKO:
            return lv_romanize(sf)
        elif self.language is Language.PK:
            return pk_romanize(sf)
        else:
            raise NotImplementedError

    def falavay(self) -> str:
        return self.word.falavay()


@dataclass
class GlossPhonologicalWord:
    swords: List[GlossSyntacticWord]
    language: Language

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
        return "".join(sword.broad_transcription() for sword in self.swords)

    def narrow_transcription(self) -> str:
        return "".join(sword.narrow_transcription() for sword in self.swords)

    def romanization(self) -> str:
        return "".join(sword.romanization() for sword in self.swords)

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
