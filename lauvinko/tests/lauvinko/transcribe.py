import unittest

from lauvinko.lang.lauvinko.morphology import LauvinkoMorpheme
from lauvinko.lang.lauvinko.transcribe import transcribe


lm = LauvinkoMorpheme.from_informal_transcription


TESTS: list[tuple[LauvinkoMorpheme, str]] = [
    (lm("pa/le"), 'pále'),
    (lm("se\\anor"), 'sèanor'),
    (lm("nca/ke"), 'ancáke'),
    (lm("nca/y"), 'ancáy'),
    (lm('tte/kin'), 'téking'),
    (lm("tte/n"), 'téng'),
    (lm("vo/kka"), 'vókka'),
    (lm('vo/k'), 'vóh'),
    (lm("la/ppam"), 'láppang'),
    (lm('la/pam'), 'lápang'),
    (lm("a/nta"), 'ánta'),
    (lm("a/n"), 'áng'),
    (lm("a/nti"), 'ánti'),
    (lm("a/ni"), 'áni'),
    (lm("avo/nta"), 'avónta'),
    (lm("avo/n"), 'avóng'),
    (lm("pe/c"), 'pés'),
    (lm("pe/s"), 'pés'),
    (lm("pa/y"), 'páy'),
    (lm("o/kka"), 'ókka'),
    (lm("o/k"), 'óh'),
    (lm("o/p"), 'óh'),
    (lm("o/"), 'ó'),
    (lm("kwo/lenta"), 'pólenta'),
    (lm("kwo\\linta"), 'pòlinta'),
    (lm("co/ntes"), 'cóntes'),
    (lm("co/nis"), 'cónis'),
    (lm("nyayi\\s"), 'nayìs'),
    (lm("a/tli"), 'áhli'),
    (lm("a/lli"), 'álli'),
    (lm("yavo/ppami"), 'yavóppami'),
    (lm("yavo/pmi"), 'yavóhmi'),
    (lm("o/kay"), 'ókay'),
    (lm("o/ayi"), 'óayi'),
    (lm("nkwe/kke"), 'mékke'),
    (lm("nkwe/ke"), 'méke'),
    (lm("e/kkangi"), 'ékkangi'),
    (lm("e/kngi"), 'éhngi'),
    (lm("ka\\ming"), 'kàming'),
    (lm("i\\lay"), 'ìlay'),
    (lm("ngo\\yang"), 'ngòyang'),
    (lm("kwayi/nta"), 'payínta'),
    (lm("kwayi/n"), 'payíng'),
    (lm("he\\nacvi"), 'hènasvi'),
    (lm("ko/nkapir"), 'kónkapir'),
    (lm("ko/ngpir"), 'kómpir'),
    (lm("ma/tcop"), 'máccoh'),
    (lm("ma/cap"), 'mácah'),
    (lm("me\\k"), 'mèh'),
    (lm("ko/nca"), 'kónca'),
    (lm("ko/nsa"), 'kónsa'),
    (lm("o/ksan"), 'óssang'),
    (lm("o/asan"), 'óasang'),
    (lm("so\\y"), 'sòy'),
    (lm("so/kar"), 'sókar'),
    (lm("so/ala"), 'sóala'),
    (lm("to/pay"), 'tópay'),
    (lm("to/ve"), 'tóve'),
    (lm("atca"), 'acca'),
    (lm('acca'), 'asca'),
    (lm('acsa'), 'assa'),
    (lm('alya'), 'alya'),
    (lm('alla'), 'alla'),
    (lm('alva'), 'arva'),
    (lm('alnga'), 'arnga'),
    (lm('atya'), 'acya'),
    (lm('acya'), 'acya'),
    (lm('asya'), 'asya'),
]


class LauvinkoTranscriptionTests(unittest.TestCase):
    def test_transcription(self):
        for morpheme, transcription in TESTS:
            self.assertEqual(
                transcribe(morpheme.surface_form),
                transcription,
            )
