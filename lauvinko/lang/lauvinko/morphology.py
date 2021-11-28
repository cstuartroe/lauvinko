from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from ..shared.phonology import VowelFrontness
from ..shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from ..shared.morphology import Morpheme, Lemma, Word, MorphosyntacticType, bucket_kasanic_prefixes
from ..proto_kasanic.phonology import ProtoKasanicVowel, PKSurfaceForm
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
    lemma: Optional["LauvinkoLemma"]
    surface_form: LauvinkoSurfaceForm
    virtual_original_form: ProtoKasanicMorpheme
    falavay: str

    class InvalidAccent(ValueError):
        pass

    def original_initial_consonant(self):
        return self.virtual_original_form.surface_form.syllables[0].onset

    @classmethod
    def from_informal_transcription(cls, transcription: str) -> "LauvinkoMorpheme":
        return cls(**cls._from_informal_transcription(transcription))

    @staticmethod
    def _from_informal_transcription(transcription: str):
        sf, vof = TranscriptionReader(transcription).read()
        return {
            "lemma": None,
            "surface_form": sf,
            "virtual_original_form": vof,
            "falavay": None,
        }

    @staticmethod
    def join(morphemes: List["LauvinkoMorpheme"], accented: Optional[int], context: MorphemeContext) -> LauvinkoSurfaceForm:
        virtual_combined_form = ProtoKasanicMorpheme.join([
            m.virtual_original_form
            for m in morphemes
        ], stressed=accented)

        return ProtoKasanicOrigin.evolve_surface_form(
            pk_sf=virtual_combined_form,
            context=context
        )


@dataclass
class LauvinkoLemma(Lemma):
    definition: str
    category: KasanicStemCategory
    mstype: MorphosyntacticType
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
            lemma=self,
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
            mstype=pk_lemma.mstype,
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
class LauvinkoWord(Word):
    modal_prefixes: List[LauvinkoMorpheme]
    tertiary_aspect: Optional[LauvinkoMorpheme]
    topic_agreement: Optional[LauvinkoMorpheme]
    topic_case: Optional[LauvinkoMorpheme]
    stem: LauvinkoMorpheme

    def prefixes(self):
        out = [*self.modal_prefixes]

        for m in self.tertiary_aspect, self.topic_agreement, self.topic_case:
            if m is not None:
                out.append(m)

        return out

    def morphemes(self) -> List[LauvinkoMorpheme]:
        return [
            *self.prefixes(),
            self.stem,
        ]

    def surface_form(self) -> LauvinkoSurfaceForm:
        return LauvinkoMorpheme.join(
            morphemes=self.morphemes(),
            accented=len(self.prefixes()),
            context=MorphemeContext.NONAUGMENTED,  # TODO
        )

    @classmethod
    def from_morphemes(cls, morphemes: List[LauvinkoMorpheme]) -> "LauvinkoWord":
        prefixes, stem = morphemes[:-1], morphemes[-1]
        return cls(
            stem=stem,
            **bucket_kasanic_prefixes(prefixes),
        )



