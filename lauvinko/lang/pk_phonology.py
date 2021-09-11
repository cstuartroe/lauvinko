from dataclasses import dataclass
from enum import Enum
from typing import Optional, List


@dataclass
class Phoneme:
    ipa: str


class PlaceOfArticulation(str, Enum):
    LABIAL = "labial"
    ALVEOLAR = "alveolar"
    PALATAL = "palatal"
    VELAR = "velar"
    LABIOVELAR = "labiovelar"
    GLOTTAL = "glottal"


class MannerOfArticulation(str, Enum):
    NASAL = "nasal"
    PLAIN_STOP = "stop"
    PRENASALIZED_STOP = "prenasalized stop"
    PREGLOTTALIZED_STOP = "preglottalized stop"
    FRICATIVE = "fricative"
    APPROXIMANT = "approximant"


@dataclass
class Consonant(Phoneme):
    poa: PlaceOfArticulation
    moa: MannerOfArticulation


class ProtoKasanicOnset(Consonant, Enum):
    M = ("m", PlaceOfArticulation.LABIAL, MannerOfArticulation.NASAL)
    N = ("n", PlaceOfArticulation.ALVEOLAR, MannerOfArticulation.NASAL)
    NY = ("ɲ", PlaceOfArticulation.PALATAL, MannerOfArticulation.NASAL)
    NG = ("ŋ", PlaceOfArticulation.VELAR, MannerOfArticulation.NASAL)
    NGW = ("ŋʷ", PlaceOfArticulation.LABIOVELAR, MannerOfArticulation.NASAL)

    P = ("p", PlaceOfArticulation.LABIAL, MannerOfArticulation.PLAIN_STOP)
    T = ("t", PlaceOfArticulation.ALVEOLAR, MannerOfArticulation.PLAIN_STOP)
    C = ("t͡ɕ", PlaceOfArticulation.PALATAL, MannerOfArticulation.PLAIN_STOP)
    K = ("k", PlaceOfArticulation.VELAR, MannerOfArticulation.PLAIN_STOP)
    KW = ("kʷ", PlaceOfArticulation.LABIOVELAR, MannerOfArticulation.PLAIN_STOP)

    MP = ("ᵐp", PlaceOfArticulation.LABIAL, MannerOfArticulation.PRENASALIZED_STOP)
    NT = ("ⁿt", PlaceOfArticulation.ALVEOLAR, MannerOfArticulation.PRENASALIZED_STOP)
    NC = ("ᶮt͡ɕ", PlaceOfArticulation.PALATAL, MannerOfArticulation.PRENASALIZED_STOP)
    NK = ("ᵑk", PlaceOfArticulation.VELAR, MannerOfArticulation.PRENASALIZED_STOP)
    NKW = ("ᵑkʷ", PlaceOfArticulation.LABIOVELAR, MannerOfArticulation.PRENASALIZED_STOP)

    PP = ("ˀp", PlaceOfArticulation.LABIAL, MannerOfArticulation.PREGLOTTALIZED_STOP)
    TT = ("ˀt", PlaceOfArticulation.ALVEOLAR, MannerOfArticulation.PREGLOTTALIZED_STOP)
    CC = ("ˀt͡ɕ", PlaceOfArticulation.PALATAL, MannerOfArticulation.PREGLOTTALIZED_STOP)
    KK = ("ˀk", PlaceOfArticulation.VELAR, MannerOfArticulation.PREGLOTTALIZED_STOP)
    KKW = ("ˀkʷ", PlaceOfArticulation.LABIOVELAR, MannerOfArticulation.PREGLOTTALIZED_STOP)

    S = ("s", PlaceOfArticulation.ALVEOLAR, MannerOfArticulation.FRICATIVE)
    H = ("h", PlaceOfArticulation.GLOTTAL, MannerOfArticulation.FRICATIVE)

    R = ("r", PlaceOfArticulation.ALVEOLAR, MannerOfArticulation.APPROXIMANT)
    Y = ("j", PlaceOfArticulation.PALATAL, MannerOfArticulation.APPROXIMANT)
    W = ("w", PlaceOfArticulation.LABIOVELAR, MannerOfArticulation.APPROXIMANT)

    @classmethod
    def find_by(cls, poa: PlaceOfArticulation, moa: MannerOfArticulation) -> Optional["ProtoKasanicOnset"]:
        for c in list(cls):
            if c.poa == poa and c.moa == moa:
                return c

        return None

    def __hash__(self):
        return hash(f"{self.ipa}{self.poa}{self.moa}")


class VowelFrontness(str, Enum):
    FRONT = "front"
    MID = "mid"
    BACK = "back"
    FRONTING = "fronting"
    BACKING = "backing"
    UNDERSPECIFIED = "underspecified"


@dataclass
class Vowel(Phoneme):
    low: bool
    frontness: VowelFrontness


class ProtoKasanicVowel(Vowel, Enum):
    AA = ('a', True, VowelFrontness.MID)
    E = ('e', True, VowelFrontness.FRONT)
    O = ('o', True, VowelFrontness.BACK)

    A = ('ɘ', False, VowelFrontness.MID)
    I = ('i', False, VowelFrontness.FRONT)
    U = ('u', False, VowelFrontness.BACK)

    AI = ('ai̯', True, VowelFrontness.FRONTING)
    AU = ('au̯', True, VowelFrontness.BACKING)

    LOW = ('A', True, VowelFrontness.UNDERSPECIFIED)
    HIGH = ('I', False, VowelFrontness.UNDERSPECIFIED)

    @classmethod
    def shift_height(cls, vowel: "ProtoKasanicVowel", low: bool) -> "ProtoKasanicVowel":
        for v in list(cls):
            if v.low == low and v.frontness == vowel.frontness:
                return v

        return vowel

    def __hash__(self):
        return hash(f"{self.ipa}{self.low}{self.frontness}")


@dataclass
class ProtoKasanicSyllable:
    onset: Optional[ProtoKasanicOnset]
    vowel: ProtoKasanicVowel

    class InvalidSyllable(ValueError):
        pass

    def __post_init__(self):
        if self.onset is ProtoKasanicOnset.W and self.vowel is ProtoKasanicVowel.U:
            raise ProtoKasanicSyllable.InvalidSyllable("wu")

        if self.onset is ProtoKasanicOnset.Y and self.vowel is ProtoKasanicVowel.I:
            raise ProtoKasanicSyllable.InvalidSyllable("yi")


class ProtoKasanicMutation(Enum):
    FORTITION = {
        ProtoKasanicOnset.S: ProtoKasanicOnset.C,
        MannerOfArticulation.PLAIN_STOP: MannerOfArticulation.PREGLOTTALIZED_STOP,
    }

    LENITION = {
        ProtoKasanicOnset.P: ProtoKasanicOnset.W,
        ProtoKasanicOnset.T: ProtoKasanicOnset.R,
        ProtoKasanicOnset.C: ProtoKasanicOnset.S,
        ProtoKasanicOnset.K: ProtoKasanicOnset.H,
        ProtoKasanicOnset.KW: ProtoKasanicOnset.W,

        MannerOfArticulation.PRENASALIZED_STOP: MannerOfArticulation.NASAL,
        MannerOfArticulation.PREGLOTTALIZED_STOP: MannerOfArticulation.PLAIN_STOP,
    }

    NASALIZATION = {
        MannerOfArticulation.APPROXIMANT: MannerOfArticulation.NASAL,
        MannerOfArticulation.PLAIN_STOP: MannerOfArticulation.PRENASALIZED_STOP,
    }

    def mutate(self, c: ProtoKasanicOnset) -> ProtoKasanicOnset:
        if c in self.value:
            return self.value[c]

        if c.moa in self.value:
            out = ProtoKasanicOnset.find_by(c.poa, self.value[c.moa])
            if out is not None:
                return out

        return c


@dataclass
class PKSurfaceForm:
    syllables: List[ProtoKasanicSyllable]
    stress_position: int
