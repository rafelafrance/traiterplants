from spacy import registry
from traiter.pylib.matcher_compiler import Compiler
from traiter.pylib.patterns import common

from ..vocabulary import terms

_PART_LEADER = """ primary secondary """.split()

_DECODER = common.PATTERNS | {
    "leader": {"LOWER": {"IN": _PART_LEADER}},
    "part": {"ENT_TYPE": {"IN": terms.PART_ENTS}},
    "subpart": {"ENT_TYPE": {"IN": terms.SUBPART_ENTS}},
}

# ####################################################################################
PART = Compiler(
    "part",
    decoder=_DECODER,
    patterns=[
        "leader? part",
        "leader? part -? part",
        "leader? part -? subpart",
        "leader? part    subpart+",
    ],
)


@registry.misc(PART.on_match)
def on_part_match(ent):
    words = []
    new_label = None

    for token in ent:
        label = token._.cached_label
        if label in terms.PART_ENTS:
            new_label = label

        words.append(terms.PLANT_TERMS.replace.get(token.lower_, token.lower_))

    ent._.data[new_label] = " ".join(words)
    ent._.data[new_label] = ent._.data[new_label].replace(" - ", "-")
    ent._.new_label = new_label


# ####################################################################################
MULTIPLE_PARTS = Compiler(
    "multiple_parts",
    decoder=_DECODER,
    patterns=[
        "leader? part and part",
    ],
)


@registry.misc(MULTIPLE_PARTS.on_match)
def on_multiple_parts_match(ent):
    ent._.new_label = "multiple_parts"
    ent._.data["multiple_parts"] = [
        terms.PLANT_TERMS.replace.get(t.lower_, t.lower_)
        for t in ent
        if t._.cached_label in terms.PARTS_SET
    ]


# ####################################################################################
MISSING_PART = Compiler(
    "missing_part",
    decoder=_DECODER,
    patterns=[
        "missing part",
        "missing part  -  part",
        "missing part and part",
        "missing part -?  subpart",
        "missing part     subpart",
    ],
)


@registry.misc(MISSING_PART.on_match)
def missing_part_match(ent):
    if part := next((t for t in ent if t.ent_type_ == "part"), None):
        ent._.data["part"] = terms.PLANT_TERMS.replace.get(part.lower_, part.lower_)
    ent._.data["missing_part"] = ent.text.lower()
