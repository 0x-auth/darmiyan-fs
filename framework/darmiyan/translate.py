"""
The AI seam.

A Translator turns a human description into a Relation spec -- a plain dict,
nothing more. The framework never calls a model; it calls this interface.
Anything satisfying it can be plugged in: a regex, an LLM, a lookup table.

The contract is deliberately narrow. A translator may choose a, b, c, d, a
seed and a step count. It may not choose the invariant, the sector, or the
answer. Those are the framework's to find.
"""

from __future__ import annotations

from typing import Protocol


class Translator(Protocol):
    def to_spec(self, text: str) -> dict:
        ...


class KeywordTranslator:
    """
    The trivial one, so the seam is exercised rather than described.
    Replace with an LLM call that returns the same dict shape.
    """

    TABLE = {
        "golden":    dict(a=1, b=1, c=1, d=0, seed=1),
        "boost":     dict(a=2, b=1, c=1, d=1, seed=1),
        "shift":     dict(a=1, b=1, c=0, d=1, seed=0),
        "parabolic": dict(a=2, b=-1, c=1, d=0, seed=2),
        "rotation":  dict(a=0, b=-1, c=1, d=0, seed=2),
        "order3":    dict(a=0, b=-1, c=1, d=-1, seed=2),
        "fixed":     dict(a=2, b=-1, c=1, d=0, seed=1),
        "horizon":   dict(a=0, b=1, c=1, d=-1, seed=2),
    }

    def to_spec(self, text: str) -> dict:
        t = text.lower()
        for k, v in self.TABLE.items():
            if k in t:
                return {"name": k, **v}
        raise ValueError(
            f"no relation matches {text!r}. known: {sorted(self.TABLE)}. "
            "A real translator would emit a, b, c, d directly."
        )
