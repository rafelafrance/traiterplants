from spacy import registry
from traiter.pylib import actions
from traiter.pylib import const as t_const
from traiter.pylib.pattern_compilers.matcher import Compiler
from traiter.pylib.patterns import common

from .term import TAXON_RANKS
from .term import TAXON_TERMS


_DECODER = common.PATTERNS | {
    "auth": {"SHAPE": {"IN": t_const.NAME_SHAPES}},
    "taxon": {"ENT_TYPE": "taxon"},
    "_": {"TEXT": {"REGEX": r"^[:._;,]+$"}},
}


# ###################################################################################
MULTI_TAXON = Compiler(
    "multi_taxon",
    on_match="plant_multi_taxon_v1",
    decoder=_DECODER,
    patterns=[
        "taxon and taxon",
    ],
)


@registry.misc(MULTI_TAXON.on_match)
def on_multi_taxon_match(ent):
    taxa = []

    for token in ent:
        if token.ent_type_ == "taxon":
            taxa.append(TAXON_TERMS.replace.get(token.lower_, token.text))
            ent._.data["rank"] = TAXON_RANKS.replace.get(token.lower_, "unknown")

    ent._.data["taxon"] = taxa


# ###################################################################################
TAXON_PLUS1 = Compiler(
    "taxon_auth",
    on_match="plant_taxon_plus1_v1",
    decoder=_DECODER,
    patterns=[
        "taxon ( auth+           _? )",
        "taxon ( auth+ and auth+ _? )",
        "taxon   auth+               ",
        "taxon   auth+ and auth+     ",
        "taxon ( auth+           _? ) auth+",
        "taxon ( auth+ and auth+ _? ) auth+",
    ],
)


@registry.misc(TAXON_PLUS1.on_match)
def on_taxon_auth_match(ent):
    auth = []

    taxon_ = [e for e in ent.ents if e.label_ == "taxon"]
    if len(taxon_) != 1:
        raise actions.RejectMatch()

    for token in ent:
        if token.ent_type_ == "taxon":
            continue

        if auth and token.lower_ in common.AND:
            auth.append("and")

        elif token.shape_ in t_const.NAME_SHAPES:
            auth.append(token.text)

    ent._.data["taxon"] = taxon_[0]._.data["taxon"]
    ent._.data["rank"] = taxon_[0]._.data["rank"]
    ent._.data["authority"] = " ".join(auth)
    ent._.new_label = "taxon"
