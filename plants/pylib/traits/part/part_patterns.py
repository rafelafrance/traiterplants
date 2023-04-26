from traiter.pylib import const as t_const
from traiter.pylib.pipes.reject_match import REJECT_MATCH
from traiter.pylib.traits.pattern_compiler import Compiler

from . import part_action as act


def part_patterns():
    decoder = {
        "-": {"TEXT": {"IN": t_const.DASH}, "OP": "+"},
        "and": {"ENT_TYPE": "part_and"},
        "bad_part": {"ENT_TYPE": "bad_part"},
        "leader": {"ENT_TYPE": "part_leader"},
        "missing": {"ENT_TYPE": "missing"},
        "part": {"ENT_TYPE": {"IN": act.PART_LABELS}},
        "subpart": {"ENT_TYPE": "subpart"},
    }

    return [
        Compiler(
            label="part",
            id="part",
            on_match=act.PART_MATCH,
            keep=act.ALL_LABELS,
            decoder=decoder,
            patterns=[
                "leader? part+",
                "leader? part+ - part+",
            ],
        ),
        Compiler(
            label="missing_part",
            on_match=act.PART_MATCH,
            keep=act.ALL_LABELS,
            decoder=decoder,
            patterns=[
                "missing part+",
                "missing part+ and part+",
                "missing part+ -   part+",
            ],
        ),
        Compiler(
            label="multiple_parts",
            on_match=act.PART_MATCH,
            keep=act.ALL_LABELS,
            decoder=decoder,
            patterns=[
                "leader? part+ and part+",
                "missing part+ and part+",
            ],
        ),
        Compiler(
            label="subpart",
            on_match=act.PART_MATCH,
            keep=act.ALL_LABELS,
            decoder=decoder,
            patterns=[
                "leader? subpart+",
                "leader? subpart+ - subpart+",
                "leader? part+ -?   subpart+",
                "leader? part+      subpart+",
                "- subpart",
            ],
        ),
        Compiler(
            label="missing_subpart",
            on_match=act.PART_MATCH,
            keep=act.ALL_LABELS,
            decoder=decoder,
            patterns=[
                "missing part+ -?   subpart+",
                "missing part+      subpart+",
                "missing subpart+",
            ],
        ),
        Compiler(
            label="not_a_part",
            on_match=REJECT_MATCH,
            decoder=decoder,
            patterns=[
                "- part+",
                "bad_part",
            ],
        ),
    ]
