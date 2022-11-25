from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import re
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
from .diachronic.from_pk import ProtoKasanicOrigin, break_pk_consonant, PK_TO_LV_ONSETS, OFFGLIDES
from .diachronic.from_transcription import TranscriptionReader
from .romanize import romanize


def epenthetic_vowel(c: LauvinkoConsonant) -> LauvinkoVowel:
    if c is LauvinkoConsonant.Y:
        return LauvinkoVowel.I
    elif c is LauvinkoConsonant.V:
        return LauvinkoVowel.O
    else:
        return LauvinkoVowel.A


def epenthetic_consonant(f: VowelFrontness) -> Optional[LauvinkoConsonant]:
    if f in (VowelFrontness.FRONT, VowelFrontness.FRONTING):
        return LauvinkoConsonant.Y
    elif f in (VowelFrontness.BACK, VowelFrontness.BACKING):
        return LauvinkoConsonant.V
    else:
        return None

@dataclass
class LauvinkoMorpheme(Morpheme):
    """One of the complexities of LauvinkoMorpheme is that LauvinkoMorpheme.join needs to maintain equivalence with
    historical change. For this reason, it needs to maintain original_initial_consonant and end_mutation
    so that mutations can be retroactively applied.
    """
    lemma: Optional["LauvinkoLemma"]
    surface_form: LauvinkoSurfaceForm
    virtual_original_form: ProtoKasanicMorpheme
    context: MorphemeContext

    class InvalidAccent(ValueError):
        pass

    def original_initial_consonant(self):
        sylls = self.virtual_original_form.surface_form.syllables
        if len(sylls) == 0:
            return None
        else:
            return sylls[0].onset

    def end_mutation(self):
        return self.virtual_original_form.end_mutation

    def falavay(self):
        return falavay(self.virtual_original_form.surface_form, augment=self.context is MorphemeContext.AUGMENTED)

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
            "context": MorphemeContext.NONAUGMENTED,
        }

    @staticmethod
    def join(morphemes: List["LauvinkoMorpheme"], accented: Optional[int]) -> "LauvinkoMorpheme":
        syllables: List[LauvinkoSyllable] = []
        pk_syllables: List[ProtoKasanicSyllable] = []
        accent_position = None
        falling_accent = None
        pk_stress_position = None
        active_mutation = None

        for i, morpheme in enumerate(morphemes):
            ms = [
                LauvinkoSyllable(
                    onset=s.onset,
                    vowel=s.vowel,
                    coda=s.coda,
                )
                for s in morpheme.surface_form.syllables
            ]

            morpheme_pk_syllables = [
                ProtoKasanicSyllable(
                    onset=s.onset,
                    vowel=s.vowel,
                )
                for s in morpheme.virtual_original_form.surface_form.syllables
            ]

            pk_consonant = morpheme.original_initial_consonant()

            if active_mutation is not None and len(ms) > 0:
                pk_consonant = active_mutation.mutate(pk_consonant)
                morpheme_pk_syllables[0].onset = pk_consonant

            if len(ms) == 0:
                pass
            elif len(syllables) > 0:
                if pk_consonant is not None and pk_consonant is not ProtoKasanicOnset.NC:
                    c1, c2 = break_pk_consonant(pk_consonant)

                    if c1 is not None:
                        if syllables[-1].coda is None:
                            syllables[-1].coda = c1
                        elif syllables[-1].coda is LauvinkoConsonant.A:
                            epenthetic_syllable = LauvinkoSyllable(
                                onset=epenthetic_consonant(syllables[-1].vowel.frontness),
                                vowel=LauvinkoVowel.A,
                                coda=c1,
                            )

                            syllables[-1].coda = None
                            syllables.append(epenthetic_syllable)
                        else:
                            epenthetic_syllable = LauvinkoSyllable(
                                onset=syllables[-1].coda,
                                vowel=epenthetic_vowel(syllables[-1].coda),
                                coda=c1,
                            )

                            syllables[-1].coda = None
                            syllables.append(epenthetic_syllable)

                    ms[0].onset = c2 and PK_TO_LV_ONSETS[c2]
            else:
                if pk_consonant is not ProtoKasanicOnset.NC:
                    ms[0].onset = pk_consonant and PK_TO_LV_ONSETS[pk_consonant]

            if len(syllables) > 0 and len(ms) > 0:
                if ms[0].onset is LauvinkoConsonant.H:
                    ms[0].onset = None

                if ms[0].onset is None:
                    v1, c1, v2, c2 = syllables[-1].vowel, syllables[-1].coda, ms[0].vowel, ms[0].coda

                    original_final_vowel = pk_syllables[-1].vowel

                    if c1 is LauvinkoConsonant.A:
                        pass

                    elif original_final_vowel is ProtoKasanicVowel.A:
                        merged_vowel = LauvinkoVowel.find_by(
                            frontness=v2.frontness,
                            low=True,
                        )
                        ms[0].vowel = merged_vowel

                    elif original_final_vowel is ProtoKasanicVowel.AA and c2 is None and \
                            not (accented == i and morpheme.surface_form.accent_position == 0):
                        ms[0].coda = epenthetic_consonant(v2.frontness)
                        ms[0].vowel = LauvinkoVowel.A

                    v2 = ms[0].vowel
                    if c1 is not None:
                        if original_final_vowel.frontness is VowelFrontness.BACK \
                                and v2.frontness is not VowelFrontness.BACK:
                            ms[0].onset = LauvinkoConsonant.V

                        elif c1 is LauvinkoConsonant.A:
                            syllables[-1].coda = None
                            ms[0].onset = epenthetic_consonant(v1.frontness)

                        else:
                            syllables[-1].coda = None
                            ms[0].onset = c1

                    if ms[0].onset is not None:
                        pass

                    elif morpheme.surface_form.accent_position != 0 and v2.frontness is VowelFrontness.MID:
                        ms[0].onset = syllables[-1].onset
                        ms[0].vowel = v1
                        del syllables[-1]

                    elif v1.frontness is v2.frontness and not (v1 is LauvinkoVowel.I and v2 is LauvinkoVowel.E):
                        ms[0].onset = syllables[-1].onset
                        del syllables[-1]
                        ms[0].vowel = LauvinkoVowel.find_by(
                            frontness=v1.frontness,
                            low=v1.low or v2.low,
                        )

                    else:
                        ec = (epenthetic_consonant(original_final_vowel.frontness)
                              or epenthetic_consonant(v2.frontness)
                              or epenthetic_consonant(v1.frontness))
                        if ec is None:
                            raise RuntimeError(f"{original_final_vowel} {v1} {v2}")

                        ms[0].onset = ec

            if i == accented:
                pk_stress_position = len(pk_syllables) + morpheme.virtual_original_form.surface_form.stress_position

                if morpheme.surface_form.accent_position is None:
                    raise LauvinkoMorpheme.InvalidAccent(f"Morpheme bears no accent: {morpheme}")

                accent_position = len(syllables) + morpheme.surface_form.accent_position
                falling_accent = morpheme.surface_form.falling_accent

            syllables += ms

            pk_syllables += morpheme_pk_syllables

            if (len(ms) > 0) or (morpheme.end_mutation() is not None):
                active_mutation = morpheme.end_mutation()

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
                    stress_position=pk_stress_position,
                ),
                end_mutation=morphemes[-1].end_mutation(),
            ),
            context=morphemes[-1].context,
        )


@dataclass
class LauvinkoLemma(Lemma):
    ident: str
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

    def form(self, primary_ta: PrimaryTenseAspect, context: MorphemeContext) -> LauvinkoMorpheme:
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
            context=context,
        )

    def citation_form(self, context: MorphemeContext = MorphemeContext.NONAUGMENTED):
        return self.form(self.category.citation_form, context)

    @classmethod
    def from_pk(cls, pk_lemma: ProtoKasanicLemma, definition: Optional[str] = None,
                forms: Optional[dict[tuple[PrimaryTenseAspect, bool], LauvinkoMorpheme]] = None) -> "LauvinkoLemma":
        return cls(
            ident=pk_lemma.ident,
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
    AGENTIVE = ("age", True)
    INSTRUMENTAL = ("ins", False)
    PATIENTIVE = ("pat", False)
    GENITIVE = ("gen", None)
    ALLATIVE = ("all", False)
    LOCATIVE = ("loc", True)
    ABLATIVE = ("abl", False)
    PERLATIVE = ("prl", False)
    PARTITIVE = ("par", False)


CASE_BY_IDENT = {
    f"${c.abbreviation}$": c
    for c in LauvinkoCase
}


class LauvinkoWordType(Enum):
    CONTENT_WORD = "content word"
    DETERMINER = "determiner"
    ADPOSITION = "adposition"
    NUMBER_SUFFIX = "number suffix"
    SEX_SUFFIX = "sex suffix"


class InvalidSyntacticWordSequence(ValueError):
    pass


PARTICLE_MSTYPES = {
    MorphosyntacticType.ADPOSITION: LauvinkoWordType.ADPOSITION,
    MorphosyntacticType.NUMBER_SUFFIX: LauvinkoWordType.NUMBER_SUFFIX,
    MorphosyntacticType.SEX_SUFFIX: LauvinkoWordType.SEX_SUFFIX,
}


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

        elif morphemes[0].lemma.mstype in PARTICLE_MSTYPES:
            return LauvinkoParticle.from_morphemes(morphemes)

        else:
            raise NotImplementedError

    @staticmethod
    def join_syntactic_words(words: List["LauvinkoWord"]) -> "LauvinkoSurfaceForm":
        if len(words) == 1:
            return words[0].surface_form()

        accented = 0
        i = 0
        found = False
        context: Optional[MorphemeContext] = None

        if words[i].word_type() is LauvinkoWordType.CONTENT_WORD:
            found = True
            context = words[i]._as_morph.context
            i += 1

        if words[i:] and words[i].word_type() is LauvinkoWordType.ADPOSITION:
            found = False
            i += 1

        if words[i:] and words[i].word_type() is LauvinkoWordType.CONTENT_WORD:
            found = True
            accented = i
            context = words[i]._as_morph.context
            i += 1

        if words[i:] and words[i].word_type() is LauvinkoWordType.SEX_SUFFIX:
            i += 1

        if words[i:] and words[i].word_type() is LauvinkoWordType.DETERMINER:
            if context is not None and context is not words[i]._as_morph.context:
                raise ValueError("Augment must match between content and class word")
            found = True
            i += 1

        if words[i:] and words[i].word_type() is LauvinkoWordType.NUMBER_SUFFIX:
            i += 1

        if not found or i != len(words):
            raise InvalidSyntacticWordSequence(str([w.word_type().value for w in words]))

        return LauvinkoWord.cliticize(
            words=words,
            accented=accented,
        )

    @classmethod
    def cliticize(cls, words: List["LauvinkoWord"], accented: int) -> "LauvinkoSurfaceForm":
        syllables: List[LauvinkoSyllable] = []
        accent_position = None
        falling_accent = None

        for i, word in enumerate(words):
            sf = word.surface_form()

            if len(sf.syllables) == 0:
                if word.word_type() is LauvinkoWordType.DETERMINER:
                    word.apply_case_ending(syllables, accent_position)
                continue

            ms = [
                LauvinkoSyllable(
                    onset=s.onset,
                    vowel=s.vowel,
                    coda=s.coda,
                )
                for s in sf.syllables
            ]

            if ms[0].onset is None:
                if len(syllables) == 0:
                    pass

                elif syllables[-1].coda is LauvinkoConsonant.A:
                    frontness = ms[0].vowel.frontness
                    if ms[0].vowel.frontness is VowelFrontness.MID:
                        syllables[-1].coda = None
                        frontness = syllables[-1].vowel.frontness

                    if frontness is VowelFrontness.FRONT:
                        ms[0].onset = LauvinkoConsonant.Y

                    elif frontness is VowelFrontness.BACK:
                        ms[0].onset = LauvinkoConsonant.V

                    else:
                        raise RuntimeError

                elif syllables[-1].coda is not None:
                    ms[0].onset = syllables[-1].coda
                    syllables[-1].coda = None

                elif syllables[-1].vowel is LauvinkoVowel.A and accent_position != len(syllables):
                    ms[0].onset = syllables[-1].onset
                    del syllables[-1]

                elif ms[0].vowel.frontness == syllables[-1].vowel.frontness and not ms[0].vowel.low:
                    ms[0].vowel = syllables[-1].vowel
                    ms[0].onset = syllables[-1].onset
                    del syllables[-1]

                elif syllables[-1].vowel.frontness is VowelFrontness.FRONT:
                    ms[0].onset = LauvinkoConsonant.Y

                elif syllables[-1].vowel.frontness is VowelFrontness.BACK:
                    ms[0].onset = LauvinkoConsonant.V

            if accented == i:
                accent_position = len(syllables) + sf.accent_position
                falling_accent = sf.falling_accent

            syllables += ms

        if accent_position is None:
            raise ValueError

        return LauvinkoSurfaceForm(
            syllables=syllables,
            accent_position=accent_position,
            falling_accent=falling_accent,
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


PKS = ProtoKasanicSyllable
PKO = ProtoKasanicOnset
PKV = ProtoKasanicVowel

LS = LauvinkoSyllable
LC = LauvinkoConsonant
LV = LauvinkoVowel

CASE_SPELLING_SYLLABLES: dict[str, Optional[tuple[ProtoKasanicOnset, ProtoKasanicVowel]]] = {
    LauvinkoCase.AGENTIVE.abbreviation: None,
    LauvinkoCase.INSTRUMENTAL.abbreviation: (PKO.K, PKV.A),
    LauvinkoCase.PATIENTIVE.abbreviation: None,
    LauvinkoCase.ALLATIVE.abbreviation: (None, PKV.I),
    LauvinkoCase.LOCATIVE.abbreviation: (None, PKV.U),
    LauvinkoCase.ABLATIVE.abbreviation: (None, PKV.U),
    LauvinkoCase.PERLATIVE.abbreviation: (PKO.M, PKV.I),
    LauvinkoCase.PARTITIVE.abbreviation: (None, PKV.E),
}


ANIMATES = {"1excl", "1incl", "2fam", "2fml", "2hon", "3rd", "hea"}

PARTITIVE_NUMBERS = {
    "hea": "pl",
    "bra": "du",
    "lea": "pl",
    "rck": "sg",
    "sea": None,
}

IRREGULAR_CLASS_WORDS: dict[tuple[str, str], tuple[Optional[list[ProtoKasanicSyllable]], list[LauvinkoSyllable], bool]] = {
    ("$1excl$.$sg$", LauvinkoCase.GENITIVE.abbreviation): (
        [PKS(None, PKV.O), PKS(PKO.N, PKV.I)], [LS(None, LV.O), LS(LC.N, LV.I)], False,
    ),
    ("$1incl$.$pl$", LauvinkoCase.GENITIVE.abbreviation): (
        [PKS(PKO.P, PKV.AA), PKS(PKO.N, PKV.I)], [LS(LC.P, LV.A), LS(LC.N, LV.I)], False,
    ),
    ("$2fam$.$sg$", LauvinkoCase.GENITIVE.abbreviation): (
        None, [LS(LC.L, LV.I)], False,
    ),
    # TODO: What's up with the 2nd person plural pronoun?
    ("$2hon$", LauvinkoCase.GENITIVE.abbreviation): (
        [PKS(PKO.N, PKV.AA), PKS(None, PKV.I)], [LS(LC.N, LV.A, LC.Y)], False,
    ),
    ("$3rd$.$sg$", LauvinkoCase.GENITIVE.abbreviation): (
        [PKS(PKO.R, PKV.I), PKS(PKO.N, PKV.A)], [LS(LC.L, LV.I, LC.N)], False,
    ),
    # TODO: Also the 3rd person plural?

    ("$bra$.$sg$", LauvinkoCase.INSTRUMENTAL.abbreviation): (
        [PKS(None, PKV.I), PKS(PKO.K, PKV.A)], [LS(None, LV.I, LC.K)], True,
    ),
    ("$bra$.$du$", LauvinkoCase.INSTRUMENTAL.abbreviation): (
        [PKS(PKO.M, PKV.E), PKS(PKO.K, PKV.A)], [LS(LC.M, LV.E, LC.K)], True,
    ),
    ("$bra$.$pl$", LauvinkoCase.INSTRUMENTAL.abbreviation): (
        [PKS(None, PKV.O), PKS(PKO.K, PKV.A)], [LS(None, LV.O, LC.K)], True,
    ),

    ("$lea$.$sg$", LauvinkoCase.ABLATIVE.abbreviation): (
        None, [LS(None, LV.O), LS(LC.V, LV.O)], False,
    ),
}


def _add_case_vowel(lv_syllables: list[LauvinkoSyllable], accent_position: int, vowel: LauvinkoVowel):
    if lv_syllables[-1].coda is None:
        if lv_syllables[-1].vowel.frontness is vowel.frontness:
            # TODO: Consider removal once irregularly-spelled pronouns are implemented
            if ((vowel is LauvinkoVowel.I) and (lv_syllables[-1].vowel is LauvinkoVowel.E)
                    and accent_position < (len(lv_syllables) - 1)):
                lv_syllables[-1].vowel = LauvinkoVowel.I
        else:
            lv_syllables[-1].coda = OFFGLIDES[vowel.frontness]

    elif lv_syllables[-1].coda is LauvinkoConsonant.A:
        raise NotImplementedError

    else:
        syll = LauvinkoSyllable(
            onset=lv_syllables[-1].coda,
            vowel=vowel,
            coda=None,
        )
        lv_syllables[-1].coda = None
        lv_syllables.append(syll)


def _add_case_consonant(lv_syllables: list[LauvinkoSyllable], consonant: LauvinkoConsonant):
    if lv_syllables[-1].coda is None:
        lv_syllables[-1].coda = consonant

    elif lv_syllables[-1].coda is LauvinkoConsonant.A:
        raise NotImplementedError

    else:
        syll = LauvinkoSyllable(
            onset=lv_syllables[-1].coda,
            vowel=LauvinkoVowel.A,
            coda=consonant,
        )
        lv_syllables[-1].coda = None
        lv_syllables.append(syll)


def _add_partitive_suffix(lv_syllables: list[LauvinkoSyllable], definite: bool):
    coda = LauvinkoConsonant.S if definite else None

    if lv_syllables[-1].coda is None:
        lv_syllables.append(LauvinkoSyllable(onset=LauvinkoConsonant.Y, vowel=LauvinkoVowel.E, coda=coda))
    elif lv_syllables[-1].coda is LauvinkoConsonant.A:
        raise NotImplementedError
    else:
        syll = LauvinkoSyllable(
            onset=lv_syllables[-1].coda,
            vowel=LauvinkoVowel.E,
            coda=coda,
        )
        lv_syllables[-1].coda = None
        lv_syllables.append(syll)

@dataclass
class LauvinkoClassWord(LauvinkoWord):
    class_word: LauvinkoMorpheme
    case_suffix: Optional[LauvinkoMorpheme]
    definite_suffix: Optional[LauvinkoMorpheme]

    def __post_init__(self):
        assert self.class_word.lemma.mstype is MorphosyntacticType.CLASS_WORD

        if self.case_suffix is not None:
            assert self.case_suffix.lemma.mstype is MorphosyntacticType.ADPOSITION

            expected_augment = self.case().augment

            if expected_augment is None:
                expected_augment = self.animate()

            if expected_augment:
                assert self.class_word.context is MorphemeContext.AUGMENTED
            else:
                assert self.class_word.context is MorphemeContext.NONAUGMENTED

        if self.case() is LauvinkoCase.PARTITIVE:
            person, number = self.pn()
            assert number == PARTITIVE_NUMBERS.get(person, number)

        if self.definite_suffix is not None:
            assert self.definite_suffix.lemma.mstype is MorphosyntacticType.DEFINITE_MARKER

            # The head class word is inherently indefinite, definite referents use $3rd$ class words
            assert not self.class_word.lemma.ident.startswith("$hea$")

            assert self.case_suffix is not None
            assert self.case_suffix.lemma.ident == f"${LauvinkoCase.PARTITIVE.abbreviation}$"

        self._as_morph = self._generate_morph()

    def case(self) -> Optional[LauvinkoCase]:
        if self.case_suffix is None:
            return None
        return CASE_BY_IDENT[self.case_suffix.lemma.ident]

    def pn(self) -> tuple[str, Optional[str]]:
        parts = self.class_word.lemma.ident.split(".")
        labels = [
            re.match(r"\$([0-9a-z]+)\$", part).group(1)
            for part in parts
        ]
        return tuple(labels) if len(labels) == 2 else (labels[0], None)

    def animate(self) -> bool:
        person, number = self.pn()
        return person in ANIMATES

    def apply_case_ending(self, lv_syllables: list[LauvinkoSyllable], accent_position: int):
        case = self.case()

        if case is None:
            pass
        elif case in (LauvinkoCase.AGENTIVE, LauvinkoCase.PATIENTIVE):
            pass
        elif case is LauvinkoCase.INSTRUMENTAL:
            _add_case_consonant(lv_syllables, LauvinkoConsonant.K)
        elif case is LauvinkoCase.GENITIVE:
            if self.animate():
                # TODO: How attached am I to the stray anusvara?
                _add_case_vowel(lv_syllables, accent_position, LauvinkoVowel.I)
            else:
                _add_case_consonant(lv_syllables, LauvinkoConsonant.N)
        elif case is LauvinkoCase.ALLATIVE:
            _add_case_vowel(lv_syllables, accent_position, LauvinkoVowel.I)
        elif case in (LauvinkoCase.LOCATIVE, LauvinkoCase.ABLATIVE):
            _add_case_vowel(lv_syllables, accent_position, LauvinkoVowel.O)
        elif case is LauvinkoCase.PERLATIVE:
            lv_syllables.append(LauvinkoSyllable(onset=LauvinkoConsonant.M, vowel=LauvinkoVowel.I, coda=None))
        elif case is LauvinkoCase.PARTITIVE:
            _add_partitive_suffix(lv_syllables, self.definite_suffix is not None)
        else:
            raise NotImplementedError

    def _case_spelling(self) -> ProtoKasanicSyllable:
        case = self.case()

        if case is LauvinkoCase.GENITIVE:
            if self.animate():
                tup = (None, PKV.I)
            else:
                tup = (PKO.N, PKV.A)
        else:
            tup = CASE_SPELLING_SYLLABLES[case.abbreviation]

        return tup and ProtoKasanicSyllable(*tup)

    def _generate_morph(self) -> "LauvinkoMorpheme":
        case = self.case()
        if case is None:
            return self.class_word

        pk_syllables: list[ProtoKasanicSyllable] = [*self.class_word.virtual_original_form.surface_form.syllables]
        syll = self._case_spelling()
        syll and pk_syllables.append(syll)

        if self.definite_suffix is not None:
            pk_syllables.append(*self.definite_suffix.virtual_original_form.surface_form.syllables)

        accent_position = self.class_word.surface_form.accent_position
        falling_accent = self.class_word.surface_form.falling_accent

        tup = (self.class_word.lemma.ident, case.abbreviation)
        if tup in IRREGULAR_CLASS_WORDS:
            pks, lv_syllables, falling_accent = IRREGULAR_CLASS_WORDS[tup]
            if pks is not None:
                pk_syllables = pks

        else:
            lv_syllables: list[LauvinkoSyllable] = [
                LauvinkoSyllable(
                    onset=s.onset,
                    vowel=s.vowel,
                    coda=s.coda,
                )
                for s in self.class_word.surface_form.syllables
            ]

            if len(lv_syllables) > 0:
                self.apply_case_ending(lv_syllables, accent_position)

        return LauvinkoMorpheme(
            lemma=None,
            surface_form=LauvinkoSurfaceForm(
                syllables=lv_syllables,
                accent_position=accent_position,
                falling_accent=falling_accent,
            ),
            virtual_original_form=ProtoKasanicMorpheme(
                lemma=None,
                surface_form=PKSurfaceForm(
                    syllables=pk_syllables,
                    stress_position=self.class_word.virtual_original_form.surface_form.stress_position,
                ),
                end_mutation=None,
            ),
            context=self.class_word.context,
        )

    def word_type(self) -> LauvinkoWordType:
        return LauvinkoWordType.DETERMINER

    @classmethod
    def from_morphemes(cls, morphemes: List[LauvinkoMorpheme]) -> "LauvinkoClassWord":
        class_word = morphemes[0]
        case_suffix = None
        definite_suffix = None

        if len(morphemes) >= 2:
            case_suffix = morphemes[1]
        if len(morphemes) == 3:
            definite_suffix = morphemes[2]

        return cls(class_word, case_suffix, definite_suffix)

@dataclass
class LauvinkoParticle(LauvinkoWord):
    morpheme: LauvinkoMorpheme

    def __post_init__(self):
        super().__post_init__()
        assert self.morpheme.lemma.mstype in PARTICLE_MSTYPES

    def _get_accented(self):
        return None

    def morphemes(self) -> List[LauvinkoMorpheme]:
        return [self.morpheme]

    def word_type(self) -> LauvinkoWordType:
        return PARTICLE_MSTYPES[self.morpheme.lemma.mstype]

    @classmethod
    def from_morphemes(cls, morphemes: List[LauvinkoMorpheme]) -> "LauvinkoParticle":
        if len(morphemes) == 1:
            return cls(*morphemes)
        else:
            raise ValueError
