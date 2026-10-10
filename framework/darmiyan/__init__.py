"""
darmiyan -- a two-chart emulator for self-referential relations.

One object (Relation), two resolvers (Inside, Outside), one enforced
contract (the bridge). Everything else is a view on those.

    >>> import darmiyan
    >>> r = darmiyan.read(darmiyan.spec(name="golden", a=1, b=1, c=1, d=0))
    >>> r.agreement
    'exact'
"""

from .relation import Relation, from_spec, RelationError
from .inside import Inside, Walk
from .outside import Outside
from .bridge import read, Reading, BridgeViolation
from .translate import Translator, KeywordTranslator
from .substrate import (walk, Outcome, floor_of, floor_is_stable,
                        relaxation, horizon, SubstrateError)

__version__ = "1.1.0"

__all__ = [
    "Relation", "from_spec", "spec", "RelationError",
    "Inside", "Walk", "Outside",
    "read", "Reading", "BridgeViolation",
    "Translator", "KeywordTranslator",
    "walk", "Outcome", "floor_of", "floor_is_stable",
    "relaxation", "horizon", "SubstrateError",
]


def spec(**kw) -> Relation:
    """Build a Relation from keywords. The one constructor you need."""
    return from_spec(kw)


def from_text(text: str, translator: Translator | None = None) -> Reading:
    """Natural language in, a checked Reading out."""
    tr = translator or KeywordTranslator()
    return read(from_spec(tr.to_spec(text)))
