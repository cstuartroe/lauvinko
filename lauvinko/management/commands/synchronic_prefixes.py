from django.core.management.base import BaseCommand
from lauvinko.lang.shared.semantics import Language
from lauvinko.lang.gloss.gloss import Gloss
from .prefix_combinations import ROOTS, PREFIXES


def prefix_string_substitution(original, prefixed) -> tuple[str, str]:
    i = -1
    while i >= -len(original) and i >= -len(prefixed) and original[i] == prefixed[i]:
        i -= 1

    return original[:i+1], prefixed[:i+1]


def determine_prefix_change(root: str, prefix: str) -> tuple[str, str]:
    root_gloss = Gloss.parse(root, language=Language.LAUVINKO)
    prefix_gloss = Gloss.parse(f"{prefix}-{root}", language=Language.LAUVINKO)

    rr = root_gloss.broad_transcription()[0]
    pr = prefix_gloss.broad_transcription()[0]

    return prefix_string_substitution(rr.replace(".", ""), pr.replace(".", ""))


def sort_by_entries(d: dict) -> dict:
    l = list(d.items())
    l.sort(key=lambda p: len(p[1]))
    return dict(l)


def get_representative_roots(printing: bool = True) -> list[str]:
    """This function groups the roots into root groups.
       Root groups are defined as all the roots for which all
       prefixes lead to the same string replacements.
       Once root groups are determined, this function takes one
       root from each and returns the list.
       At time of writing, this function identifies 34 root groups.
    """

    root_groups = {}

    for root in ROOTS:
        prefix_changes_all = []
        for prefix in PREFIXES:
            prefix_change = '/'.join(determine_prefix_change(root, prefix))
            prefix_changes_all.append(prefix_change)

        prefix_changes_str = '\n'.join(prefix_changes_all)
        if prefix_changes_str not in root_groups:
            root_groups[prefix_changes_str] = []
        root_groups[prefix_changes_str].append(root)

    root_groups = sort_by_entries(root_groups)

    if printing:
        for prefix_changes, roots in root_groups.items():
            print(prefix_changes)
            for root in roots:
                gloss = Gloss.parse(root, language=Language.LAUVINKO)
                print(root, gloss.romanization()[0])
            print(f"{len(roots)}/{len(ROOTS)} ({len(roots)*100/len(ROOTS):.1f}%)")

    return [
        root_group[0]
        for root_group in root_groups.values()
    ]


class Command(BaseCommand):
    help = 'Compiles all sentences and word counts from block glosses'

    def handle(self, *args, **options):
        roots = get_representative_roots(printing=False)
        for prefix in PREFIXES:
            prefix_changes = {}

            for root in roots:
                prefix_change = '/'.join(determine_prefix_change(root, prefix))
                if prefix_change not in prefix_changes:
                    prefix_changes[prefix_change] = []
                prefix_changes[prefix_change].append(root)

            prefix_changes = sort_by_entries(prefix_changes)

            print(prefix)
            print()
            for change, root_group in prefix_changes.items():
                print(change)
                for root in root_group:
                    rr = Gloss.parse(root, language=Language.LAUVINKO).romanization()[0]
                    pr = Gloss.parse(f"{prefix}-{root}", language=Language.LAUVINKO).romanization()[0]
                    print(f"{root}: {rr} -> {pr}")
                print()
            print()

        print(len(roots), "root groups")
