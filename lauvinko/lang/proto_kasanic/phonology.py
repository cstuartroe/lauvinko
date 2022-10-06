from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from lauvinko.lang.shared.phonology import (
    MannerOfArticulation,
    PlaceOfArticulation,
    Consonant,
    VowelFrontness,
    Vowel,
    Syllable,
    SurfaceForm,
)


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


class ProtoKasanicVowel(Vowel, Enum):
    AA = ('a', True, VowelFrontness.MID)
    E = ('e', True, VowelFrontness.FRONT)
    O = ('o', True, VowelFrontness.BACK)

    A = ('ə', False, VowelFrontness.MID)
    I = ('i', False, VowelFrontness.FRONT)
    U = ('u', False, VowelFrontness.BACK)

    AI = ('ai̯', True, VowelFrontness.FRONTING)
    AU = ('au̯', True, VowelFrontness.BACKING)

    LOW = ('A', True, VowelFrontness.UNDERSPECIFIED)
    HIGH = ('I', False, VowelFrontness.UNDERSPECIFIED)


@dataclass
class ProtoKasanicSyllable(Syllable):
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
        None: None,
        ProtoKasanicOnset.S: ProtoKasanicOnset.C,
        MannerOfArticulation.PLAIN_STOP: MannerOfArticulation.PREGLOTTALIZED_STOP,
    }

    LENITION = {
        None: None,

        ProtoKasanicOnset.P: ProtoKasanicOnset.W,
        ProtoKasanicOnset.T: ProtoKasanicOnset.R,
        ProtoKasanicOnset.C: ProtoKasanicOnset.S,
        ProtoKasanicOnset.K: ProtoKasanicOnset.H,
        ProtoKasanicOnset.KW: ProtoKasanicOnset.W,

        MannerOfArticulation.PRENASALIZED_STOP: MannerOfArticulation.NASAL,
        MannerOfArticulation.PREGLOTTALIZED_STOP: MannerOfArticulation.PLAIN_STOP,
    }

    NASALIZATION = {
        None: ProtoKasanicOnset.N,

        MannerOfArticulation.APPROXIMANT: MannerOfArticulation.NASAL,
        MannerOfArticulation.PLAIN_STOP: MannerOfArticulation.PRENASALIZED_STOP,
    }

    def mutate(self, c: Optional[ProtoKasanicOnset]) -> ProtoKasanicOnset:
        if c in self.value:
            return self.value[c]

        if c.moa in self.value:
            out = ProtoKasanicOnset.find_by(c.poa, self.value[c.moa])
            if out is not None:
                return out

        return c


@dataclass
class PKSurfaceForm(SurfaceForm):
    """Stress position must be None if len(syllables) is 0"""
    syllables: List[ProtoKasanicSyllable]
    stress_position: Optional[int]
    validated: bool = False

    class InvalidStress(ValueError):
        pass

    def __post_init__(self):
        if self.stress_position is not None and self.stress_position >= len(self.syllables):
            if not self.validated and self.stress_position == 0:
                pass  # This is an edge case that's permitted
            else:
                raise PKSurfaceForm.InvalidStress

        for syllable in self.syllables[1:]:
            if syllable.vowel.frontness is VowelFrontness.UNDERSPECIFIED:
                raise ProtoKasanicSyllable.InvalidSyllable(f"Non-initial vowel is underspecified: {self.syllables}")

    def broad_transcription(self) -> str:
        syllables_ipa = []

        for i, syllable in enumerate(self.syllables):
            stress = "ˈ" if i == self.stress_position else ''

            syllables_ipa.append(f"{stress}{getattr(syllable.onset, 'ipa', '')}{syllable.vowel.ipa}")

        return '.'.join(syllables_ipa)

    def narrow_transcription(self) -> str:
        return self.broad_transcription()  # This is a protolang, who needs narrow transcription lol
