from traiter.pylib.term_list import TermList

from .. import const

ADMIN_UNIT_TERMS = TermList().shared("us_locations")

PLANT_TERMS = TermList().shared("labels numerics time units")
PLANT_TERMS += TermList().read(const.TREATMENT_CSV)
PLANT_TERMS += TermList().read(const.VOCAB_DIR / "ranks.csv")

TAXON_TERMS = TermList().read(const.TAXON_CSV)
MONOMIAL_TERMS = TAXON_TERMS.split("monomial")
BINOMIAL_TERMS = TAXON_TERMS.split("binomial")
TAXON_RANKS = TAXON_TERMS.pattern_dict("ranks")
RANK_TERMS = TermList().read(const.VOCAB_DIR / "ranks.csv")
RANK_ABBREV = RANK_TERMS.pattern_dict("abbrev")
