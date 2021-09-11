from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from abc import ABC


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
    """Subclasses should also subclass Enum, and represent the consonant inventory of a particular language"""

    poa: PlaceOfArticulation
    moa: MannerOfArticulation

    @classmethod
    def find_by(cls, poa: PlaceOfArticulation, moa: MannerOfArticulation) -> Optional["cls"]:
        """Finds a consonant with given poa and moa within a particular inventory"""
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
    """Subclasses should also subclass Enum, and represent the vowel inventory of a particular language"""

    low: bool
    frontness: VowelFrontness

    @classmethod
    def shift_height(cls, vowel: "cls", low: bool) -> "cls":
        """Finds a vowel of same height and given frontness within a particular inventory"""
        for v in list(cls):
            if v.low == low and v.frontness == vowel.frontness:
                return v

        return vowel

    def __hash__(self):
        return hash(f"{self.ipa}{self.low}{self.frontness}")


@dataclass
class Syllable(ABC):
    pass


@dataclass
class SurfaceForm(ABC):
    syllables: List[Syllable]
    stress_position: Optional[int]

    def broad_transcription(self) -> str:
        raise NotImplementedError

    def narrow_transcription(self) -> str:
        raise NotImplementedError
