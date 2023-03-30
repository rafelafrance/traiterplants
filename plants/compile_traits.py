#!/usr/bin/env python3
import argparse
import csv
import logging
import textwrap
from pathlib import Path

from pylib.traits.habit import habit_compilers as habit
from pylib.traits.link_location import link_location_compilers as link_location
from pylib.traits.link_part import link_part_compilers as link_part
from pylib.traits.link_sex import link_sex_compilers as link_sex
from pylib.traits.part import part_compilers as part
from pylib.traits.part_location import part_location_compilers as part_location
from pylib.traits.shape import shape_compilers as shape
from pylib.traits.surface import surface_compilers as surface
from spacy.lang.en import English
from traiter.pylib import log


class Matchers:
    def __init__(self, name, matchers, dir_=None):
        self.name = name
        self.matchers = matchers if isinstance(matchers, list) else [matchers]
        self.dir = dir_ if dir_ else name


ALL_MATCHERS = [
    Matchers("habit", habit.COMPILERS),
    Matchers("link_location", link_location.LINK_LOCATION),
    Matchers("link_part", link_part.LINK_PART, "link_part"),
    Matchers("link_part_once", link_part.LINK_PART_ONCE, "link_part"),
    Matchers("link_sex", link_sex.LINK_SEX),
    Matchers("link_subpart", link_part.LINK_SUBPART, "link_part"),
    Matchers("part", part.COMPILERS),
    Matchers("part_location", part_location.COMPILERS),
    Matchers("shape", shape.COMPILERS),
    Matchers("surface", surface.COMPILERS),
]


def main():
    log.started()

    args = parse_args()

    compile_terms(args)
    compile_patterns(args)

    log.finished()


def compile_patterns(args):
    for matchers in ALL_MATCHERS:
        if args.trait and matchers.dir != args.trait:
            continue

        logging.info(f"Compiling patterns for {matchers.name}")

        patterns = []
        for matcher in matchers.matchers:
            for pattern in matcher.patterns:
                line = {
                    "label": matcher.label,
                    "pattern": pattern,
                }
                if matcher.id:
                    line["id"] = matcher.id
                patterns.append(line)

        nlp = English()
        ruler = nlp.add_pipe("entity_ruler", config={"validate": True})
        ruler.add_patterns(patterns)

        dir_ = args.traits_dir / matchers.dir

        path = dir_ / f"{matchers.name}_patterns.jsonl"
        ruler.to_disk(path)


def compile_terms(args):
    for path in sorted(args.traits_dir.glob("**/*.csv")):
        if args.trait and path.stem != args.trait:
            continue

        logging.info(f"Compiling terms for {path.stem}")

        with open(path) as term_file:
            reader = csv.DictReader(term_file)
            terms = list(reader)

        lower = []
        text = []
        for term in terms:
            pattern = {
                "label": term["label"],
                "pattern": term["pattern"],
            }
            if term.get("attr", "lower") == "lower":
                lower.append(pattern)
            else:
                text.append(pattern)

        if lower:
            nlp = English()
            ruler = nlp.add_pipe("entity_ruler")
            ruler.add_patterns(lower)
            ruler.to_disk(path.parent / f"{path.stem}_terms_lower.jsonl")

        if text:
            nlp = English()
            ruler = nlp.add_pipe("entity_ruler")
            ruler.add_patterns(text)
            ruler.to_disk(path.parent / f"{path.stem}_terms_text.jsonl")


def parse_args() -> argparse.Namespace:
    description = """Convert pattern objects into entity ruler patterns."""

    arg_parser = argparse.ArgumentParser(
        description=textwrap.dedent(description), fromfile_prefix_chars="@"
    )

    arg_parser.add_argument(
        "--traits-dir",
        type=Path,
        metavar="PATH",
        required=True,
        help="""Save the term JSONL files to this directory.""",
    )

    arg_parser.add_argument("--trait", help="Only compile patterns for this trait.")

    return arg_parser.parse_args()


if __name__ == "__main__":
    main()
