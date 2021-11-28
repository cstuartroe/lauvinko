from lauvinko.lang.shared.phonology import MannerOfArticulation, PlaceOfArticulation
from lauvinko.lang.lauvinko.phonology import LauvinkoConsonant, LauvinkoSurfaceForm


def coda_romanization(coda: LauvinkoConsonant, next_onset: LauvinkoConsonant) -> str:
    if coda is None:
        return ''

    elif coda.moa is MannerOfArticulation.NASAL:
        if next_onset is None:
            return 'ng'
        elif next_onset.poa is PlaceOfArticulation.LABIAL:
            return 'm'
        else:
            return 'n'

    elif coda.moa is MannerOfArticulation.PLAIN_STOP:
        if next_onset and (next_onset.moa is MannerOfArticulation.PLAIN_STOP or next_onset in {LauvinkoConsonant.C, LauvinkoConsonant.S}):
            return next_onset.name.lower()
        elif next_onset is LauvinkoConsonant.Y:
            return 'c'
        else:
            return 'h'

    elif coda is LauvinkoConsonant.C:
        if next_onset is LauvinkoConsonant.Y:
            return 'c'
        else:
            return 's'

    elif coda is LauvinkoConsonant.L:
        if next_onset in {LauvinkoConsonant.L, LauvinkoConsonant.Y}:
            return 'l'
        else:
            return 'r'

    elif coda is LauvinkoConsonant.V:
        return 'u'

    else:
        return coda.name.lower()


def romanize(sf: LauvinkoSurfaceForm):
    out = ""

    for i, syllable in enumerate(sf.syllables):
        if syllable.onset:
            out += syllable.onset.name.lower()

        out += syllable.vowel.name.lower()
        if i == sf.accent_position:
            out += "\u0300" if sf.falling_accent else "\u0301"

        next_onset = sf.syllables[i+1].onset if i + 1 < len(sf.syllables) else None

        out += coda_romanization(syllable.coda, next_onset)

    return out
