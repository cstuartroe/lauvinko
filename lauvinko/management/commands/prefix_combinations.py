from django.core.management.base import BaseCommand
from lauvinko.lang.shared.morphology import MorphosyntacticType
from lauvinko.lang.shared.semantics import Language, PTA2ABBREV
from lauvinko.lang.lauvinko.diachronic.base import OriginLanguage
from lauvinko.lang.gloss.gloss import Gloss
from lauvinko.lang.dictionary.dictionary import Dictionary, MODAL_PREFIXES, TERTIARY_ASPECT_PREFIXES, TOPIC_AGREEMENT_PREFIXES, TOPIC_CASE_PREFIXES

ROOTS = []

for entry in Dictionary.load().entries.values():
    if entry.mstype is not MorphosyntacticType.INDEPENDENT:
        continue
    origin_lang, _ = entry.origin.language_and_word()
    if origin_lang is not OriginLanguage.KASANIC:
        continue

    lv_lemma = entry.languages[Language.LAUVINKO]
    for pta in lv_lemma.category.primary_aspects:
        abbrev = PTA2ABBREV[pta]
        for augment in ["au", "na"]:
            ROOTS.append(f"{lv_lemma.ident}.${abbrev}$.${augment}$")

ROOTS.sort()

# ROOTS = [
#     "black.$inc$.$na$",
#     "cut.$np$.$na$",
#     "wise.$inc$.$na$",
#     "deep.$gn$.$na$",
#     "cross.$np$.$na$",
#     "help.$imnp$.$na$",
#     "build.$fqnp$.$na$",
#     "build.$fqpt$.$na$",
#     "cross.$fqnp$.$na$",
#     "cross.$fqpt$.$na$",
#     "cut.$fqpt$.$na$",
#     "narrow.$gn$.$na$",
#     "depict.$fqpt$.$na$",
#     "atineni.$gn$.$na$",
# ]

PREFIXES = []

for p in MODAL_PREFIXES.keys():
    PREFIXES.append(p)

for p in TERTIARY_ASPECT_PREFIXES.keys():
    PREFIXES.append(f"${p}$")

for p in TOPIC_AGREEMENT_PREFIXES.keys():
    PREFIXES.append(f"${p}$-$tage$")

for p in TOPIC_CASE_PREFIXES.keys():
    PREFIXES.append(f"$st$-${p}$")

# PREFIXES = ["after:$st$", "like"]


OUTFILE = "lauvinko/lang/prefixes.txt"


class Command(BaseCommand):
    help = 'Exports the combination of every prefix with every root'

    def handle(self, *args, **options):
    #     for root in ROOTS:
    #         print(root)
    #         forms = [
    #             Gloss.parse(root, language=Language.LAUVINKO).romanization()[0]
    #         ]
    #         for prefix in PREFIXES:
    #             if prefix == "$st$-$tage$":
    #                 continue
    #             form = Gloss.parse(f"{prefix}-{root}", language=Language.LAUVINKO).romanization()[0]
    #             forms.append(form)
    #
    #         for i in range(6):
    #             print('\t'.join(forms[i*6:(i+1)*6]))
    #
    #
    # def skip(self):
        outfile_content = ""

        for prefix in PREFIXES:
            outfile_content += f"{prefix}\n\n"

            for root in ROOTS:
                rr = Gloss.parse(root, language=Language.LAUVINKO).romanization()[0]
                pr = Gloss.parse(f"{prefix}-{root}", language=Language.LAUVINKO).romanization()[0]
                outfile_content += f"{root}: {rr} -> {pr}\n"

            outfile_content += "\n"

        with open(OUTFILE, "w") as fh:
            fh.write(outfile_content)
