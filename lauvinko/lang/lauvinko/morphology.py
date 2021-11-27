from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from ..shared.phonology import VowelFrontness
from ..shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from ..shared.morphology import Morpheme, Lemma, Word
from ..proto_kasanic.phonology import ProtoKasanicVowel
from .phonology import (
    LauvinkoSyllable,
    LauvinkoSurfaceForm,
    LauvinkoVowel,
    LauvinkoConsonant,
)
from ..proto_kasanic.morphology import ProtoKasanicLemma, ProtoKasanicMorpheme
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
    surface_form: LauvinkoSurfaceForm
    virtual_original_form: ProtoKasanicMorpheme
    falavay: str

    class InvalidAccent(ValueError):
        pass

    def original_initial_consonant(self):
        return self.virtual_original_form.surface_form.syllables[0].onset

    @classmethod
    def from_informal_transcription(cls, transcription: str) -> "LauvinkoMorpheme":
        return cls(*cls._from_informal_transcription(transcription))

    @staticmethod
    def _from_informal_transcription(transcription: str):
        sf, vof = TranscriptionReader(transcription).read()
        return (
            sf,
            vof,
            None,
        )

    @staticmethod
    def join(morphemes: List["LauvinkoMorpheme"], accented: Optional[int]) -> LauvinkoSurfaceForm:
        return morphemes[0].surface_form


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
        sf, vof, falavay = self.origin.generate_form(primary_ta, context)
        return LauvinkoMorpheme(
            surface_form=sf,
            virtual_original_form=vof,
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



