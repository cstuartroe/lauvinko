from dataclasses import dataclass
from typing import List, Optional
from ..shared.morphology import Morpheme
from ..proto_kasanic.phonology import ProtoKasanicOnset, ProtoKasanicMutation
from .phonology import (
    LauvinkoSyllable,
    LauvinkoSurfaceForm,
)
from .diachronic.from_transcription import TranscriptionReader


@dataclass
class LauvinkoMorpheme(Morpheme):
    """One of the complexities of LauvinkoMorpheme is that LauvinkoMorpheme.join needs to maintain equivalence with
    historical change. For this reason, it needs to maintain original_initial_consonant and end_mutation
    so that mutations can be retroactively applied.
    """
    syllables: List[LauvinkoSyllable]
    accent_position: Optional[int]
    falling_accent: bool
    original_initial_consonant: Optional[ProtoKasanicOnset]
    end_mutation: Optional[ProtoKasanicMutation]
    falavay: str

    class InvalidAccent(ValueError):
        pass

    def __post_init__(self):
        if self.accent_position is not None and self.accent_position >= len(self.syllables):
            raise LauvinkoMorpheme.InvalidAccent("Accent in invalid position")

    def surface_form(self) -> LauvinkoSurfaceForm:
        return LauvinkoSurfaceForm(
            syllables=self.syllables,
            accent_position=self.accent_position,
            falling_accent=self.falling_accent,
        )

    @classmethod
    def from_informal_transcription(cls, transcription: str) -> "LauvinkoMorpheme":
        return cls(*cls._from_informal_transcription(transcription))

    @staticmethod
    def _from_informal_transcription(transcription: str):
        sf, oic, mut = TranscriptionReader(transcription).read()
        return (
            sf.syllables,
            sf.accent_position,
            sf.falling_accent,
            oic,
            mut,
            None,
        )

    @staticmethod
    def join(morphemes: List["LauvinkoMorpheme"], accented: Optional[int]) -> LauvinkoSurfaceForm:
        pass
