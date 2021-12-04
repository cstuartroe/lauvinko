from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from ..proto_kasanic.romanize import falavay
from ..shared.phonology import VowelFrontness
from ..shared.semantics import PrimaryTenseAspect, KasanicStemCategory, PTA2ABBREV
from ..shared.morphology import Morpheme, Lemma, Word, MorphosyntacticType, bucket_kasanic_prefixes
from ..proto_kasanic.phonology import ProtoKasanicVowel, PKSurfaceForm, ProtoKasanicSyllable, ProtoKasanicOnset
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
from .romanize import romanize


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

    class InvalidAccent(ValueError):
        pass

    def original_initial_consonant(self):
        return self.virtual_original_form.surface_form.syllables[0].onset

    def original_final_vowel(self):
        return self.virtual_original_form.surface_form.syllables[-1].vowel

    def end_mutation(self):
        return self.virtual_original_form.end_mutation

    def falavay(self):
        return falavay(self.virtual_original_form.surface_form)  # TODO: augment?

    def romanization(self):
        return romanize(self.surface_form)

    def to_json(self):
        return {
            "romanization": self.romanization(),
            "falavay": self.falavay(),
        }

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
        }

    @staticmethod
    def join(morphemes: List["LauvinkoMorpheme"], accented: Optional[int]) -> "LauvinkoMorpheme":
        syllables: List[LauvinkoSyllable] = []
        pk_syllables: List[ProtoKasanicSyllable] = []
        accent_position = None
        falling_accent = None

        for i, morpheme in enumerate(morphemes):
            pk_syllables += morpheme.virtual_original_form.surface_form.syllables

            ms = [
                LauvinkoSyllable(
                    onset=s.onset,
                    vowel=s.vowel,
                    coda=s.coda,
                )
                for s in morpheme.surface_form.syllables
            ]

            False and print(
                "".join(
                    f"{s.onset}{s.vowel}{s.coda or ''}"
                    for s in ms
                )
            )

            if len(syllables) > 0:
                pk_consonant = morpheme.original_initial_consonant()

                if morphemes[i - 1].end_mutation() is not None:
                    pk_consonant = morphemes[i - 1].end_mutation().mutate(pk_consonant)

                if pk_consonant is not None and pk_consonant is not ProtoKasanicOnset.NC:
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

                    if morphemes[i - 1].original_final_vowel() is ProtoKasanicVowel.A:
                        merged_vowel = LauvinkoVowel.find_by(
                            frontness=v2.frontness,
                            low=True,
                        )
                        ms[0].vowel = merged_vowel
                        v1 = merged_vowel

                    elif morphemes[i - 1].original_final_vowel() is ProtoKasanicVowel.AA and c2 is None and \
                            not (accented == i and morpheme.surface_form.accent_position == 0):
                        if v2.frontness is VowelFrontness.FRONT:
                            ms[0].coda = LauvinkoConsonant.Y
                        elif v2.frontness is VowelFrontness.BACK:
                            ms[0].coda = LauvinkoConsonant.V

                        ms[0].vowel = LauvinkoVowel.A

                    v2 = ms[0].vowel

                    if c1 is not None:
                        print("c1 is not none")
                        if morphemes[i - 1].original_final_vowel().frontness is VowelFrontness.BACK \
                                and v2.frontness is not VowelFrontness.BACK:
                            ms[0].onset = LauvinkoConsonant.V

                        else:
                            syllables[-1].coda = None
                            ms[0].onset = c1

                    elif morpheme.surface_form.accent_position != 0 and v2.frontness is VowelFrontness.MID:
                        print("drop initial vowel")
                        ms[0].onset = syllables[-1].onset
                        ms[0].vowel = v1
                        del syllables[-1]

                    elif v1.frontness is v2.frontness:
                        print("frontness equal")
                        ms[0].onset = syllables[-1].onset
                        del syllables[-1]
                        ms[0].vowel = LauvinkoVowel.find_by(
                            frontness=v1.frontness,
                            low=v1.low or v2.low,
                        )

                    else:
                        print("insert glide")
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
                accent_position = len(syllables) + morpheme.surface_form.accent_position
                falling_accent = morpheme.surface_form.falling_accent

            syllables += ms

        lv_sf = LauvinkoSurfaceForm(
            syllables=syllables,
            accent_position=accent_position,
            falling_accent=falling_accent,
        )

        return LauvinkoMorpheme(
            lemma=None,
            surface_form=lv_sf,
            virtual_original_form=ProtoKasanicMorpheme(
                lemma=None,
                surface_form=PKSurfaceForm(
                    syllables=pk_syllables,
                    stress_position=None,  # TODO
                ),
                end_mutation=morphemes[-1].end_mutation(),
            ),
        )


@dataclass
class LauvinkoLemma(Lemma):
    definition: str
    category: KasanicStemCategory
    mstype: MorphosyntacticType
    forms: dict[tuple[PrimaryTenseAspect, MorphemeContext], LauvinkoMorpheme]
    origin: LauvinkoLemmaOrigin

    def __post_init__(self):
        for (primary_ta, context), form in self.forms.items():
            if primary_ta not in self.category.primary_aspects:
                raise Lemma.NonexistentForm

            form.lemma = self

    def form(self, primary_ta: PrimaryTenseAspect, context: MorphemeContext):
        self.check_form_allowed(primary_ta)

        if (primary_ta, context) not in self.forms:
            self.forms[(primary_ta, context)] = self._generate_form(primary_ta, context)

        return self.forms[(primary_ta, context)]

    def _generate_form(self, primary_ta: PrimaryTenseAspect, context: MorphemeContext) -> LauvinkoMorpheme:
        sf, vof = self.origin.generate_form(primary_ta, context)
        return LauvinkoMorpheme(
            lemma=self,
            surface_form=sf,
            virtual_original_form=vof,
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

    # for API
    def to_json(self):
        forms = {}

        for pta in self.category.primary_aspects:
            abbrev = PTA2ABBREV[pta]

            forms[abbrev + ".au"] = self.form(
                pta,
                MorphemeContext.AUGMENTED,
            ).to_json()

            forms[abbrev + ".na"] = self.form(
                pta,
                MorphemeContext.NONAUGMENTED,
            ).to_json()

        return {
            "forms": forms,
            "definition": self.definition,
            "category": self.category.title,
        }


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


class LauvinkoWordType(Enum):
    CONTENT_WORD = "content word"
    DETERMINER = "determiner"
    ADPOSITION = "adposition"


class InvalidSyntacticWordSequence(ValueError):
    pass


@dataclass
class LauvinkoWord(Word):
    def __post_init__(self):
        self._as_morph = LauvinkoMorpheme.join(
            morphemes=self.morphemes(),
            accented=self._get_accented(),
        )

    def _get_accented(self):
        raise NotImplementedError

    def morphemes(self) -> List[LauvinkoMorpheme]:
        raise NotImplementedError

    def falavay(self):
        return self._as_morph.falavay()

    def surface_form(self) -> LauvinkoSurfaceForm:
        return self._as_morph.surface_form

    def word_type(self) -> LauvinkoWordType:
        raise NotImplementedError

    @classmethod
    def from_morphemes(cls, morphemes: List[LauvinkoMorpheme]) -> "LauvinkoWord":
        if morphemes[-1].lemma.mstype is MorphosyntacticType.INDEPENDENT:
            return LauvinkoContentWord.from_morphemes(morphemes)

        elif morphemes[0].lemma.mstype is MorphosyntacticType.CLASS_WORD:
            return LauvinkoClassWord.from_morphemes(morphemes)

        else:
            raise NotImplementedError

    @staticmethod
    def join_syntactic_words(words: List["LauvinkoWord"]) -> "LauvinkoSurfaceForm":
        if len(words) == 1:
            return words[0].surface_form()

        accented = 0
        i = 0
        found = False

        if words[i].word_type() is LauvinkoWordType.CONTENT_WORD:
            found = True
            i += 1

        if words[i:] and words[i].word_type() is LauvinkoWordType.ADPOSITION:
            found = False
            accented += 1
            i += 1

        if words[i:] and words[i].word_type() is LauvinkoWordType.CONTENT_WORD:
            found = True
            accented += 1
            i += 1

        if words[i:] and words[i].word_type() is LauvinkoWordType.DETERMINER:
            i += 1

        if not found or i != len(words):
            raise InvalidSyntacticWordSequence(str([w.word_type().value for w in words]))

        return LauvinkoSurfaceForm.cliticize(
            sfs=[w.surface_form() for w in words],
            accented=accented,
        )


@dataclass
class LauvinkoContentWord(LauvinkoWord):
    modal_prefixes: List[LauvinkoMorpheme]
    tertiary_aspect: Optional[LauvinkoMorpheme]
    topic_agreement: Optional[LauvinkoMorpheme]
    topic_case: Optional[LauvinkoMorpheme]
    stem: LauvinkoMorpheme

    def _get_accented(self):
        return len(self.prefixes())

    def __post_init__(self):
        super().__post_init__()
        assert self.stem.lemma.mstype is MorphosyntacticType.INDEPENDENT

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

    def word_type(self) -> LauvinkoWordType:
        return LauvinkoWordType.CONTENT_WORD

    @classmethod
    def from_morphemes(cls, morphemes: List[LauvinkoMorpheme]) -> "LauvinkoContentWord":
        prefixes, stem = morphemes[:-1], morphemes[-1]
        return cls(
            stem=stem,
            **bucket_kasanic_prefixes(prefixes),
        )


@dataclass
class LauvinkoClassWord(LauvinkoWord):
    class_word: LauvinkoMorpheme
    case_suffix: Optional[LauvinkoMorpheme]

    def __post_init__(self):
        super().__post_init__()
        assert self.class_word.lemma.mstype is MorphosyntacticType.CLASS_WORD
        if self.case_suffix is not None:
            assert self.case_suffix.lemma.mstype is MorphosyntacticType.CASE_MARKER

    def _get_accented(self):
        return 1

    def morphemes(self) -> List[LauvinkoMorpheme]:
        if self.case_suffix is None:
            return [self.class_word]
        else:
            return [self.class_word, self.case_suffix]

    def word_type(self) -> LauvinkoWordType:
        return LauvinkoWordType.DETERMINER

    @classmethod
    def from_morphemes(cls, morphemes: List[LauvinkoMorpheme]) -> "LauvinkoClassWord":
        if len(morphemes) == 1:
            return cls(morphemes[0], None)
        elif len(morphemes) == 2:
            return cls(*morphemes)
        else:
            raise ValueError
