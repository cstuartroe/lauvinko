from enum import Enum
from typing import Optional, List
from lauvinko.lang.proto_kasanic.phonology import (
    ProtoKasanicOnset,
    PKSurfaceForm,
    ProtoKasanicSyllable,
    ProtoKasanicVowel,
)
from lauvinko.lang.proto_kasanic.morphology import MUTATION_NOTATION, ProtoKasanicMorpheme
from lauvinko.lang.lauvinko.phonology import LauvinkoConsonant, LauvinkoVowel, LauvinkoSyllable, LauvinkoSurfaceForm
from .from_pk import PK_TO_LV_ONSETS


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


class InvalidTranscription(ValueError):
    pass


class TranscriptionReaderState(Enum):
    # The next thing must be a vowel
    PRE_VOWEL = "pre-vowel"
    # The next thing must be a consonant or accent mark
    POST_VOWEL = "post-vowel"
    # Just saw a post-vowel consonant, not yet sure whether it was an onset or coda
    # Either consonant or vowel allowed next
    POST_CONSONANT = "post-consonant"


class TranscriptionReader:
    def __init__(self, transcription: str):
        self.transcription = transcription
        self.original_initial_consonant: Optional[ProtoKasanicOnset] = None
        self.end_mutation = None
        self.i = 0
        self.syllables: list[LauvinkoSyllable] = []
        self.accent_position: Optional[int] = None
        self.falling_accent: Optional[bool] = None
        self.last_seen_consonant: Optional[LauvinkoConsonant] = None
        self.state: TranscriptionReaderState = None

    def next(self, n=1):
        if len(self.transcription) >= self.i + n:
            return self.transcription[self.i: self.i + n]

    def read(self) -> tuple[LauvinkoSurfaceForm, ProtoKasanicMorpheme]:
        self.get_end_mutation()
        self.get_initial_consonant()
        self.main_loop()
        self.resolve_final_consonant()

        virtual_syllables: List[ProtoKasanicSyllable] = []
        for i, syllable in enumerate(self.syllables):
            s = ProtoKasanicSyllable(
                onset=self.original_initial_consonant if i == 0 else None, # TODO?
                vowel=ProtoKasanicVowel.find_by(
                    frontness=syllable.vowel.frontness,
                    low=syllable.vowel.low,
                )
            )

            virtual_syllables.append(s)

            # TODO: this doesn't really work lol, what about codas n whatnot

        return (
            LauvinkoSurfaceForm(
                syllables=self.syllables,
                accent_position=self.accent_position,
                falling_accent=self.falling_accent,
            ),
            ProtoKasanicMorpheme(
                lemma=None,
                surface_form=PKSurfaceForm(
                    syllables=virtual_syllables,
                    stress_position=self.accent_position,
                ),
                end_mutation=self.end_mutation,
            ),
        )

    def get_end_mutation(self):
        if len(self.transcription) >= 2 and self.transcription[-2:] in MUTATION_NOTATION:
            self.end_mutation = MUTATION_NOTATION[self.transcription[-2:]]
            self.transcription = self.transcription[:-2]
        else:
            self.end_mutation = None

    def get_initial_consonant(self):
        if self.next(3) in INFORMAL_PK_ONSETS:
            self.original_initial_consonant = INFORMAL_PK_ONSETS[self.next(3)]
            self.last_seen_consonant = PK_TO_LV_ONSETS[self.original_initial_consonant]
            self.i += 3

        elif self.next(2) in INFORMAL_PK_ONSETS:
            self.original_initial_consonant = INFORMAL_PK_ONSETS[self.next(2)]

            if self.original_initial_consonant is ProtoKasanicOnset.NC:
                self.syllables.append(LauvinkoSyllable(
                    onset=None,
                    vowel=LauvinkoVowel.A,
                    coda=LauvinkoConsonant.N,
                ))
                self.last_seen_consonant = LauvinkoConsonant.C
            else:
                self.last_seen_consonant = PK_TO_LV_ONSETS[self.original_initial_consonant]

            self.i += 2

        elif self.next() in INFORMAL_PK_ONSETS:
            self.original_initial_consonant = INFORMAL_PK_ONSETS[self.next()]
            self.last_seen_consonant = PK_TO_LV_ONSETS[self.original_initial_consonant]
            self.i += 1

        elif self.next() in INFORMAL_LV_VOWELS:
            self.original_initial_consonant = None
            self.last_seen_consonant = None

        else:
            raise InvalidTranscription("Initial consonant(s) did not match a PK onset. You may need to add keys to "
                                       "INFORMAL_PK_ONSETS.")

        self.state = TranscriptionReaderState.PRE_VOWEL

    def push_vowel(self, v_str: str):
        vowel = INFORMAL_LV_VOWELS[v_str]
        self.syllables.append(LauvinkoSyllable(onset=self.last_seen_consonant, vowel=vowel, coda=None))
        self.last_seen_consonant = None
        self.state = TranscriptionReaderState.POST_VOWEL
        self.i += len(v_str)

    def get_consonant(self):
        if self.next(2) in INFORMAL_LV_CONSONANTS:
            c_str = self.next(2)
        elif self.next() in INFORMAL_LV_CONSONANTS:
            c_str = self.next()
        else:
            raise InvalidTranscription(f"Expecting consonant at position {self.i} of {self.transcription}")

        self.i += len(c_str)
        return INFORMAL_LV_CONSONANTS[c_str]

    def main_loop(self):
        while self.i < len(self.transcription):
            if self.state is TranscriptionReaderState.PRE_VOWEL:
                if self.next() in INFORMAL_LV_VOWELS:
                    self.push_vowel(self.next())

                else:
                    raise InvalidTranscription(f"Expecting vowel at position {self.i} of {self.transcription}")

            elif self.state is TranscriptionReaderState.POST_VOWEL:
                if self.next() in "/\\":
                    if self.accent_position is not None:
                        raise InvalidTranscription(f"More than one accented syllable in {self.transcription}")

                    self.accent_position = len(self.syllables) - 1
                    self.falling_accent = self.next() == '\\'
                    self.i += 1
                    continue

                self.last_seen_consonant = self.get_consonant()
                self.state = TranscriptionReaderState.POST_CONSONANT

            elif self.state is TranscriptionReaderState.POST_CONSONANT:
                if self.next() in INFORMAL_LV_VOWELS:
                    self.push_vowel(self.next())

                else:
                    self.syllables[-1].coda = self.last_seen_consonant
                    self.last_seen_consonant = self.get_consonant()
                    self.state = TranscriptionReaderState.PRE_VOWEL

    def resolve_final_consonant(self):
        if self.state is TranscriptionReaderState.PRE_VOWEL:
            raise InvalidTranscription(f"Ends with two consonants: {self.transcription}")
        elif self.state is TranscriptionReaderState.POST_CONSONANT:
            self.syllables[-1].coda = self.last_seen_consonant
