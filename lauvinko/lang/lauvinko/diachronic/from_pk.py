from dataclasses import dataclass
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicLemma
from lauvinko.lang.shared.semantics import PrimaryTenseAspect
from lauvinko.lang.shared.phonology import MannerOfArticulation, PlaceOfArticulation
from lauvinko.lang.proto_kasanic.phonology import ProtoKasanicOnset, PKSurfaceForm
from lauvinko.lang.proto_kasanic.morphology import MUTATION_NOTATION
from lauvinko.lang.lauvinko.phonology import LauvinkoConsonant, LauvinkoVowel, LauvinkoSyllable, LauvinkoSurfaceForm
from .base import LauvinkoLemmaOrigin


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


def pk_to_lv(pk_sf: PKSurfaceForm, augment: bool) -> LauvinkoSurfaceForm:
    pass


@dataclass
class ProtoKasanicOrigin(LauvinkoLemmaOrigin):
    derived_from: ProtoKasanicLemma
