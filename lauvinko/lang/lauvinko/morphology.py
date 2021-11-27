from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from ..shared.phonology import VowelFrontness
from ..shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from ..shared.morphology import Morpheme, Lemma, Word
from ..proto_kasanic.phonology import ProtoKasanicOnset, ProtoKasanicMutation, ProtoKasanicVowel
from .phonology import (
    LauvinkoSyllable,
    LauvinkoSurfaceForm,
    LauvinkoVowel,
    LauvinkoConsonant,
)
from ..proto_kasanic.morphology import ProtoKasanicLemma
from .diachronic.base import LauvinkoLemmaOrigin, MorphemeContext
from .diachronic.from_pk import ProtoKasanicOrigin, break_pk_consonant, PK_TO_LV_ONSETS
from .diachronic.from_transcription import TranscriptionReader


def epenthetic_vowel(c: LauvinkoConsonant) -> LauvinkoVowel:
    if c is LauvinkoConsonant.Y:
        return LauvinkoVowel.I
    elif c is LauvinkoConsonant.V:
        return LauvinkoVowel.O
    else:
        return LauvinkoVowel.A


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
    original_final_vowel: ProtoKasanicVowel
    end_mutation: Optional[ProtoKasanicMutation]
    falavay: str

    class InvalidAccent(ValueError):
        pass

    def __post_init__(self):
        if self.accent_position is not None and self.accent_position >= len(self.syllables):
            raise LauvinkoMorpheme.InvalidAccent("Accent in invalid position")

        if self.original_final_vowel is None:
            if self.syllables[-1].coda is None:
                v = self.syllables[-1].vowel

                self.original_final_vowel = ProtoKasanicVowel.find_by(
                    frontness=v.frontness,
                    low=v.low,
                )

            else:
                self.original_final_vowel = ProtoKasanicVowel.A

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
            None,
            mut,
            None,
        )

    @staticmethod
    def join(morphemes: List["LauvinkoMorpheme"], accented: Optional[int]) -> LauvinkoSurfaceForm:
        syllables: List[LauvinkoSyllable] = []
        accent_position = None
        falling_accent = None

        for i, morpheme in enumerate(morphemes):
            ms = morpheme.surface_form().syllables

            if len(syllables) > 0:
                pk_consonant = morpheme.original_initial_consonant

                if morphemes[i-1].end_mutation is not None:
                    pk_consonant = morphemes[i-1].end_mutation.mutate(pk_consonant)

                if pk_consonant is not None:
                    c1, c2 = break_pk_consonant(pk_consonant)

                    if c1 is not None:
                        if syllables[-1].coda is None:
                            syllables[-1].coda = c1
                        else:
                            epenthetic_syllable = LauvinkoSyllable(
                                onset=syllables[-1].coda,
                                vowel=epenthetic_vowel(syllables[-1].coda),
                                coda=c1,
                            )

                            syllables[-1].coda = None
                            syllables.append(epenthetic_syllable)

                    ms[0].onset = c2 and PK_TO_LV_ONSETS[c2]

                if ms[0].onset is LauvinkoConsonant.H:
                    ms[0].onset = None

                if ms[0].onset is None:
                    v1, c1, v2, c2 = syllables[-1].vowel, syllables[-1].coda, ms[0].vowel, ms[0].coda

                    if morphemes[i - 1].original_final_vowel is ProtoKasanicVowel.A:
                        ms[0].vowel = LauvinkoVowel.find_by(
                            frontness=v2.frontness,
                            low=True,
                        )

                    elif morphemes[i - 1].original_final_vowel is ProtoKasanicVowel.AA and c2 is None:
                        if v2.frontness is VowelFrontness.FRONT:
                            ms[0].coda = LauvinkoConsonant.Y
                        elif v2.frontness is VowelFrontness.BACK:
                            ms[0].coda = LauvinkoConsonant.V

                        ms[0].vowel = LauvinkoVowel.A

                    v2 = ms[0].vowel

                    if c1 is not None:
                        if morphemes[i - 1].original_final_vowel.frontness is VowelFrontness.BACK and v2.frontness is not VowelFrontness.BACK:
                            ms[0].onset = LauvinkoConsonant.V

                        else:
                            syllables[-1].coda = None
                            ms[0].onset = c1

                    elif v1.frontness is v2.frontness:
                        ms[0].onset = syllables[-1].onset
                        del syllables[-1]
                        ms[0].vowel = LauvinkoVowel.find_by(
                            frontness=v1.frontness,
                            low=v1.low or v2.low,
                        )

                    else:
                        if v1.frontness is VowelFrontness.FRONT:
                            epenthetic_consonant = LauvinkoConsonant.Y
                        elif v1.frontness is VowelFrontness.BACK:
                            epenthetic_consonant = LauvinkoConsonant.V
                        elif v2.frontness is VowelFrontness.FRONT:
                            epenthetic_consonant = LauvinkoConsonant.Y
                        elif v2.frontness is VowelFrontness.BACK:
                            epenthetic_consonant = LauvinkoConsonant.V
                        else:
                            raise RuntimeError

                        ms[0].onset = epenthetic_consonant

            if i == accented:
                accent_position = len(syllables) + morpheme.surface_form().accent_position
                falling_accent = morpheme.surface_form().falling_accent

            syllables += ms

        return LauvinkoSurfaceForm(
            syllables=syllables,
            accent_position=accent_position,
            falling_accent=falling_accent,
        )


@dataclass
class LauvinkoLemma(Lemma):
    definition: str
    category: KasanicStemCategory
    forms: dict[tuple[PrimaryTenseAspect, MorphemeContext], LauvinkoMorpheme]
    origin: LauvinkoLemmaOrigin

    def __post_init__(self):
        for primary_ta, _ in self.forms.keys():
            if primary_ta not in self.category.primary_aspects:
                raise Lemma.NonexistentForm

    def form(self, primary_ta: PrimaryTenseAspect, context: MorphemeContext):
        self.check_form_allowed(primary_ta)

        if (primary_ta, context) not in self.forms:
            self.forms[(primary_ta, context)] = self._generate_form(primary_ta, context)

        return self.forms[(primary_ta, context)]

    def _generate_form(self, primary_ta: PrimaryTenseAspect, context: MorphemeContext) -> LauvinkoMorpheme:
        sf, oic, ofv, mut, falavay = self.origin.generate_form(primary_ta, context)
        return LauvinkoMorpheme(
            syllables=sf.syllables,
            accent_position=sf.accent_position,
            falling_accent=sf.falling_accent,
            original_initial_consonant=oic,
            original_final_vowel=ofv,
            end_mutation=mut,
            falavay=falavay,
        )

    def citation_form(self, context: MorphemeContext = MorphemeContext.NONAUGMENTED):
        return self.form(self.category.citation_form, context)

    @classmethod
    def from_pk(cls, pk_lemma: ProtoKasanicLemma, definition: Optional[str] = None,
                forms: Optional[dict[tuple[PrimaryTenseAspect, bool], LauvinkoMorpheme]] = None) -> "LauvinkoLemma":
        return cls(
            definition=(definition or pk_lemma.definition),
            category=pk_lemma.category,
            forms=forms or {},
            origin=ProtoKasanicOrigin(pk_lemma),
        )


@dataclass
class Case:
    abbreviation: str
    augment: bool


class LauvinkoCase(Case, Enum):
    VOLITIVE = ("vol", True)
    INSTRUMENTAL = ("ins", False)
    PATIENTIVE = ("pat", False)
    DATIVE = ("dat", True)
    ALLATIVE = ("all", False)
    LOCATIVE = ("loc", True)
    ABLATIVE = ("abl", False)
    PERLATIVE = ("prl", False)
    PARTITIVE = ("par", False)


@dataclass
class LauvinkoPronoun:
    personal: Optional[LauvinkoMorpheme]
    case: LauvinkoCase
    definite: bool


@dataclass
class LauvinkoWord(Word):
    disjunct_prefixes: List[LauvinkoMorpheme]
    modal_prefixes: List[LauvinkoMorpheme]
    tertiary_aspect: Optional[LauvinkoMorpheme]
    topic_agreement: Optional[LauvinkoMorpheme]
    topic_case: Optional[LauvinkoMorpheme]
    stem: LauvinkoMorpheme
    pronoun: LauvinkoPronoun

    def prefixes(self):
        out = [*self.disjunct_prefixes, *self.modal_prefixes]

        for m in self.tertiary_aspect, self.topic_agreement, self.topic_agreement:
            if m is not None:
                out.append(m)

        return out

    def morphemes(self) -> List[LauvinkoMorpheme]:
        return [
            *self.prefixes(),
            self.stem,
            *self.pronoun.morphemes()
        ]

    def surface_form(self) -> LauvinkoSurfaceForm:
        return LauvinkoMorpheme.join(morphemes=self.morphemes(), accented=len(self.prefixes()))



