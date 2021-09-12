from lauvinko.lang.lauvinko.phonology import LauvinkoSurfaceForm
from lauvinko.lang.proto_kasanic.phonology import ProtoKasanicOnset, ProtoKasanicMutation
from lauvinko.lang.shared.semantics import PrimaryTenseAspect


class LauvinkoLemmaOrigin:
    def generate_form(self, primary_ta: PrimaryTenseAspect, augment: bool) \
            -> tuple[LauvinkoSurfaceForm, ProtoKasanicOnset, ProtoKasanicMutation]:
        raise NotImplementedError

