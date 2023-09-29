import json
import os
from dataclasses import dataclass
import mistletoe
from mistletoe.ast_renderer import ASTRenderer
from django.core.management.base import BaseCommand
from .validate_links import PAGES_DIR
from lauvinko.lang.shared.semantics import Language
from lauvinko.lang.gloss.gloss import Gloss, normalize_word


SENTENCES_FILE = "lauvinko/lang/sentences.txt"


def get_outline(block: dict):
    lines = block["children"][0]["content"].split("\n")
    outline = ""

    i = 0
    while lines[i] != "":
        outline += lines[i].strip() + " "
        i += 1

    translation = ' '.join(line.strip() for line in lines[i:]).strip()

    return outline, translation


@dataclass
class Sentence:
    words: list[str]
    translation: str


class Command(BaseCommand):
    help = 'Compiles all sentences and word counts from block glosses'

    def handle(self, *args, **options):
        word_counts: dict[str, int] = {}
        sentences: list[Sentence] = []

        outfile_content = ""

        for mdfile in sorted(list(os.listdir(PAGES_DIR))):
            with open(os.path.join(PAGES_DIR, mdfile), 'r') as fh:
                content = json.loads(mistletoe.markdown(fh.read(), ASTRenderer))

            for block in content["children"]:
                if block["type"] == "CodeFence":
                    lang = block["language"]
                    if lang == "" or lang.startswith("lv"):
                        outline, translation = get_outline(block)
                        gloss = Gloss.parse(outline, language=Language.LAUVINKO)
                        r = gloss.romanization()
                        f = gloss.falavay()
                        for word in r:
                            n = normalize_word(word)
                            word_counts[n] = word_counts.get(n, 0) + 1
                        sentences.append(Sentence(r, translation))

                        outfile_content += ' '.join(f) + "\n"
                        outfile_content += ' '.join(r) + "\n"

        print()
        for word, count in sorted(list(word_counts.items()), key=lambda x: x[1])[-100:]:
            print(word, count)

        print()
        print(f"{len(sentences)} sentences.")
        print(f"{sum(word_counts.values())} total words.")
        print(f"{len(word_counts)} distinct words.")
        print(f"{len(list(w for w, c in word_counts.items() if c == 1))} hapax legomena.")

        with open(SENTENCES_FILE, "w") as fh:
            fh.write(outfile_content)
