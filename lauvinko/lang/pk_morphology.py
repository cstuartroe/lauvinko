from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import regex
from .semantics import PrimaryTenseAspect, KasanicStemCategory
from .pk_phonology import (
    ProtoKasanicOnset,
    VowelFrontness,
    ProtoKasanicVowel,
    ProtoKasanicSyllable,
    ProtoKasanicMutation,
    PKSurfaceForm,
)


@dataclass
class ProtoKasanicMorpheme:
    syllables: List[ProtoKasanicSyllable]
    end_mutation: Optional[ProtoKasanicMutation]

    def __post_init__(self):
        for syllable in self.syllables[1:]:
            if syllable.vowel.frontness is VowelFrontness.UNDERSPECIFIED:
                raise ProtoKasanicSyllable.InvalidSyllable(f"Non-initial vowel is underspecified: {self.syllables}")

    def surface_form(self, stress_position=0):
        return ProtoKasanicMorpheme.join([self], stress_position)

    class InvalidTranscription(ValueError):
        pass

    @staticmethod
    def _from_informal_transcription(transcription: str):
        m = regex.fullmatch("(([mngptckshryw']{0,3})([aeiou@~]{1,2}))*(\\+[FLN])?", transcription)

        if m is None:
            raise ProtoKasanicMorpheme.InvalidTranscription("Transcription does not match regex")

        syllables = []
        for o_str, v_str in zip(m.captures(2), m.captures(3)):
            if o_str in {"", "'"}:
                onset = None
            else:
                try:
                    onset = ProtoKasanicOnset[o_str.upper()]
                except KeyError:
                    raise ProtoKasanicMorpheme.InvalidTranscription("Invalid onset: " + o_str)

            UNDERSPECIFIED_VOWELS = {
                "@": ProtoKasanicVowel.LOW,
                "~": ProtoKasanicVowel.HIGH,
            }

            try:
                vowel = UNDERSPECIFIED_VOWELS.get(v_str) or ProtoKasanicVowel[v_str.upper()]
            except KeyError:
                raise ProtoKasanicMorpheme.InvalidTranscription("Invalid vowel: " + v_str)

            syllables.append(ProtoKasanicSyllable(onset, vowel))

        mutations = {
            "+F": ProtoKasanicMutation.FORTITION,
            "+L": ProtoKasanicMutation.LENITION,
            "+N": ProtoKasanicMutation.NASALIZATION,
        }

        mutation = mutations.get(m.group(4))

        # I need a separate function
        return syllables, mutation

    @classmethod
    def from_informal_transcription(cls, transcription: str):
        return ProtoKasanicMorpheme(*cls._from_informal_transcription(transcription))

    class StressedZeroMorpheme(ValueError):
        pass

    @staticmethod
    def join(morphemes: List["ProtoKasanicMorpheme"], stressed: int) -> PKSurfaceForm:
        syllables = []
        stress_position = None
        active_mutation = None

        for i, morpheme in enumerate(morphemes):
            if len(morpheme.syllables) == 0:
                if stressed == i:
                    raise ProtoKasanicMorpheme.StressedZeroMorpheme

                # Zero morphemes may still apply a mutation, which overrides any previous mutation
                active_mutation = morpheme.end_mutation or active_mutation

                continue

            if stressed == i:
                stress_position = len(syllables)

            syllables_to_add = [*morpheme.syllables]
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
REDUPLICATOR = ProtoKasanicMorpheme([], None)

TENSE_ASPECT_PREFIXES = {
    PrimaryTenseAspect.INCEPTIVE: pkm("i+N"),
    PrimaryTenseAspect.FREQUENTATIVE_NONPAST: REDUPLICATOR,
    PrimaryTenseAspect.FREQUENTATIVE_PAST:    REDUPLICATOR,
}


@dataclass
class ProtoKasanicStem:
    primary_prefix: Optional[ProtoKasanicMorpheme]
    main_morpheme: ProtoKasanicMorpheme


class ProtoKasanicLemma:
    def __init__(
            self,
            category: KasanicStemCategory,
            generic_morph: ProtoKasanicMorpheme,
            definition: str,
            irregular_forms: dict[PrimaryTenseAspect, ProtoKasanicStem] = None
    ):
        if PrimaryTenseAspect.GENERAL in category.primary_aspects:
            if generic_morph.syllables[0].vowel.frontness is VowelFrontness.UNDERSPECIFIED:
                raise AblautMismatch(f"{category} generic form must not include ablaut vowel: {generic_morph}")

        else:
            if generic_morph.syllables[0].vowel.frontness is not VowelFrontness.UNDERSPECIFIED:
                raise AblautMismatch(f"{category} generic form must include ablaut vowel: {generic_morph}")

        self.category = category
        self.generic_morph = generic_morph
        self.definition = definition
        self.forms: dict[PrimaryTenseAspect, ProtoKasanicStem] = irregular_forms or {}

    def form(self, primary_ta: PrimaryTenseAspect) -> ProtoKasanicStem:
        if primary_ta not in self.forms:
            self.forms[primary_ta] = self._generate_form(primary_ta)

        return self.forms[primary_ta]

    def _generate_form(self, primary_ta: PrimaryTenseAspect) -> ProtoKasanicStem:

        generic_first_syllable = self.generic_morph.syllables[0]

        ablauts = LOW_ABLAUTS if generic_first_syllable.vowel.low else HIGH_ABLAUTS
        if ablauts[primary_ta] is None:
            form_first_syllable = generic_first_syllable
        else:
            form_first_syllable = ProtoKasanicSyllable(
                onset=generic_first_syllable.onset,
                vowel=ablauts[primary_ta],
            )

        main = ProtoKasanicMorpheme(
            syllables=([form_first_syllable, *self.generic_morph.syllables[1:]]),
            end_mutation=self.generic_morph.end_mutation,
        )

        prefix: Optional[ProtoKasanicMorpheme] = TENSE_ASPECT_PREFIXES.get(primary_ta, None)

        return ProtoKasanicStem(primary_prefix=prefix, main_morpheme=main)

    def citation_form(self):
        return self.form(self.category.citation_form)


class PKPrefix(ProtoKasanicMorpheme, Enum):
    def gloss_keyname(self) -> str:
        if self.name.endswith("_"):
            return f"${self[:-1].lower()}$"
        else:
            return self.name.lower()


class PKModalPrefix(PKPrefix):
    IF = _pkm("tti+L")
    IN_ORDER = _pkm("ki+L")
    THUS = _pkm("iwo+F")
    AFTER = _pkm("nyinyi")
    SWRF_ = _pkm("o+N")
    NOT = _pkm("aara")
    AGAIN = _pkm("tere")
    WANT = _pkm("ewa")
    LIKE = _pkm("mika")
    CAN = _pkm("so+N")
    MUST = _pkm("nosa+L")
    VERY = _pkm("kora")
    BUT = _pkm("caa")


class PKTertiaryAspectPrefix(PKPrefix):
    PRO_ = _pkm("mpi")
    EXP_ = _pkm("raa+F")


class PKTopicAgreementPrefix(PKPrefix):
    T1S_ = _pkm("na")
    T1P = _pkm("ta")
    T2S = _pkm("i+F")
    T2P = _pkm("e+F")
    T3AS = _pkm("")
    T3AP = _pkm("aa")
    T3IS = _pkm("sa")
    T3IP = _pkm("aasa")


class PKTopicCasePrefix(PKPrefix):
    TVOL_ = _pkm("")
    TDAT_ = _pkm("pa+N")
    TLOC_ = _pkm("posa")
    DEP_ = _pkm("eta")


@dataclass
class PKWord:
    stem: ProtoKasanicStem
    modal_prefixes: List[PKModalPrefix]
    tertiary_aspect: Optional[PKTertiaryAspectPrefix]
    topic_agreement: Optional[PKTopicAgreementPrefix]
    topic_case: Optional[PKTopicCasePrefix]

    class MorphemeOrderError(ValueError):
        pass

    def morphemes(self):
        out = [*self.modal_prefixes]

        for m in self.tertiary_aspect, self.topic_agreement, self.topic_agreement, self.stem.primary_prefix:
            if m is not None:
                out.append(m)

        out.append(self.stem.main_morpheme)

        return out

    def surface_form(self):
        ms = self.morphemes()
        return ProtoKasanicMorpheme.join(
            ms,
            len(ms) - 1,
        )

    @staticmethod
    def bucket_prefixes(prefixes: List[PKPrefix]):
        modal_prefixes: List[PKModalPrefix] = []
        tertiary_aspect: Optional[PKTertiaryAspectPrefix] = None
        topic_agreement: Optional[PKTopicAgreementPrefix] = None
        topic_case: Optional[PKTopicCasePrefix] = None

        i = 0
        while (i < len(prefixes)) and (prefixes[i] in PKModalPrefix):
            modal_prefixes.append(prefixes[i])
            i += 1

        if i < len(prefixes) and prefixes[i] in PKTertiaryAspectPrefix:
            tertiary_aspect = prefixes[i]
            i += 1

        if i < len(prefixes) and prefixes[i] in PKTopicAgreementPrefix:
            topic_agreement = prefixes[i]
            i += 1

        if i < len(prefixes) and prefixes[i] in PKTopicCasePrefix:
            topic_case = prefixes[i]
            i += 1

        if i < len(prefixes):
            raise PKWord.MorphemeOrderError("Invalid or out of order prefix: " + prefixes[i].gloss_keyname())

        return {
            "modal_prefixes": modal_prefixes,
            "tertiary_aspect": tertiary_aspect,
            "topic_agreement": topic_agreement,
            "topic_case": topic_case,
        }

