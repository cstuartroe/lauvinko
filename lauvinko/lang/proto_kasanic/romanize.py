from lauvinko.lang.proto_kasanic.phonology import (
    MannerOfArticulation,
    PlaceOfArticulation,
    ProtoKasanicOnset,
    ProtoKasanicVowel,
    ProtoKasanicSyllable,
    PKSurfaceForm,
)

FALAVAY_CONSONANTS: dict[ProtoKasanicOnset, str] = {
    ProtoKasanicOnset.M:   "m",
    ProtoKasanicOnset.N:   "n",
    ProtoKasanicOnset.NY:  "N",
    ProtoKasanicOnset.NG:  "q",
    ProtoKasanicOnset.NGW: "m",

    ProtoKasanicOnset.P:  "p",
    ProtoKasanicOnset.T:  "t",
    ProtoKasanicOnset.C:  "j",
    ProtoKasanicOnset.K:  "k",
    ProtoKasanicOnset.KW: "p",

    ProtoKasanicOnset.MP:  "Mp",
    ProtoKasanicOnset.NT:  "Mt",
    ProtoKasanicOnset.NC:  "Mj",
    ProtoKasanicOnset.NK:  "Mk",
    ProtoKasanicOnset.NKW: "Mp",

    ProtoKasanicOnset.PP:  "Hp",
    ProtoKasanicOnset.TT:  "Ht",
    ProtoKasanicOnset.CC:  "Hj",
    ProtoKasanicOnset.KK:  "Hk",
    ProtoKasanicOnset.KKW: "Hp",

    ProtoKasanicOnset.S: "x",
    ProtoKasanicOnset.H: "h",

    ProtoKasanicOnset.R: "l",
    ProtoKasanicOnset.Y: "y",
    ProtoKasanicOnset.W: "w",

    None: "",
}

FALAVAY_VOWELS: dict[ProtoKasanicVowel, str] = {
    ProtoKasanicVowel.AA: "a",
    ProtoKasanicVowel.E:  "e",
    ProtoKasanicVowel.O:  "o",
    ProtoKasanicVowel.A:  "v",
    ProtoKasanicVowel.I:  "i",
    ProtoKasanicVowel.U:  "u",
    ProtoKasanicVowel.AI: "Y",
    ProtoKasanicVowel.AU: "W",
}


AUGMENT_CHAR = "gv"


def syllable_falavay(syllable: ProtoKasanicSyllable) -> str:
    return FALAVAY_CONSONANTS[syllable.onset] + FALAVAY_VOWELS[syllable.vowel]


def falavay(form: PKSurfaceForm, augment: bool = False) -> str:
    out = ""

    for i, syllable in enumerate(form.syllables):
        out += syllable_falavay(syllable)
        if i == form.stress_position and augment:
            out += AUGMENT_CHAR

    return out


def romanize_onset(onset: ProtoKasanicOnset) -> str:
    if onset is None:
        return ""

    if onset is ProtoKasanicOnset.NY:
        return "ñ"

    cons_str = onset.name.lower()

    if onset.moa is MannerOfArticulation.PREGLOTTALIZED_STOP:
        cons_str = "'" + cons_str[1:]

    elif onset.poa is PlaceOfArticulation.PALATAL:
        cons_str = cons_str.replace("n", "ñ")

    elif onset.poa in {PlaceOfArticulation.VELAR, PlaceOfArticulation.LABIOVELAR}:
        cons_str = cons_str.replace("g", "").replace("n", "ṅ")

    cons_str = cons_str.replace("w", "v")

    return cons_str


def romanize_vowel(vowel: ProtoKasanicVowel) -> str:
    if vowel is ProtoKasanicVowel.AA:
        return "a"
    elif vowel is ProtoKasanicVowel.A:
        return "ə"
    else:
        return vowel.name.lower()


def romanize_syllable(syllable: ProtoKasanicSyllable) -> str:
    return romanize_onset(syllable.onset) + romanize_vowel(syllable.vowel)


def romanize(form: PKSurfaceForm, show_stress: bool = False) -> str:
    out = ""

    for i, syllable in enumerate(form.syllables):
        out += romanize_syllable(syllable)
        if i == form.stress_position and show_stress:
            out += "\u0301" # Combining acute accent

    return out
