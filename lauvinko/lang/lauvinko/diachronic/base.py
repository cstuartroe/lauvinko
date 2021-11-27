from enum import Enum
from lauvinko.lang.lauvinko.phonology import LauvinkoSurfaceForm
from lauvinko.lang.proto_kasanic.phonology import (
    ProtoKasanicOnset,
    ProtoKasanicVowel,
    ProtoKasanicMutation,
)
from lauvinko.lang.shared.semantics import PrimaryTenseAspect


class MorphemeContext(Enum):
    AUGMENTED = "AUGMENTED"
    NONAUGMENTED = "NONAUGMENTED"
    PREFIXED = "PREFIXED"


class LauvinkoLemmaOrigin:
    def generate_form(self, primary_ta: PrimaryTenseAspect, context: MorphemeContext) \
            -> tuple[LauvinkoSurfaceForm, ProtoKasanicOnset, ProtoKasanicVowel, ProtoKasanicMutation, str]:
        raise NotImplementedError

    class InvalidOrigin(ValueError):
        pass


class OriginLanguage(Enum):
    KASANIC = "kasanic"
    MALAY = "malay"
    SANSKRIT = "sanskrit"
    TAMIL = "tamil"
    ARABIC = "arabic"
    HOKKIEN = "hokkien"
    PORTUGUESE = "portuguese"
    DUTCH = "dutch"
    ENGLISH = "english"


class UnspecifiedOrigin(LauvinkoLemmaOrigin):
    def generate_form(self, primary_ta: PrimaryTenseAspect, context: MorphemeContext):
        raise LauvinkoLemmaOrigin.InvalidOrigin(
            "A lemma with unspecified origin must have all forms explicitly specified"
        )
