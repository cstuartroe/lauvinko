from typing import Optional, List, Iterable
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicLemma, ProtoKasanicMorpheme
from lauvinko.lang.shared.semantics import PrimaryTenseAspect
from lauvinko.lang.shared.phonology import (
    MannerOfArticulation,
    PlaceOfArticulation,
    VowelFrontness,
    GenericCVCSyllable,
)
from lauvinko.lang.proto_kasanic.phonology import (
    ProtoKasanicOnset,
    PKSurfaceForm,
    ProtoKasanicMutation,
    ProtoKasanicVowel,
)
from lauvinko.lang.proto_kasanic.romanize import falavay as pk_falavay
from lauvinko.lang.lauvinko.phonology import LauvinkoConsonant, LauvinkoVowel, LauvinkoSyllable, LauvinkoSurfaceForm
from .base import LauvinkoLemmaOrigin, MorphemeContext


def pk_to_lv_onset(pk_onset: ProtoKasanicOnset):
    """Converts 24 of the 25 Proto-Kasanic onsets to the Lauvinko consonant they would become word-initially.
    Cannot handle the PK prenasalized palatal stop because this becomes the sequence /ant͡s/ word-initially in Lauvinko.
    """
    if pk_onset is ProtoKasanicOnset.NC:
        raise ValueError("Deal with NC another way")

    if pk_onset.moa in {MannerOfArticulation.PREGLOTTALIZED_STOP, MannerOfArticulation.PLAIN_STOP}:
        if pk_onset.poa is PlaceOfArticulation.PALATAL:
            moa = MannerOfArticulation.AFFRICATE
        else:
            moa = MannerOfArticulation.PLAIN_STOP
    elif pk_onset.moa is MannerOfArticulation.PRENASALIZED_STOP:
        moa = MannerOfArticulation.NASAL
    else:
        moa = pk_onset.moa

    if pk_onset.poa is PlaceOfArticulation.PALATAL and pk_onset.moa is not MannerOfArticulation.APPROXIMANT:
        poa = PlaceOfArticulation.ALVEOLAR
    elif pk_onset.poa is PlaceOfArticulation.LABIOVELAR:
        poa = PlaceOfArticulation.LABIAL
    else:
        poa = pk_onset.poa

    return LauvinkoConsonant.find_by(poa=poa, moa=moa)


PK_TO_LV_ONSETS = {
    c: pk_to_lv_onset(c)
    for c in ProtoKasanicOnset
    if c is not ProtoKasanicOnset.NC
}

DIPHTHONG_END = {
    ProtoKasanicVowel.AI: ProtoKasanicVowel.I,
    ProtoKasanicVowel.AU: ProtoKasanicVowel.U,
}

OFFGLIDES = {
    VowelFrontness.FRONT: LauvinkoConsonant.Y,
    VowelFrontness.MID: LauvinkoConsonant.A,
    VowelFrontness.BACK: LauvinkoConsonant.V,
}


def break_pk_consonant(c: ProtoKasanicOnset) -> tuple[Optional[LauvinkoConsonant], Optional[ProtoKasanicOnset]]:
    if c is None:
        return None, None

    elif c.moa is MannerOfArticulation.PRENASALIZED_STOP:
        return LauvinkoConsonant.N, ProtoKasanicOnset.find_by(poa=c.poa, moa=MannerOfArticulation.PLAIN_STOP)

    elif c.moa is MannerOfArticulation.PREGLOTTALIZED_STOP:
        c2 = ProtoKasanicOnset.find_by(poa=c.poa, moa=MannerOfArticulation.PLAIN_STOP)

        if c is ProtoKasanicOnset.CC:
            return LauvinkoConsonant.T, c2
        else:
            return PK_TO_LV_ONSETS[c], c2

    else:
        return None, c


class ProtoKasanicOrigin(LauvinkoLemmaOrigin):
    """Ye gods what a mess of duct tape and brimstone this class is.
    Heaven forbid the need ever arises to change it again.
    Thank the stars above for the test suite.
    """
    def __init__(self, derived_from: ProtoKasanicLemma):
        self.derived_from = derived_from

    def generate_form(self, primary_ta: PrimaryTenseAspect, context: MorphemeContext) \
            -> tuple[LauvinkoSurfaceForm, ProtoKasanicMorpheme]:
        pk_stem = self.derived_from.form(primary_ta)
        pk_sf = pk_stem.surface_form()

        lv_sf = self.evolve_surface_form(pk_sf, context)

        return lv_sf, pk_stem.main_morpheme

    @classmethod
    def evolve_surface_form(cls, pk_sf: PKSurfaceForm, context: MorphemeContext) -> LauvinkoSurfaceForm:
        syllables: Iterable[GenericCVCSyllable] = cls.genericize(pk_sf, context)

        syllables = cls.break_diphthongs(syllables)
        syllables, falling_accent = cls.transform_consonants(syllables, context)
        syllables = cls.remove_h(syllables)
        syllables = cls.reduce_vowels(syllables, context)
        syllables = cls.resolve_vowel_hiatus(syllables)
        syllables = cls.resolve_offglides(syllables)
        syllables = cls.remove_short_vowels(syllables)
        syllables = cls.resolve_offglides(syllables)
        syllables = cls.convert_vowels(syllables)

        lv_syllables, accent_position = cls.degenericize(syllables)

        lv_sf = LauvinkoSurfaceForm(
            syllables=lv_syllables,
            accent_position=accent_position,
            falling_accent=falling_accent,
        )

        if context is MorphemeContext.PREFIXED:
            assert lv_sf.accent_position is None
        else:
            assert (lv_sf.accent_position is None) == (pk_sf.stress_position is None)
            assert (lv_sf.accent_position is None) == (lv_sf.falling_accent is None)

        return lv_sf

    @staticmethod
    def genericize(pk_sf: PKSurfaceForm, context: MorphemeContext) -> List[GenericCVCSyllable]:
        return [
            GenericCVCSyllable(onset=syllable.onset, vowel=syllable.vowel, coda=None,
                               stressed=(i == pk_sf.stress_position and context != MorphemeContext.PREFIXED))
            for i, syllable in enumerate(pk_sf.syllables)
        ]

    @staticmethod
    def break_diphthongs(syllables: Iterable[GenericCVCSyllable]):
        for syllable in syllables:
            if syllable.vowel in {ProtoKasanicVowel.AI, ProtoKasanicVowel.AU}:
                yield GenericCVCSyllable(onset=syllable.onset, vowel=ProtoKasanicVowel.AA, coda=None, stressed=False)
                yield GenericCVCSyllable(onset=None, vowel=DIPHTHONG_END[syllable.vowel], coda=None, stressed=syllable.stressed)
            else:
                yield syllable

    @staticmethod
    def remove_h(syllables: Iterable[GenericCVCSyllable]):
        for i, syllable in enumerate(syllables):
            if syllable.onset is LauvinkoConsonant.H and i > 0:
                syllable.onset = None
            yield syllable

    @staticmethod
    def transform_consonants(syllables: Iterable[GenericCVCSyllable], context: MorphemeContext):
        syllables = list(syllables)
        out_syllables = []
        falling_accent = None

        if syllables[0].onset is ProtoKasanicOnset.NC:
            syllables = [GenericCVCSyllable(
                onset=None,
                vowel=ProtoKasanicVowel.AA,
                coda=None,
                stressed=False,
            )] + syllables

        for i, syllable in enumerate(syllables):
            if syllables[i].stressed:
                falling_accent = context is not MorphemeContext.AUGMENTED

            poststress = i > 0 and syllables[i - 1].stressed
            should_reduce = poststress and context is MorphemeContext.NONAUGMENTED

            if should_reduce:
                if syllable.onset is ProtoKasanicOnset.NC:
                    out_syllables[-1].coda = LauvinkoConsonant.N
                    syllable.onset = LauvinkoConsonant.S
                    falling_accent = False

                else:
                    mutated = syllable.onset and ProtoKasanicMutation.LENITION.mutate(syllable.onset)
                    falling_accent = mutated is syllable.onset
                    syllable.onset = mutated and PK_TO_LV_ONSETS[mutated]

                out_syllables.append(syllable)
                continue

            elif len(out_syllables) > 0:
                out_syllables[-1].coda, syllable.onset = break_pk_consonant(syllable.onset)

            syllable.onset = syllable.onset and PK_TO_LV_ONSETS[syllable.onset]

            out_syllables.append(syllable)

        return out_syllables, falling_accent

    @staticmethod
    def reduce_vowels(syllables: Iterable[GenericCVCSyllable], context: MorphemeContext):
        syllables = list(syllables)

        for i in range(1, len(syllables)):
            if syllables[i - 1].stressed and context is MorphemeContext.NONAUGMENTED:
                syllables[i].vowel = ProtoKasanicVowel.shift_height(syllables[i].vowel, low=False)

        assert syllables[-1].coda is None
        if not syllables[-1].stressed and context is not MorphemeContext.PREFIXED:
            syllables[-1].vowel = ProtoKasanicVowel.shift_height(syllables[-1].vowel, low=False)

        return syllables

    @staticmethod
    def resolve_vowel_hiatus(syllables: Iterable[GenericCVCSyllable]):
        syllables = list(syllables)

        i = 0
        while i < len(syllables):
            if (i + 1 < len(syllables)) and syllables[i + 1].onset is None:
                assert syllables[i].coda is None

                if (i + 2 < len(syllables)) and syllables[i + 2].onset is None:
                    assert syllables[i+1].coda is None

                    if syllables[i+1].stressed:
                        syllables[i+1].stressed = False
                        syllables[i].stressed = True

                    if syllables[i+1].vowel.frontness is not VowelFrontness.MID:
                        syllables[i+2].onset = OFFGLIDES[syllables[i+1].vowel.frontness]

                    del syllables[i+1]
                    continue

                v1, v2, has_coda = syllables[i].vowel, syllables[i+1].vowel, syllables[i+1].coda is not None

                if (syllables[i].stressed or ((not v2.low) and not syllables[i+1].stressed)) and not has_coda:
                    syllables[i].coda = OFFGLIDES[v2.frontness]
                    yield syllables[i]

                elif v1.frontness is VowelFrontness.MID and v2.frontness is VowelFrontness.MID:
                    yield GenericCVCSyllable(
                        onset=syllables[i].onset,
                        vowel=ProtoKasanicVowel.find_by(
                            frontness=VowelFrontness.MID,
                            low=v1.low or v2.low,
                        ),
                        coda=syllables[i + 1].coda,
                        stressed=syllables[i].stressed or syllables[i + 1].stressed,
                    )

                elif v1.frontness is v2.frontness and not v2.low:
                    yield GenericCVCSyllable(
                        onset=syllables[i].onset,
                        vowel=syllables[i].vowel,
                        coda=syllables[i+1].coda,
                        stressed=syllables[i].stressed or syllables[i+1].stressed,
                    )

                else:
                    if v1 is ProtoKasanicVowel.A:
                        yield GenericCVCSyllable(
                            onset=syllables[i].onset,
                            vowel=ProtoKasanicVowel.shift_height(v2, low=True),
                            coda=syllables[i+1].coda,
                            stressed=syllables[i].stressed or syllables[i+1].stressed,
                        )

                    else:
                        if v1 is ProtoKasanicVowel.AA:
                            syllables[i+1].onset = OFFGLIDES[v2.frontness]
                        else:
                            syllables[i+1].onset = OFFGLIDES[v1.frontness]

                        yield syllables[i]
                        yield syllables[i+1]

                i += 2

            else:
                yield syllables[i]
                i += 1

    @staticmethod
    def resolve_offglides(syllables: Iterable[GenericCVCSyllable]):
        for syllable in syllables:
            if syllable.vowel is ProtoKasanicVowel.A and syllable.coda is LauvinkoConsonant.V:
                syllable.vowel = ProtoKasanicVowel.O
                syllable.coda = None

            elif syllable.vowel is ProtoKasanicVowel.A and syllable.coda is LauvinkoConsonant.Y:
                syllable.vowel = ProtoKasanicVowel.E
                syllable.coda = None

            elif syllable.coda is OFFGLIDES[syllable.vowel.frontness]:
                syllable.coda = None

            yield syllable

    @staticmethod
    def remove_short_vowels(syllables: Iterable[GenericCVCSyllable]):
        syllables = list(syllables)
        out_syllables = []

        i = len(syllables) - 1
        while i >= 0:
            if i - 1 >= 0:
                if syllables[i].vowel in {ProtoKasanicVowel.A, ProtoKasanicVowel.U} and \
                        (not syllables[i].stressed) and syllables[i-1].coda is None \
                        and syllables[i].coda is None:
                    out_syllables.append(GenericCVCSyllable(
                        onset=syllables[i-1].onset,
                        vowel=syllables[i-1].vowel,
                        coda=syllables[i].onset,
                        stressed=syllables[i-1].stressed,
                    ))
                    i -= 2
                    continue

                elif syllables[i].onset is OFFGLIDES[syllables[i].vowel.frontness] and not syllables[i].vowel.low:
                    if syllables[i-1].coda is None and syllables[i].coda is None:
                        syllables[i-1].coda = syllables[i].onset
                        syllables[i-1].stressed = syllables[i-1].stressed or syllables[i].stressed
                        out_syllables.append(syllables[i-1])
                        i -= 2
                        continue

                    elif syllables[i-1].coda is None and syllables[i-1].vowel.frontness is syllables[i].vowel.frontness:
                        syllables[i-1].coda = syllables[i].coda
                        assert not syllables[i].stressed
                        out_syllables.append(syllables[i-1])
                        i -= 2
                        continue

            out_syllables.append(syllables[i])
            i -= 1

        out_syllables.reverse()
        return out_syllables

    @staticmethod
    def convert_vowels(syllables: Iterable[GenericCVCSyllable]):
        for syllable in syllables:
            if syllable.vowel is ProtoKasanicVowel.U:
                syllable.vowel = LauvinkoVowel.O if syllable.stressed else LauvinkoVowel.A
            elif syllable.vowel is ProtoKasanicVowel.A:
                syllable.vowel = LauvinkoVowel.E if syllable.stressed else LauvinkoVowel.A
            else:
                syllable.vowel = LauvinkoVowel.find_by(syllable.vowel.low, syllable.vowel.frontness)

            yield syllable

    @staticmethod
    def degenericize(syllables: Iterable[GenericCVCSyllable]) -> tuple[List[LauvinkoSyllable], Optional[bool]]:
        lv_syllables, accent_position = [], None

        for i, syllable in enumerate(syllables):
            lv_syllables.append(LauvinkoSyllable(
                onset=syllable.onset,
                vowel=syllable.vowel,
                coda=syllable.coda,
            ))

            if syllable.stressed:
                accent_position = i

        return lv_syllables, accent_position
