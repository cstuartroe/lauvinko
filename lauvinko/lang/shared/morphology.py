from dataclasses import dataclass
from typing import List, Any
from lauvinko.lang.shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from .phonology import SurfaceForm


@dataclass
class Morpheme:
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


@dataclass
class Lemma:
    """A Lemma is like a word but unspecified for inflection
    It is more or less equivalent to a single dictionary entry for a single language
    """
    definition: str
    category: KasanicStemCategory
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


class Word:
    """A Word differs from a SurfaceForm in that it still has some knowledge of its underlying morphological structure.
    It differs from a lemma in that it can have a specific set of inflections and/or affixes
    """
    def morphemes(self) -> List[Morpheme]:
        raise NotImplementedError

    def surface_form(self) -> SurfaceForm:
        raise NotImplementedError
