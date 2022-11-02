import unittest
from typing import Iterable

from lauvinko.lang.lauvinko.diachronic.base import MorphemeContext
from lauvinko.lang.shared.morphology import MorphosyntacticType
from lauvinko.lang.shared.phonology import VowelFrontness
from lauvinko.lang.shared.semantics import KasanicStemCategory, PrimaryTenseAspect
from lauvinko.lang.proto_kasanic.phonology import ProtoKasanicOnset, ProtoKasanicVowel, ProtoKasanicSyllable, PKSurfaceForm
from lauvinko.lang.proto_kasanic.morphology import ProtoKasanicMorpheme, pkm, ProtoKasanicLemma
from lauvinko.lang.proto_kasanic.romanize import romanize as pk_romanize
from lauvinko.lang.lauvinko.morphology import LauvinkoMorpheme, LauvinkoLemma
from lauvinko.lang.lauvinko.romanize import romanize as lv_romanize


lm = LauvinkoMorpheme.from_informal_transcription


PK_TESTS: list[tuple[ProtoKasanicMorpheme, LauvinkoMorpheme, LauvinkoMorpheme]] = [
    (pkm("paaraye+N"), lm("pa/le+N"), lm("pa\\le+N")),
    (pkm("sehaanoro"), lm("se/anor"), lm("se\\anor")),
    (pkm("ncaakaye"), lm("nca/ke"), lm("nca/y")),
    (pkm("ttakinyo"), lm('tte/kin'), lm("tte/n")),
    (pkm("wokko"), lm("vo/kka"), lm('vo/k')),
    (pkm("raappungwa"), lm("la/ppam"), lm('la/pam')),
    (pkm("aanta"), lm("a/nta"), lm("a/n")),
    (pkm("aanti"), lm("a/nti"), lm("a/ni")),
    (pkm("aunta"), lm("avo/nta"), lm("avo/n")),
    (pkm("peca"), lm("pe/c"), lm("pe/s")),
    (pkm("pai"), lm("pa/y"), lm("pa\\y")),
    (pkm("okka"), lm("o/kka"), lm("o/k")),
    (pkm("opaa"), lm("o/p"), lm("o/")),
    (pkm("kworentaa"), lm("kwo/lenta"), lm("kwo\\linta")),
    (pkm("contesaa"), lm("co/ntes"), lm("co/nis")),
    (pkm("nyaisaa"), lm("nyayi/s"), lm("nyayi\\s")),
    (pkm("aatari"), lm("a/tli"), lm("a/lli")),
    (pkm("yauppami"), lm("yavo/ppami"), lm("yavo/pmi")),
    (pkm("okaaye"), lm("o/kay"), lm("o/ayi")),
    (pkm("nkwakkaye"), lm("nkwe/kke"), lm("nkwe/ke")),
    (pkm("ekkungi"), lm("e/kkangi"), lm("e/kngi")),
    (pkm("kaamengaa"), lm("ka/meng"), lm("ka\\ming")),
    (pkm("irohi"), lm("i/loy"), lm("i\\lay")),
    (pkm("ngoyangu"), lm("ngo/yang"), lm("ngo\\yang")),
    (pkm("kwaintaa"), lm("kwayi/nta"), lm("kwayi/n")),
    (pkm("henaacawi"), lm("he/nacvi"), lm("he\\nacvi")),
    (pkm("konkaakwiru"), lm("ko/nkapir"), lm("ko/ngpir")),
    (pkm("maaccopo"), lm("ma/tcop"), lm("ma/cap")),
    (pkm("mahika"), lm("me/k"), lm("me\\k")),
    (pkm("konco"), lm("ko/nca"), lm("ko/nsa")),
    (pkm("ukasana"), lm("o/ksan"), lm("o/asan")),
    (pkm("sohai"), lm("so/y"), lm("so\\y")),
    (pkm("sukara"), lm("so/kar"), lm("so/ala")),
    (pkm("tupai"), lm("to/pay"), lm("to/ve")),
    (pkm("ttu'inkwa/kitaa"), lm("ttavinpe/kit"), lm("ttavinpe/t")),

    (pkm("tehinti"), lm("te/nti"), lm("te\\nti")),
    (pkm("tohinti"), lm("to/vinti"), lm("to\\vinti")),
    (pkm("tahinti"), lm("te/nti"), lm("te\\nti")),
    (pkm("taahinti"), lm("ta/yinti"), lm("ta\\yinti")),

    (pkm("taatehinti"), lm("ta/tenti"), lm("ta/linti")),
    (pkm("taatohinti"), lm("ta/tovinti"), lm("ta/rvinti")),
    (pkm("taatahinti"), lm("ta/tenti"), lm("ta/lenti")),
    (pkm("taataahinti"), lm("ta/tayinti"), lm("ta/lenti")),

    (pkm("tehini"), lm("te/ni"), lm("te\\ni")),
    (pkm("tohini"), lm("to/yni"), lm("to\\yni")),
    (pkm("tahini"), lm("te/ni"), lm("te\\ni")),
    (pkm("taahini"), lm("ta/yni"), lm("ta\\yni")),

    (pkm("taatehini"), lm("ta/teni"), lm("ta/lini")),
    (pkm("taatohini"), lm("ta/toyni"), lm("ta/layni")),
    (pkm("taatahini"), lm("ta/teni"), lm("ta/leni")),
    (pkm("taataahini"), lm("ta/tayni"), lm("ta/leni")),

    (pkm("aahiho"), lm("a/y"), lm("a\\y")),
    (pkm("ahiho"), lm("e/"), lm("e\\")),
    (pkm("aahihoni"), lm("a/yoni"), lm("a\\yoni")),
    (pkm("aihe"), lm("a/y"), lm("a\\y")),
    (pkm("aiho"), lm("a/y"), lm("a\\y")),
    (pkm("ai'ohe"), lm("a/yoy"), lm("a\\yay")),
    (pkm("ai'ohe'aa"), lm("a/yoy"), lm("a\\yay")),
    (pkm("o'aa'u'i"), lm("o/vi"), lm("o\\vi")),
    (pkm("i'aa'a'e'ota"), lm("i/yot"), lm("i\\yot")),
]


TA_TEST_ORDER = [
    PrimaryTenseAspect.IMPERFECTIVE_NONPAST,
    PrimaryTenseAspect.IMPERFECTIVE_PAST,
    PrimaryTenseAspect.PERFECTIVE,
    PrimaryTenseAspect.INCEPTIVE,
    PrimaryTenseAspect.FREQUENTATIVE_NONPAST,
    PrimaryTenseAspect.FREQUENTATIVE_PAST,
]


FULL_TENSE_ASPECT_TESTS = [
    (pkm("tt@ko"), lm("ta/u"), lm("to/"), lm("te/u"), lm("itta/u"), lm("tette/u"), lm("totto/")),
    (pkm("kw~ri"), lm("pe\\li"), lm("ko\\li"), lm("pi\\li"), lm("inpe\\li"), lm("pipi\\li"), lm("kako\\li")),
    (pkm("nc@"), lm("anca\\"), lm("anco\\"), lm("ance\\"), lm("inca\\"), lm("ancence\\"), lm("anconco\\")),
    (pkm("nt~toka"), lm("ne/lak"), lm("no/lak"), lm("ni/lak"), lm("inte/lak"), lm("ninti/lak"), lm("nanto/lak")),
]


def all_pk_sylls(max_syllables=2) -> Iterable[list[ProtoKasanicSyllable]]:
    if max_syllables <= 0:
        yield from []

    else:
        for onset in (None, *ProtoKasanicOnset):
            for vowel in ProtoKasanicVowel:
                if vowel.frontness is VowelFrontness.UNDERSPECIFIED:
                    continue

                try:
                    syll = ProtoKasanicSyllable(onset=onset, vowel=vowel)
                except ProtoKasanicSyllable.InvalidSyllable:
                    continue

                yield [syll]

                for sylls in all_pk_sylls(max_syllables-1):
                    yield [syll, *sylls]


class LauvinkoDiachronicTests(unittest.TestCase):
    def test_evolution_from_pk(self):
        for pk_morpheme, lv_morpheme_au, lv_morpheme_na in PK_TESTS:
            pk_lemma = ProtoKasanicLemma(
                ident="",
                definition="",
                category=KasanicStemCategory.UNINFLECTED,
                mstype=MorphosyntacticType.INDEPENDENT,
                forms={},
                generic_morph=pk_morpheme,
            )
            lv_lemma = LauvinkoLemma.from_pk(pk_lemma)

            for augment, lv_morpheme in [
                (MorphemeContext.AUGMENTED, lv_morpheme_au),
                (MorphemeContext.NONAUGMENTED, lv_morpheme_na),
            ]:
                evolved_form = lv_lemma.form(PrimaryTenseAspect.GENERAL, context=augment)

                self.assertEqual(
                    evolved_form.surface_form.historical_transcription(),
                    lv_morpheme.surface_form.historical_transcription(),
                )
                self.assertIs(
                    evolved_form.virtual_original_form.end_mutation,
                    lv_morpheme.virtual_original_form.end_mutation,
                )
                self.assertIs(
                    evolved_form.original_initial_consonant(),
                    lv_morpheme.original_initial_consonant(),
                )

    def test_tense_aspect(self):
        for pk_morpheme, *forms in FULL_TENSE_ASPECT_TESTS:
            pk_lemma = ProtoKasanicLemma(
                ident="",
                definition="",
                category=KasanicStemCategory.FIENTIVE,
                mstype=MorphosyntacticType.INDEPENDENT,
                forms={},
                generic_morph=pk_morpheme,
            )
            lv_lemma = LauvinkoLemma.from_pk(pk_lemma)

            for primary_ta, lv_morpheme in zip(TA_TEST_ORDER, forms):
                evolved_form = lv_lemma.form(primary_ta, MorphemeContext.NONAUGMENTED)

                self.assertEqual(
                    evolved_form.surface_form.historical_transcription(),
                    lv_morpheme.surface_form.historical_transcription(),
                )

    def test_information_loss(self):
        pk_sfs = set()
        lv_au_sfs = set()
        lv_na_sfs = set()

        for i, sylls in enumerate(all_pk_sylls(2)):
            pk_lemma = ProtoKasanicLemma(
                ident="",
                definition="",
                category=KasanicStemCategory.UNINFLECTED,
                mstype=MorphosyntacticType.INDEPENDENT,
                forms={},
                generic_morph=ProtoKasanicMorpheme(
                    lemma=None,
                    surface_form=PKSurfaceForm(
                        syllables=sylls,
                        stress_position=0,
                    ),
                    end_mutation=None,
                ),
            )

            pkr = pk_romanize(pk_lemma.form(PrimaryTenseAspect.GENERAL).surface_form())
            pk_sfs.add(pkr)

            lv_lemma = LauvinkoLemma.from_pk(pk_lemma)

            aur = lv_romanize(lv_lemma.form(PrimaryTenseAspect.GENERAL, context=MorphemeContext.AUGMENTED).surface_form)
            lv_au_sfs.add(aur)

            nar = lv_romanize(lv_lemma.form(PrimaryTenseAspect.GENERAL,
                                            context=MorphemeContext.NONAUGMENTED).surface_form)
            lv_na_sfs.add(nar)

        print(f"There are {len(pk_sfs)} Proto-Kasanic surface forms")
        print(f"There are {len(lv_au_sfs)} Lauvinko augment surface forms")
        print(f"There are {len(lv_na_sfs)} Lauvinko nonaugment surface forms")
        print(f"There are {len(lv_au_sfs | lv_na_sfs)} total Lauvinko surface forms")
        print(f"There are only {len(lv_au_sfs & lv_na_sfs)} surface forms which can be either augment or non-augment")
