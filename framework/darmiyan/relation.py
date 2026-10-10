"""
The artifact: a relation laid down as structure.

A Relation is the only object in this framework. It is NOT code that runs.
It is a law written down as directories and symlinks, so that something can
later walk it without being told what it is walking.

Nothing written to disk records the law, the sector, the invariant, or a
clock. That is the whole point: the reader has to find out.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Callable, Iterator


class RelationError(Exception):
    pass


def _name(x: Fraction | None) -> str:
    if x is None:
        return "inf"
    return f"{x.numerator}_{x.denominator}"


def _value(s: str) -> Fraction | None:
    if s == "inf":
        return None
    n, d = s.split("_")
    return Fraction(int(n), int(d))


@dataclass
class Relation:
    """
    A law x -> (a x + b) / (c x + d), materialised as structure.

    The Mobius family is the default because its answers are known in
    advance, which is what makes the bridge checkable rather than
    decorative. `step` may be replaced with any map on the rationals; the
    inside resolver will still work, and the outside resolver will report
    that it cannot recover a Mobius law, which is the honest outcome.
    """

    name: str
    a: int = 1
    b: int = 1
    c: int = 1
    d: int = 0
    seed: Fraction = field(default_factory=lambda: Fraction(1))
    steps: int = 28
    root: str = "/var/darmiyan"

    # ------------------------------------------------------------- the law

    def step(self, x: Fraction | None) -> Fraction | None:
        if x is None:
            return None if self.c == 0 else Fraction(self.a, self.c)
        den = self.c * x + self.d
        if den == 0:
            return None
        return Fraction(self.a * x + self.b, den)

    def orbit(self) -> Iterator[Fraction | None]:
        x: Fraction | None = self.seed
        seen = set()
        for _ in range(self.steps):
            k = _name(x)
            if k in seen:
                return
            seen.add(k)
            yield x
            nxt = self.step(x)
            if nxt == x:
                return
            x = nxt

    # --------------------------------------------------------- the writing

    @property
    def path(self) -> str:
        return os.path.join(self.root, self.name)

    def materialise(self, clean: bool = True) -> str:
        """
        Write the relation to disk. Directories are states; a symlink `to`
        is the law. No metadata of any kind is written.
        """
        if clean and os.path.exists(self.path):
            shutil.rmtree(self.path)
        os.makedirs(self.path, exist_ok=True)

        x: Fraction | None = self.seed
        seen: set[str] = set()
        for _ in range(self.steps):
            here = _name(x)
            if here in seen:
                break
            seen.add(here)
            os.makedirs(os.path.join(self.path, here), exist_ok=True)
            nxt = self.step(x)
            nkey = _name(nxt)
            os.makedirs(os.path.join(self.path, nkey), exist_ok=True)
            link = os.path.join(self.path, here, "to")
            if not os.path.lexists(link):
                os.symlink(os.path.join("..", nkey), link)
            if nxt == x:
                break
            x = nxt
        return self.path

    @property
    def entry(self) -> str:
        return _name(self.seed)

    # ------------------------------------------- the answer, for CHECKING only

    def truth(self) -> float | None:
        """
        D = tr^2 / det, the scale-free invariant. Used ONLY to check the
        bridge during development. No resolver may call this.
        """
        det = self.a * self.d - self.b * self.c
        if det == 0:
            return None
        return (self.a + self.d) ** 2 / det


def from_spec(spec: dict) -> Relation:
    """Build a Relation from a plain dict. This is the seam an AI layer
    writes to: natural language in, this dict out, nothing else."""
    required = {"name"}
    missing = required - set(spec)
    if missing:
        raise RelationError(f"spec missing {sorted(missing)}")
    seed = spec.get("seed", 1)
    return Relation(
        name=str(spec["name"]),
        a=int(spec.get("a", 1)), b=int(spec.get("b", 1)),
        c=int(spec.get("c", 1)), d=int(spec.get("d", 0)),
        seed=Fraction(seed),
        steps=int(spec.get("steps", 28)),
        root=str(spec.get("root", "/var/darmiyan")),
    )
