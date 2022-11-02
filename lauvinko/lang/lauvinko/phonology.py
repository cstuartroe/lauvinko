from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
from lauvinko.lang.shared.phonology import (
    MannerOfArticulation,
    PlaceOfArticulation,
    Consonant,
    VowelFrontness,
    Vowel,
    Syllable,
    SurfaceForm,
)


class LauvinkoConsonant(Consonant, Enum):
    M = ("m", PlaceOfArticulation.LABIAL, MannerOfArticulation.NASAL)
    N = ("n", PlaceOfArticulation.ALVEOLAR, MannerOfArticulation.NASAL)
    NG = ("ŋ", PlaceOfArticulation.VELAR, MannerOfArticulation.NASAL)

    P = ("p", PlaceOfArticulation.LABIAL, MannerOfArticulation.PLAIN_STOP)
    T = ("t", PlaceOfArticulation.ALVEOLAR, MannerOfArticulation.PLAIN_STOP)
    C = ("t͡s", PlaceOfArticulation.ALVEOLAR, MannerOfArticulation.AFFRICATE)
    K = ("k", PlaceOfArticulation.VELAR, MannerOfArticulation.PLAIN_STOP)

    S = ("s", PlaceOfArticulation.ALVEOLAR, MannerOfArticulation.FRICATIVE)
    H = ("h", PlaceOfArticulation.GLOTTAL, MannerOfArticulation.FRICATIVE)

    L = ("l", PlaceOfArticulation.ALVEOLAR, MannerOfArticulation.APPROXIMANT)
    Y = ("j", PlaceOfArticulation.PALATAL, MannerOfArticulation.APPROXIMANT)
    V = ("ʋ", PlaceOfArticulation.LABIAL, MannerOfArticulation.APPROXIMANT)

    A = ("ɐ̯", None, None)


class LauvinkoVowel(Vowel, Enum):
    A = ('a', True, VowelFrontness.MID)
    E = ('e', True, VowelFrontness.FRONT)
    O = ('o', True, VowelFrontness.BACK)
    I = ('i', False, VowelFrontness.FRONT)



@dataclass
class LauvinkoSyllable(Syllable):
    onset: Optional[LauvinkoConsonant]
    vowel: LauvinkoVowel
    coda: Optional[LauvinkoConsonant] = None

    class InvalidSyllable(ValueError):
        pass

    def __post_init__(self):
        if self.onset is LauvinkoConsonant.A:
            raise LauvinkoSyllable.InvalidSyllable("ɐ̯ cannot be at the beginning of a syllable")

        if self.coda is LauvinkoConsonant.H:
            raise LauvinkoSyllable.InvalidSyllable("h cannot be at the end of a syllable in broad transcription (though it can in narrower transcriptions!)")

        if self.coda is LauvinkoConsonant.V and self.vowel is LauvinkoVowel.O:
            raise LauvinkoSyllable.InvalidSyllable(f"{self.vowel.ipa}{self.coda.ipa}")

        if self.coda is LauvinkoConsonant.Y and self.vowel.frontness is VowelFrontness.FRONT:
            raise LauvinkoSyllable.InvalidSyllable(f"{self.vowel.ipa}{self.coda.ipa}")

        if self.coda is LauvinkoConsonant.A and self.vowel is LauvinkoVowel.A:
            raise LauvinkoSyllable.InvalidSyllable(f"{self.vowel.ipa}{self.coda.ipa}")


def broad_coda_ipa(coda: Optional[LauvinkoConsonant]):
    """A number of phonemic distinctions are unilaterally collapsed in the coda of Lauvinko syllables.
    The original/historic consonant value is still stored with LauvinkoSyllable because it may occasionally
    be used when discussing historical change but usually a "narrower" phonemic transcription is used that
    reflects those collapses. It prefers neutral/existing phoneme symbols like /l/ and /ʋ/ rather than
    those that would more narrowly describe the typical phonetic value like /ɽ/ or /w/
    """
    if coda is None:
        return ''
    elif coda.moa is MannerOfArticulation.NASAL:
        return 'n'
    # elif coda is LauvinkoConsonant.C:
    #     return 's'
    elif coda.moa is MannerOfArticulation.PLAIN_STOP:
        return 'h'
    else:
        return coda.ipa


CODA_PHONETIC = {
    None: '',
    LauvinkoConsonant.C: 's',
    LauvinkoConsonant.L: 'ɽ',
    LauvinkoConsonant.V: 'w',
}


def narrow_coda_ipa(coda: Optional[LauvinkoConsonant]):
    if coda in CODA_PHONETIC:
        return CODA_PHONETIC[coda]
    elif coda.moa is MannerOfArticulation.NASAL:
        return 'ŋ'
    elif coda.moa is MannerOfArticulation.PLAIN_STOP:
        return 'ʔ'
    else:  # S, Y, A
        return coda.ipa


def palatal(coda: LauvinkoConsonant):
    if coda is LauvinkoConsonant.S:
        return 'ɕ'
    elif coda is LauvinkoConsonant.L:
        return 'ʎ'
    elif coda is LauvinkoConsonant.C or coda.moa is MannerOfArticulation.PLAIN_STOP:
        return 't͡ɕ'
    elif coda.moa is MannerOfArticulation.NASAL:
        return 'ɲ'

    return None


RETROFLEXES = {
    MannerOfArticulation.NASAL: 'ɳ',
    MannerOfArticulation.PLAIN_STOP: 'ʈ',
    MannerOfArticulation.AFFRICATE: 'ʈ͡ʂ',
    MannerOfArticulation.FRICATIVE: 'ʂ',
    MannerOfArticulation.APPROXIMANT: 'ɭ',
}


def consonant_sandhi(coda: LauvinkoConsonant, onset: LauvinkoConsonant):
    if onset is LauvinkoConsonant.Y:
        p = palatal(coda)
        if p is not None:
            return p[0] + p

    if coda is LauvinkoConsonant.L:
        if onset.poa is PlaceOfArticulation.ALVEOLAR:
            r = RETROFLEXES[onset.moa]
            return r[0] + r

    if coda.moa is MannerOfArticulation.NASAL:
        coda = LauvinkoConsonant.find_by(
            poa=onset.poa,
            moa=MannerOfArticulation.NASAL,
        )

        return coda.ipa + onset.ipa

    if coda.moa is MannerOfArticulation.PLAIN_STOP:
        if onset.moa in {MannerOfArticulation.NASAL, MannerOfArticulation.APPROXIMANT}:
            return 'ɦ' + onset.ipa
        else:
            return onset.ipa[0] + onset.ipa

    return narrow_coda_ipa(coda) + onset.ipa


CLOSED_VOWELS = {
    LauvinkoVowel.A: 'ɐ',
    LauvinkoVowel.E: 'ɛ',
    LauvinkoVowel.I: 'ɪ',
    LauvinkoVowel.O: 'ʊ',
}


UNACCENTED_OPEN_VOWELS = {
    **CLOSED_VOWELS,
    # TODO: If I stay happy with commenting the line below, should get rid of this dict altogether
    # LauvinkoVowel.E: CLOSED_VOWELS[LauvinkoVowel.I],
}


ACCENTED_OPEN_VOWELS = {
    LauvinkoVowel.A: 'ɑ',
    LauvinkoVowel.E: 'e',
    LauvinkoVowel.I: 'i',
    LauvinkoVowel.O: 'o',
}


def accent_ipa(falling_accent: bool):
    return "\u0302" if falling_accent else "\u0301"


@dataclass
class LauvinkoSurfaceForm(SurfaceForm):
    syllables: List[LauvinkoSyllable]
    accent_position: int
    falling_accent: bool

    class InvalidLauvinkoSurfaceForm(ValueError):
        pass

    def __post_init__(self):
        if self.accent_position is not None and self.accent_position >= len(self.syllables):
            raise self.InvalidLauvinkoSurfaceForm("Accent in invalid position")

        for syllable in self.syllables:
            syllable.__post_init__()

        for syllable in self.syllables[1:]:
            if syllable.onset is LauvinkoConsonant.H:
                raise self.InvalidLauvinkoSurfaceForm("Lauvinko surface form cannot have h medially")
            elif syllable.onset is None:
                raise self.InvalidLauvinkoSurfaceForm("Non-initial syllables in Lauvinko must have an onset")

    def broad_transcription(self):
        syllables_ipa = []

        for i, syllable in enumerate(self.syllables):
            if i == self.accent_position:
                accent = accent_ipa(self.falling_accent)
            else:
                accent = ''

            if syllable.coda is not None:
                coda = syllable.coda.ipa
            else:
                coda = ''

            syllables_ipa.append(
                f"{getattr(syllable.onset, 'ipa', '')}{syllable.vowel.ipa}{accent}{coda}"
            )

        return ".".join(syllables_ipa)

    def narrow_transcription(self) -> str:
        out = getattr(self.syllables[0].onset, 'ipa', '')

        for i in range(len(self.syllables)):
            vowel, coda = self.syllables[i].vowel, self.syllables[i].coda

            has_coda, accented = (coda is not None), (i == self.accent_position)

            if has_coda:
                out += CLOSED_VOWELS[vowel]
            elif accented:
                out += ACCENTED_OPEN_VOWELS[vowel]
            else:
                out += UNACCENTED_OPEN_VOWELS[vowel]

            if accented:
                out += accent_ipa(self.falling_accent)

                if not has_coda:
                    out += 'ː'

            if i == len(self.syllables) - 1:
                out += narrow_coda_ipa(coda)
            elif coda is None:
                out += self.syllables[i + 1].onset.ipa
            else:
                out += consonant_sandhi(coda, self.syllables[i + 1].onset)

        return out


