from dataclasses import dataclass
from enum import Enum
from typing import List, Any, Optional
from lauvinko.lang.shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from .phonology import SurfaceForm


class MorphosyntacticType(Enum):
    CLASS_WORD = "class word"
    ADPOSITION = "adposition"
    MODAL_PREFIX = "modal prefix"
    TERTIARY_ASPECT_PREFIX = "tertiary aspect prefix"
    TOPIC_AGREEMENT_PREFIX = "topic agreement prefix"
    TOPIC_CASE_PREFIX = "topic case prefix"
    NUMBER_SUFFIX = "number suffix"
    INDEPENDENT = "independent"

    class InvalidMSType(ValueError):
        pass


@dataclass
class Lemma:
    """A Lemma is like a word but unspecified for inflection
    It is more or less equivalent to a single dictionary entry for a single language
    """
    ident: str
    definition: str
    category: KasanicStemCategory
    mstype: MorphosyntacticType
    forms: dict[PrimaryTenseAspect, Any]  # Values are stems in PK, morphemes in Lauvinko

    class NonexistentForm(ValueError):
        pass

    def check_form_allowed(self, primary_ta: PrimaryTenseAspect):
        if primary_ta not in self.category.primary_aspects:
            raise self.NonexistentForm(f"{self.category.title} stem has no {primary_ta.value} form")

    def __post_init__(self):
        for primary_ta in self.forms.keys():
            self.check_form_allowed(primary_ta)

    def form(self, *args, **kwargs):
        raise NotImplementedError

    def _generate_form(self, *args, **kwargs):
        raise NotImplementedError

    def citation_form(self):
        return self.form(self.category.citation_form)

    # for API
    def to_json(self) -> dict:
        raise NotImplementedError


@dataclass
class Morpheme:
    lemma: Lemma

    """A Morpheme is a piece of a word. It differs from a Lemma in that it is fully specified for all inflectional
    categories that internally change it, and cannot for instance contain archiphonemes/underspecified phonemes.
    It will usually have a valid surface form in isolation (though dependent morphemes may refrain from implementing
    surface_form), but may still undergo sandhi with adjacent morphemes.
    """
    class InvalidTranscription(ValueError):
        pass

    @staticmethod
    def _from_informal_transcription(transcription: str):
        """Should return a tuple of constructor arguments, for the sake of Morpheme Enums"""
        raise NotImplementedError

    @classmethod
    def from_informal_transcription(cls, transcription: str):
        raise NotImplementedError

    @staticmethod
    def join(*args, **kwargs):
        raise NotImplementedError


class Word:
    """A Word differs from a SurfaceForm in that it still has some knowledge of its underlying morphological structure.
    It differs from a lemma in that it can have a specific set of inflections and/or affixes
    """
    def morphemes(self) -> List[Morpheme]:
        raise NotImplementedError

    def surface_form(self) -> SurfaceForm:
        raise NotImplementedError

    @staticmethod
    def from_morphemes(morphemes: List[Morpheme]) -> "Word":
        raise NotImplementedError


class MorphemeOrderError(ValueError):
    pass


def bucket_kasanic_prefixes(prefixes: List[Morpheme]) -> dict:
    modal_prefixes: List[Morpheme] = []
    tertiary_aspect: Optional[Morpheme] = None
    topic_agreement: Optional[Morpheme] = None
    topic_case: Optional[Morpheme] = None

    i = 0
    while i < len(prefixes) and prefixes[i].lemma.mstype is MorphosyntacticType.MODAL_PREFIX:
        modal_prefixes.append(prefixes[i])
        i += 1

    if i < len(prefixes) and prefixes[i].lemma.mstype is MorphosyntacticType.TERTIARY_ASPECT_PREFIX:
        tertiary_aspect = prefixes[i]
        i += 1

    if i < len(prefixes) and prefixes[i].lemma.mstype is MorphosyntacticType.TOPIC_AGREEMENT_PREFIX:
        topic_agreement = prefixes[i]
        i += 1

    if i < len(prefixes) and prefixes[i].lemma.mstype is MorphosyntacticType.TOPIC_CASE_PREFIX:
        topic_case = prefixes[i]
        i += 1

    if i < len(prefixes):
        raise MorphemeOrderError("Invalid or out of order prefix: " + repr(prefixes[i]))

    if topic_agreement is not None and topic_case is None:
        raise MorphemeOrderError("Must have topic case marker")
    elif topic_case is not None and topic_case.lemma.ident != "$dep$" and topic_agreement is None:
        raise MorphemeOrderError("Must have topic agreement marker")

    return {
        "modal_prefixes": modal_prefixes,
        "tertiary_aspect": tertiary_aspect,
        "topic_agreement": topic_agreement,
        "topic_case": topic_case,
    }
