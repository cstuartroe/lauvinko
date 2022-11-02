from dataclasses import dataclass
from typing import List, Optional
import regex
from lauvinko.lang.shared.semantics import PrimaryTenseAspect, KasanicStemCategory, PTA2ABBREV
from lauvinko.lang.shared.morphology import Morpheme, Lemma, Word, bucket_kasanic_prefixes, MorphosyntacticType
from .phonology import (
    ProtoKasanicOnset,
    VowelFrontness,
    ProtoKasanicVowel,
    ProtoKasanicSyllable,
    ProtoKasanicMutation,
    PKSurfaceForm,
)
from .romanize import falavay, romanize


MUTATION_NOTATION = {
    "+F": ProtoKasanicMutation.FORTITION,
    "+L": ProtoKasanicMutation.LENITION,
    "+N": ProtoKasanicMutation.NASALIZATION,
}

UNDERSPECIFIED_VOWELS = {
    "@": ProtoKasanicVowel.LOW,
    "~": ProtoKasanicVowel.HIGH,
}


def reverse(d: dict, val):
    for k, v in d.items():
        if v is val:
            return k


@dataclass
class ProtoKasanicMorpheme(Morpheme):
    lemma: Optional["ProtoKasanicLemma"]
    surface_form: PKSurfaceForm
    end_mutation: Optional[ProtoKasanicMutation]

    class InvalidTranscription(ValueError):
        pass

    @classmethod
    def from_informal_transcription(cls, transcription: str, stress_position: Optional[int] = -1) -> "ProtoKasanicMorpheme":
        return cls(
            lemma=None,
            **cls._from_informal_transcription(transcription, stress_position=stress_position),
        )

    def informal_transcription(self):
        out = ""

        for syll in self.surface_form.syllables:
            if syll.onset is not None:
                out += syll.onset.name.lower()

            if syll.vowel.frontness is VowelFrontness.UNDERSPECIFIED:
                out += reverse(UNDERSPECIFIED_VOWELS, syll.vowel)
            else:
                out += syll.vowel.name.lower()

        mut = reverse(MUTATION_NOTATION, self.end_mutation)
        if mut is not None:
            out += mut

        return out

    @staticmethod
    def _from_informal_transcription(transcription: str, stress_position: Optional[int] = -1):
        m = regex.fullmatch("(([mngptckshryw']{0,3})([aeiou@~]{1,2})(/?))*(\\+[FLN])?", transcription)

        if m is None:
            raise ProtoKasanicMorpheme.InvalidTranscription("Transcription does not match regex: " + transcription)

        syllables = []
        for i, (o_str, v_str, s_str) in enumerate(zip(m.captures(2), m.captures(3), m.captures(4))):
            if o_str in {"", "'"}:
                onset = None
            else:
                try:
                    onset = ProtoKasanicOnset[o_str.upper()]
                except KeyError:
                    raise ProtoKasanicMorpheme.InvalidTranscription("Invalid onset: " + o_str)

            try:
                vowel = UNDERSPECIFIED_VOWELS.get(v_str) or ProtoKasanicVowel[v_str.upper()]
            except KeyError:
                raise ProtoKasanicMorpheme.InvalidTranscription("Invalid vowel: " + v_str)

            syllables.append(ProtoKasanicSyllable(onset, vowel))

            if s_str:
                if stress_position == -1:
                    stress_position = i
                else:
                    raise ProtoKasanicMorpheme.InvalidTranscription(
                        f"Stress already set {transcription} {stress_position}")

        mutation = MUTATION_NOTATION.get(m.group(5))

        if stress_position == -1:
            stress_position = None if len(syllables) == 0 else 0

        return {
            "surface_form": PKSurfaceForm(
                syllables=syllables,
                stress_position=stress_position
            ),
            "end_mutation": mutation,
        }

    @staticmethod
    def join(morphemes: List["ProtoKasanicMorpheme"], stressed: Optional[int]) -> PKSurfaceForm:
        syllables = []
        stress_position = None
        active_mutation = None

        for i, morpheme in enumerate(morphemes):
            ms = morpheme.surface_form.syllables

            if stressed == i:
                stress_position = len(syllables) + morpheme.surface_form.stress_position

            if morpheme is REDUPLICATOR:
                syllables_to_add = morphemes[i + 1].surface_form.syllables[:1]

            elif len(ms) == 0 and morpheme:
                # Zero morphemes may still apply a mutation, which overrides any previous mutation
                active_mutation = morpheme.end_mutation or active_mutation

                continue

            elif i > 0 and morphemes[i-1] is REDUPLICATOR and ms[0].onset is None:
                syllables_to_add = [
                    ProtoKasanicSyllable(
                        onset=ms[1].onset,
                        vowel=ms[0].vowel,
                    ),
                    *ms[1:],
                ]


            else:
                syllables_to_add = [*ms]

            if active_mutation is not None:
                syllables_to_add[0] = ProtoKasanicSyllable(
                    onset=active_mutation.mutate(syllables_to_add[0].onset),
                    vowel=syllables_to_add[0].vowel,
                )

            syllables += syllables_to_add

            active_mutation = morpheme.end_mutation

        return PKSurfaceForm(syllables=syllables, stress_position=stress_position)


# just for ease of typing
_pkm = ProtoKasanicMorpheme._from_informal_transcription
pkm = ProtoKasanicMorpheme.from_informal_transcription


LOW_ABLAUTS: dict[PrimaryTenseAspect, ProtoKasanicVowel] = {
    PrimaryTenseAspect.GENERAL: None,
    PrimaryTenseAspect.NONPAST: ProtoKasanicVowel.E,
    PrimaryTenseAspect.PAST: ProtoKasanicVowel.O,
    PrimaryTenseAspect.IMPERFECTIVE_NONPAST: ProtoKasanicVowel.AA,
    PrimaryTenseAspect.IMPERFECTIVE_PAST: ProtoKasanicVowel.O,
    PrimaryTenseAspect.PERFECTIVE: ProtoKasanicVowel.E,
    PrimaryTenseAspect.INCEPTIVE: ProtoKasanicVowel.AA,
    PrimaryTenseAspect.FREQUENTATIVE_NONPAST: ProtoKasanicVowel.E,
    PrimaryTenseAspect.FREQUENTATIVE_PAST: ProtoKasanicVowel.O,
}

assert (v.low for v in LOW_ABLAUTS.values())

HIGH_ABLAUTS: dict[PrimaryTenseAspect, ProtoKasanicVowel] = {}

for ta, v in LOW_ABLAUTS.items():
    if v is None:
        HIGH_ABLAUTS[ta] = None
    else:
        HIGH_ABLAUTS[ta] = ProtoKasanicVowel.shift_height(v, low=False)


class AblautMismatch(ValueError):
    pass


# A special nonce morpheme that represents reduplication of the following syllable
REDUPLICATOR = ProtoKasanicMorpheme(
    surface_form=PKSurfaceForm(syllables=[], stress_position=None),
    end_mutation=None,
    lemma=None,
)

TENSE_ASPECT_PREFIXES = {
    PrimaryTenseAspect.INCEPTIVE: pkm("i+N"),
    PrimaryTenseAspect.FREQUENTATIVE_NONPAST: REDUPLICATOR,
    PrimaryTenseAspect.FREQUENTATIVE_PAST:    REDUPLICATOR,
}


@dataclass
class ProtoKasanicStem:
    primary_prefix: Optional[ProtoKasanicMorpheme]
    main_morpheme: ProtoKasanicMorpheme

    def morphemes(self) -> List[ProtoKasanicMorpheme]:
        if self.primary_prefix is None:
            return [self.main_morpheme]
        else:
            return [self.primary_prefix, self.main_morpheme]

    def surface_form(self) -> PKSurfaceForm:
        if self.main_morpheme.surface_form.stress_position is None:
            stressed = None
        else:
            stressed = int(self.primary_prefix is not None)

        return ProtoKasanicMorpheme.join(self.morphemes(), stressed=stressed)

    def as_morph(self) -> ProtoKasanicMorpheme:
        return ProtoKasanicMorpheme(
            lemma=self.main_morpheme.lemma,
            surface_form=self.surface_form(),
            end_mutation=self.main_morpheme.end_mutation,
        )

    def to_json(self):
        sf = self.surface_form()

        return {
            "romanization": romanize(sf),
            "falavay": falavay(sf),
        }


@dataclass
class ProtoKasanicLemma(Lemma):
    ident: str
    category: KasanicStemCategory
    mstype: MorphosyntacticType
    generic_morph: ProtoKasanicMorpheme
    definition: str
    forms: dict[PrimaryTenseAspect, ProtoKasanicStem]

    def __post_init__(self):
        super().__post_init__()

        if len(self.generic_morph.surface_form.syllables) > 0:
            first_vowel = self.generic_morph.surface_form.syllables[0].vowel
        else:
            first_vowel = None

        if PrimaryTenseAspect.GENERAL in self.category.primary_aspects:
            if first_vowel and (first_vowel.frontness is VowelFrontness.UNDERSPECIFIED):
                raise AblautMismatch(f"{self.category} generic form must not include ablaut vowel: {self.generic_morph}")

        else:
            if (first_vowel is None) or (first_vowel.frontness is not VowelFrontness.UNDERSPECIFIED):
                raise AblautMismatch(f"{self.category} generic form must include ablaut vowel: {self.generic_morph}")

        self.forms = self.forms or {}

    def form(self, primary_ta: PrimaryTenseAspect):
        self.check_form_allowed(primary_ta)

        if primary_ta not in self.forms:
            self.forms[primary_ta] = self._generate_form(primary_ta)

        return self.forms[primary_ta]

    def _generate_surface_form(self, primary_ta: PrimaryTenseAspect) -> PKSurfaceForm:
        if len(self.generic_morph.surface_form.syllables) == 0:
            return PKSurfaceForm(
                syllables=[],
                stress_position=None,
            )

        generic_first_syllable = self.generic_morph.surface_form.syllables[0]

        ablauts = LOW_ABLAUTS if generic_first_syllable.vowel.low else HIGH_ABLAUTS
        if ablauts[primary_ta] is None:
            form_first_syllable = generic_first_syllable
        else:
            form_first_syllable = ProtoKasanicSyllable.make_valid(
                onset=generic_first_syllable.onset,
                vowel=ablauts[primary_ta],
            )

        return PKSurfaceForm(
            syllables=([form_first_syllable, *self.generic_morph.surface_form.syllables[1:]]),
            stress_position=self.generic_morph.surface_form.stress_position,
        )

    def _generate_form(self, primary_ta: PrimaryTenseAspect) -> ProtoKasanicStem:
        main = ProtoKasanicMorpheme(
            lemma=self,
            surface_form=self._generate_surface_form(primary_ta),
            end_mutation=self.generic_morph.end_mutation,
        )

        prefix: Optional[ProtoKasanicMorpheme] = TENSE_ASPECT_PREFIXES.get(primary_ta, None)

        return ProtoKasanicStem(primary_prefix=prefix, main_morpheme=main)

    def citation_form(self) -> ProtoKasanicStem:
        return self.form(self.category.citation_form)

    def to_json(self):
        return {
            "forms": {
                PTA2ABBREV[pta]: self.form(pta).to_json()
                for pta in self.category.primary_aspects
            },
            "definition": self.definition,
            "category": self.category.title,
        }


@dataclass
class PKWord(Word):
    modal_prefixes: List[ProtoKasanicMorpheme]
    tertiary_aspect: Optional[ProtoKasanicMorpheme]
    topic_agreement: Optional[ProtoKasanicMorpheme]
    topic_case: Optional[ProtoKasanicMorpheme]
    stem: ProtoKasanicStem

    def morphemes(self) -> List[ProtoKasanicMorpheme]:
        out = [*self.modal_prefixes]

        for m in self.tertiary_aspect, self.topic_agreement, self.topic_case:
            if m is not None:
                out.append(m)

        out += self.stem.morphemes()

        return out

    def surface_form(self):
        return ProtoKasanicMorpheme.join(
            self.morphemes(),
            len(self.morphemes()) - 1,
        )

    @staticmethod
    def from_morphemes(stems: List[ProtoKasanicStem]) -> "PKWord":
        prefixes, stem = stems[:-1], stems[-1]

        prefix_morphemes = [
            prefix.main_morpheme
            for prefix in prefixes
        ]

        return PKWord(
            stem=stem,
            **bucket_kasanic_prefixes(prefix_morphemes),
        )

