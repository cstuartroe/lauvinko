from dataclasses import dataclass
from typing import List, Optional
from ..shared.morphology import Morpheme
from ..proto_kasanic.phonology import ProtoKasanicOnset, ProtoKasanicMutation
from ..proto_kasanic.morphology import MUTATION_NOTATION
from .phonology import (
    LauvinkoConsonant,
    LauvinkoVowel,
    LauvinkoSyllable,
    LauvinkoSurfaceForm,
)
from .diachronic import PK_TO_LV_ONSETS


INFORMAL_PK_ONSETS = {
    **{c.name.lower(): c for c in ProtoKasanicOnset},
    'v': ProtoKasanicOnset.W,
    'l': ProtoKasanicOnset.R,
}


INFORMAL_LV_CONSONANTS = {
    **{c.name.lower(): c for c in LauvinkoConsonant},
    'r': LauvinkoConsonant.L,
    'u': LauvinkoConsonant.V,
    'h': LauvinkoConsonant.K,
}


INFORMAL_LV_VOWELS = {
    v.name.lower(): v
    for v in LauvinkoVowel
}


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
    augmented: bool
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

    class InvalidTranscription(ValueError):
        pass

    @classmethod
    def from_informal_transcription(cls, transcription: str) -> "LauvinkoMorpheme":
        return cls(*cls._from_informal_transcription(transcription))

    @staticmethod
    def _from_informal_transcription(transcription: str):
        """This method is somewhat spaghetti"""
        if len(transcription) >= 2 and transcription[-2:] in MUTATION_NOTATION:
            end_mutation = MUTATION_NOTATION[transcription[-2:]]
            transcription = transcription[:-2]
        else:
            end_mutation = None

        accent_position = None
        falling_accent = None

        original_initial_consonant, onset, i, syllables = LauvinkoMorpheme.initialize_transcription_read(transcription)

        current_position = "pre-vowel"

        def push_vowel():
            nonlocal i, onset, current_position
            vowel = INFORMAL_LV_VOWELS[transcription[i]]
            syllables.append(LauvinkoSyllable(onset=onset, vowel=vowel, coda=None))
            onset = None
            current_position = "post-vowel"
            i += 1

        while i < len(transcription):
            if current_position == "pre-vowel":
                if transcription[i] in INFORMAL_LV_VOWELS:
                    push_vowel()

                else:
                    raise LauvinkoMorpheme.InvalidTranscription(f"Expecting vowel at position {i} of {transcription}")

            elif current_position == "post-vowel":
                if (i < len(transcription) - 1) and transcription[i:i+2] in INFORMAL_LV_CONSONANTS:
                    c_str = transcription[i:i+2]
                elif transcription[i] in INFORMAL_LV_CONSONANTS:
                    c_str = transcription[i]
                elif transcription[i] in "/\\":
                    if accent_position is not None:
                        raise LauvinkoMorpheme.InvalidTranscription(f"More than one accented syllable in {transcription}")

                    accent_position = len(syllables) - 1
                    falling_accent = transcription[i] == '\\'
                    i += 1
                    continue
                else:
                    raise LauvinkoMorpheme.InvalidTranscription(f"Expecting consonant at position {i} of {transcription}")

                onset = INFORMAL_LV_CONSONANTS[c_str]
                current_position = "post-consonant"
                i += len(c_str)

            elif current_position == "post-consonant":
                if (i < len(transcription) - 1) and transcription[i:i+2] in INFORMAL_LV_CONSONANTS:
                    c_str = transcription[i:i+2]
                elif transcription[i] in INFORMAL_LV_CONSONANTS and transcription[i] != 'a':
                    c_str = transcription[i]
                elif transcription[i] in INFORMAL_LV_VOWELS:
                    push_vowel()
                    continue
                else:
                    raise LauvinkoMorpheme.InvalidTranscription(f"Unidentifiable character: {transcription[i]}")

                syllables[-1].coda = onset
                onset = INFORMAL_LV_CONSONANTS[c_str]
                current_position = "pre-vowel"
                i += len(c_str)

        if current_position == "pre-vowel":
            raise LauvinkoMorpheme.InvalidTranscription(f"Ends with two consonants: {transcription}")
        elif current_position == "post-consonant":
            syllables[-1].coda = onset

        return (
            syllables,
            accent_position,
            falling_accent,
            original_initial_consonant,
            end_mutation,
            None,
            None,
        )


    @staticmethod
    def initialize_transcription_read(transcription: str) \
            -> tuple[ProtoKasanicOnset, LauvinkoConsonant, int, list[LauvinkoSyllable]]:
        syllables = []

        if transcription[:2] in INFORMAL_PK_ONSETS:
            original_initial_consonant = INFORMAL_PK_ONSETS[transcription[:2]]

            if original_initial_consonant is ProtoKasanicOnset.NC:
                syllables.append(LauvinkoSyllable(
                    onset=None,
                    vowel=LauvinkoVowel.A,
                    coda=LauvinkoConsonant.N,
                ))
                first_onset = LauvinkoConsonant.C
            else:
                first_onset = PK_TO_LV_ONSETS[original_initial_consonant]

            i = 2

        elif transcription[0] in INFORMAL_PK_ONSETS:
            original_initial_consonant = INFORMAL_PK_ONSETS[transcription[0]]
            first_onset = PK_TO_LV_ONSETS[original_initial_consonant]
            i = 1

        elif transcription[0] in INFORMAL_LV_VOWELS:
            original_initial_consonant = None
            first_onset = None
            i = 0

        else:
            raise ValueError("Initial consonant(s) did not match a PK onset. You may need to add keys to "
                             "INFORMAL_PK_ONSETS.")

        return original_initial_consonant, first_onset, i, syllables



    @staticmethod
    def join(morphemes: List["LauvinkoMorpheme"], accented: Optional[int]) -> LauvinkoSurfaceForm:
        pass
