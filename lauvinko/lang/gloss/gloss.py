from dataclasses import dataclass
from typing import List, Optional

from ..shared.semantics import PrimaryTenseAspect, PRIMARY_TA_ABBREVIATIONS
from ..shared.morphology import Morpheme, Word
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


@dataclass
class MorphemeSource:
    name: str
    primary_ta: Optional[PrimaryTenseAspect]
    context: Optional[MorphemeContext]

    @classmethod
    def parse(cls, source: str):
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
        )

    def resolve(self, language: Language) -> Morpheme:
        if language is Language.LAUVINKO:
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
            MorphemeSource.parse(s)
            for s in source.split("-")
        ]

        morphemes = [
            m.resolve(language)
            for m in ms
        ]

        word = WORD_CLASSES[language].from_morphemes(morphemes)

        return cls(
            morpheme_sources=ms,
            word=word,
            language=language,
        )

    def analysis(self) -> str:
        return "-".join(str(ms) for ms in self.morpheme_sources)

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
        return "".join(
            m.falavay
            for m in self.word.morphemes()
        )


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

    def analysis(self) -> str:
        return " ".join(pword.analysis() for pword in self.pwords)

    def broad_transcription(self) -> str:
        return " ".join(pword.broad_transcription() for pword in self.pwords)

    def narrow_transcription(self) -> str:
        return " ".join(pword.narrow_transcription() for pword in self.pwords)

    def romanization(self) -> str:
        return " ".join(pword.romanization() for pword in self.pwords)

    def falavay(self) -> str:
        return "".join(pword.falavay() for pword in self.pwords)
