from enum import Enum
from lauvinko.lang.lauvinko.phonology import LauvinkoSurfaceForm
from lauvinko.lang.proto_kasanic.phonology import ProtoKasanicOnset, ProtoKasanicMutation, PKSurfaceForm
from lauvinko.lang.shared.semantics import PrimaryTenseAspect


class LauvinkoLemmaOrigin:
    def generate_form(self, primary_ta: PrimaryTenseAspect, augment: bool) \
            -> tuple[LauvinkoSurfaceForm, ProtoKasanicOnset, ProtoKasanicMutation, str]:
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
    def generate_form(self, primary_ta: PrimaryTenseAspect, augment: bool):
        raise LauvinkoLemmaOrigin.InvalidOrigin(
            "A lemma with unspecified origin must have all forms explicitly specified"
        )
