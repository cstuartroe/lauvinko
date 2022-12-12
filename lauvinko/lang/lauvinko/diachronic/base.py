from dataclasses import dataclass
from typing import Optional
from enum import Enum
from lauvinko.lang.lauvinko.phonology import LauvinkoSurfaceForm
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicMorpheme
from lauvinko.lang.shared.semantics import PrimaryTenseAspect


class MorphemeContext(Enum):
    AUGMENTED = "AUGMENTED"
    NONAUGMENTED = "NONAUGMENTED"
    PREFIXED = "PREFIXED"


class OriginLanguage(Enum):
    KASANIC = ("kasanic", "pk")
    MALAY = ("malay", "ms")
    JAVANESE = ("javanese", "jv")
    SANSKRIT = ("sanskrit", "sa")
    TAMIL = ("tamil", "ta")
    ARABIC = ("arabic", "ar")
    HOKKIEN = ("hokkien", "hk")
    PORTUGUESE = ("portuguese", "pt")
    DUTCH = ("dutch", "nl")
    ENGLISH = ("english", "en")


class LauvinkoLemmaOrigin:
    def generate_form(self, primary_ta: PrimaryTenseAspect, context: MorphemeContext) \
            -> tuple[LauvinkoSurfaceForm, ProtoKasanicMorpheme]:
        raise NotImplementedError

    def language_and_word(self) -> tuple[OriginLanguage, Optional[str]]:
        raise NotImplementedError

    class InvalidOrigin(ValueError):
        pass


class UnspecifiedOrigin(LauvinkoLemmaOrigin):
    def generate_form(self, primary_ta: PrimaryTenseAspect, context: MorphemeContext):
        raise LauvinkoLemmaOrigin.InvalidOrigin(
            f"A lemma with unspecified origin must have all forms explicitly specified "
            f"(missing {primary_ta} {context})"
        )

    def language_and_word(self) -> tuple[OriginLanguage, Optional[str]]:
        return OriginLanguage.KASANIC, None

@dataclass
class GenericOrigin(LauvinkoLemmaOrigin):
    origin_language: OriginLanguage
    origin_word: str

    def generate_form(self, primary_ta: PrimaryTenseAspect, context: MorphemeContext):
        raise LauvinkoLemmaOrigin.InvalidOrigin(
            f"A lemma with generic origin must have all forms explicitly specified "
            f"(missing {primary_ta} {context})"
        )

    def language_and_word(self) -> Optional[tuple[OriginLanguage, str]]:
        return self.origin_language, self.origin_word

    @classmethod
    def from_json(cls, origin_language: OriginLanguage, languages_json: dict) -> "GenericOrigin":
        return cls(
            origin_language=origin_language,
            origin_word=languages_json[origin_language.value[1]]["native"]
        )
