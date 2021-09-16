from random import randrange
from ..shared.semantics import PrimaryTenseAspect, KasanicStemCategory
from .phonology import ProtoKasanicOnset, ProtoKasanicVowel, ProtoKasanicSyllable
from .morphology import ProtoKasanicMorpheme, ProtoKasanicLemma


class WeightedRandomizer:
    def __init__(self, items: dict):
        self.items = items
        self.total_weight = sum(items.values())

    def draw(self):
        n = 0
        stop_at = randrange(self.total_weight)

        for value, weight in self.items.items():
            n += weight

            if n > stop_at:
                return value


CONSONANT_WEIGHTS = {
    ProtoKasanicOnset.M: 46,
    ProtoKasanicOnset.N: 100,
    ProtoKasanicOnset.NY: 24,
    ProtoKasanicOnset.NG: 31,
    ProtoKasanicOnset.NGW: 8,

    ProtoKasanicOnset.P: 18,
    ProtoKasanicOnset.T: 77,
    ProtoKasanicOnset.C: 35,
    ProtoKasanicOnset.K: 88,
    ProtoKasanicOnset.KW: 11,

    ProtoKasanicOnset.MP: 6,
    ProtoKasanicOnset.NT: 27,
    ProtoKasanicOnset.NC: 7,
    ProtoKasanicOnset.NK: 16,
    ProtoKasanicOnset.NKW: 4,

    ProtoKasanicOnset.PP: 6,
    ProtoKasanicOnset.TT: 14,
    ProtoKasanicOnset.CC: 10,
    ProtoKasanicOnset.KK: 21,
    ProtoKasanicOnset.KKW: 5,

    ProtoKasanicOnset.S: 68,
    ProtoKasanicOnset.H: 12,

    ProtoKasanicOnset.R: 40,
    ProtoKasanicOnset.Y: 52,
    ProtoKasanicOnset.W: 59,
}

initial_consonant_raffle = WeightedRandomizer({
    **CONSONANT_WEIGHTS,
    None: 150
})

medial_consonant_raffle = WeightedRandomizer({
    **CONSONANT_WEIGHTS,
    None: 30,
})


vowel_raffle = WeightedRandomizer({
    ProtoKasanicVowel.AA: 100,
    ProtoKasanicVowel.E: 72,
    ProtoKasanicVowel.O: 61,
    ProtoKasanicVowel.A: 52,
    ProtoKasanicVowel.I: 85,
    ProtoKasanicVowel.U: 44,
    ProtoKasanicVowel.AI: 32,
    ProtoKasanicVowel.AU: 27,
})


underspecified_vowel_raffle = WeightedRandomizer({
    ProtoKasanicVowel.LOW: 5,
    ProtoKasanicVowel.HIGH: 3,
})


syllable_count_raffle = WeightedRandomizer({
    2: 3,
    3: 7,
    4: 2,
})


def random_pk_lemma(category: KasanicStemCategory) -> ProtoKasanicLemma:
    syllables = []
    syllable_count = syllable_count_raffle.draw()

    while len(syllables) < syllable_count:
        if len(syllables) == 0:
            onset = initial_consonant_raffle.draw()
        else:
            onset = medial_consonant_raffle.draw()

        if (len(syllables) == 0) and (PrimaryTenseAspect.GENERAL not in category.primary_aspects):
            vowel = underspecified_vowel_raffle.draw()
        else:
            vowel = vowel_raffle.draw()

        try:
            syllables.append(ProtoKasanicSyllable(onset, vowel))
        except ProtoKasanicSyllable.InvalidSyllable:
            pass  # no big deal if the onset and vowel don't match up, try try again (should be rare)

    return ProtoKasanicLemma(
        category=category,
        definition=None,
        forms={},
        generic_morph=ProtoKasanicMorpheme(
            syllables=syllables,
            end_mutation=None,
        )
    )
