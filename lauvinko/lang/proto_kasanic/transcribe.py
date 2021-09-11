from lauvinko.lang.proto_kasanic.phonology import (
    MannerOfArticulation,
    PlaceOfArticulation,
    ProtoKasanicOnset,
    ProtoKasanicVowel,
    ProtoKasanicSyllable,
    PKSurfaceForm,
)

FALAVAY_CONSONANTS: dict[ProtoKasanicOnset, str, str] = {
    ProtoKasanicOnset.M:   "m",
    ProtoKasanicOnset.N:   "n",
    ProtoKasanicOnset.NY:  "N",
    ProtoKasanicOnset.NG:  "g",
    ProtoKasanicOnset.NGW: "m",

    ProtoKasanicOnset.P:  "p",
    ProtoKasanicOnset.T:  "t",
    ProtoKasanicOnset.C:  "j",
    ProtoKasanicOnset.K:  "k",
    ProtoKasanicOnset.KW: "p",

    ProtoKasanicOnset.MP:  "p",
    ProtoKasanicOnset.NT:  "t",
    ProtoKasanicOnset.NC:  "j",
    ProtoKasanicOnset.NK:  "k",
    ProtoKasanicOnset.NKW: "p",

    ProtoKasanicOnset.PP:  "p",
    ProtoKasanicOnset.TT:  "t",
    ProtoKasanicOnset.CC:  "j",
    ProtoKasanicOnset.KK:  "k",
    ProtoKasanicOnset.KKW: "p",

    ProtoKasanicOnset.S: "x",
    ProtoKasanicOnset.H: "h",

    ProtoKasanicOnset.R: "l",
    ProtoKasanicOnset.Y: "y",
    ProtoKasanicOnset.W: "v",
}

FALAVAY_FREE_VOWELS: dict[ProtoKasanicVowel, str] = {
    ProtoKasanicVowel.AA: "A",
    ProtoKasanicVowel.E:  "E",
    ProtoKasanicVowel.O:  "O",
    ProtoKasanicVowel.A:  "Q",
    ProtoKasanicVowel.I:  "I",
    ProtoKasanicVowel.U:  "U",
    ProtoKasanicVowel.AI: "Y",
    ProtoKasanicVowel.AU: "W",
}

FALAVAY_BOUND_VOWELS: dict[ProtoKasanicVowel, tuple[str, str]] = {
    ProtoKasanicVowel.AA: ("",  "a"),
    ProtoKasanicVowel.E:  ("e", ""),
    ProtoKasanicVowel.O:  ("e", "o"),
    ProtoKasanicVowel.A:  ("",  ""),
    ProtoKasanicVowel.I:  ("",  "i"),
    ProtoKasanicVowel.U:  ("",  "u"),
    ProtoKasanicVowel.AI: ("",  "Y"),
    ProtoKasanicVowel.AU: ("",  "W"),
}


AUGMENT_CHAR = "G"
SERIF_CHAR = "q"

SERIF_CONSONANTS = set("hktx")
SERIF_BLOCKING_VOWELS = set("aou")

WIDE_CONSONANTS = set("hklmtxy")
WIDE_VOWELS = {
    "i": "X",
    "u": "Z",
}


def syllable_falavay(syllable: ProtoKasanicSyllable) -> str:
    if syllable.onset is None:
        return FALAVAY_FREE_VOWELS[syllable.vowel]

    if syllable.onset.moa is MannerOfArticulation.PREGLOTTALIZED_STOP:
        pre_diacritic = "H"
    elif syllable.onset.moa is MannerOfArticulation.PRENASALIZED_STOP:
        pre_diacritic = "M"
    else:
        pre_diacritic = ""

    onset_char = FALAVAY_CONSONANTS[syllable.onset]

    pre_vowel, post_vowel = FALAVAY_BOUND_VOWELS[syllable.vowel]

    serif = SERIF_CHAR if (onset_char in SERIF_CONSONANTS and post_vowel not in SERIF_BLOCKING_VOWELS) else ""

    if onset_char in WIDE_CONSONANTS:
        post_vowel = WIDE_VOWELS.get(post_vowel, post_vowel)

    return pre_diacritic + pre_vowel + onset_char + serif + post_vowel


def falavay(form: PKSurfaceForm, augment: bool = False) -> str:
    out = ""

    for i, syllable in enumerate(form.syllables):
        out += syllable_falavay(syllable)
        if i == form.stress_position and augment:
            out += AUGMENT_CHAR

    return out


def transcribe_onset(onset: ProtoKasanicOnset) -> str:
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


def transcribe_vowel(vowel: ProtoKasanicVowel) -> str:
    if vowel is ProtoKasanicVowel.AA:
        return "a"
    elif vowel is ProtoKasanicVowel.A:
        return "ə"
    else:
        return vowel.name.lower()


def transcribe_syllable(syllable: ProtoKasanicSyllable) -> str:
    return transcribe_onset(syllable.onset) + transcribe_vowel(syllable.vowel)


def transcribe(form: PKSurfaceForm, show_stress: bool = False) -> str:
    out = ""

    for i, syllable in enumerate(form.syllables):
        out += transcribe_syllable(syllable)
        if i == form.stress_position and show_stress:
            out += "\u0301" # Combining acute accent

    return out
