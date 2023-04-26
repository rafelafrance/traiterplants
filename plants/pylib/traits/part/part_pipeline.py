from spacy import Language
from traiter.pylib.traits import add_pipe as add

from . import part_action as act
from . import part_patterns as pat


def build(nlp: Language, **kwargs):

    with nlp.select_pipes(enable="tokenizer"):
        prev = add.term_pipe(nlp, name="part_terms", path=act.ALL_CSVS, **kwargs)

    # prev = add.debug_tokens(nlp, after=prev)  # ################################

    prev = add.trait_pipe(
        nlp,
        name="part_patterns",
        compiler=pat.part_patterns(),
        after=prev,
    )

    prev = add.cleanup_pipe(
        nlp, name="part_cleanup", delete=["missing", "bad_part"], after=prev
    )

    return prev
