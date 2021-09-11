from dataclasses import dataclass
from typing import List, Optional
from lauvinko.lang.shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from .phonology import Syllable, SurfaceForm


@dataclass
class Morpheme:
    """A Morpheme is a piece of a word. It differs from a Lemma in that it is fully specified for all inflectional
    categories that internally change it, and cannot for instance contain archiphonemes/underspecified phonemes.
    It will usually have a valid surface form in isolation (though dependent morphemes may refrain from implementing
    surface_form), but may still undergo sandhi with adjacent morphemes.
    """
    syllables: List[Syllable]

    def surface_form(self, *args, **kwargs) -> Optional[SurfaceForm]:
        raise NotImplementedError

    class InvalidTranscription(ValueError):
        pass

    @staticmethod
    def _from_informal_transcription(transcription: str):
        """Should return a tuple of constructor arguments, for the sake of Morpheme Enums"""
        raise NotImplementedError

    @classmethod
    def from_informal_transcription(cls, transcription: str):
        return cls(*cls._from_informal_transcription(transcription))

    @staticmethod
    def join(*args, **kwargs) -> SurfaceForm:
        raise NotImplementedError


@dataclass
class Lemma:
    """A Lemma is like a word but unspecified for inflection
    It is more or less equivalent to a single dictionary entry for a single language
    """
    definition: str
    category: KasanicStemCategory
    forms: dict

    def form(self, primary_ta: PrimaryTenseAspect):
        if primary_ta not in self.forms:
            self.forms[primary_ta] = self._generate_form(primary_ta)

        return self.forms[primary_ta]

    def _generate_form(self, primary_ta: PrimaryTenseAspect):
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
