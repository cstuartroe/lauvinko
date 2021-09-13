from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from ..shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from ..shared.morphology import Morpheme, Lemma, Word
from ..proto_kasanic.phonology import ProtoKasanicOnset, ProtoKasanicMutation
from .phonology import (
    LauvinkoSyllable,
    LauvinkoSurfaceForm,
)
from ..proto_kasanic.morphology import ProtoKasanicLemma
from .diachronic.base import LauvinkoLemmaOrigin
from .diachronic.from_pk import ProtoKasanicOrigin
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


@dataclass
class LauvinkoLemma(Lemma):
    definition: str
    category: KasanicStemCategory
    forms: dict[tuple[PrimaryTenseAspect, bool], LauvinkoMorpheme]
    origin: LauvinkoLemmaOrigin

    def form(self, primary_ta: PrimaryTenseAspect, augment: bool):
        self.check_form_allowed(primary_ta)

        if primary_ta not in self.forms:
            self.forms[(primary_ta, augment)] = self._generate_form(primary_ta, augment)

        return self.forms[(primary_ta, augment)]

    def _generate_form(self, primary_ta: PrimaryTenseAspect, augment: bool) -> LauvinkoMorpheme:
        sf, oic, mut, falavay = self.origin.generate_form(primary_ta, augment)
        return LauvinkoMorpheme(
            syllables=sf.syllables,
            accent_position=sf.accent_position,
            falling_accent=sf.falling_accent,
            original_initial_consonant=oic,
            end_mutation=mut,
            falavay=falavay,
        )

    def citation_form(self, augment=False):
        return self.form(self.category.citation_form, augment)

    @classmethod
    def from_pk(cls, pk_lemma: ProtoKasanicLemma) -> "LauvinkoLemma":
        return cls(
            definition=pk_lemma.definition,
            category=pk_lemma.category,
            forms={},
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



