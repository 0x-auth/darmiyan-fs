"""
Resolver I -- the inside view.

Knows three things: how many hops it has taken, the name of the directory it
is standing in, and the differences between successive names. It has no map,
no link table, no wall clock, and no access to the law.

It can fail. That is a feature: ELOOP is this resolver's only way of saying
"undefined", and where it says that is half the framework's output.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from fractions import Fraction


@dataclass
class Walk:
    values: list[Fraction]
    tau: Fraction           # proper time: sum of |differences|
    hops: int
    ending: str             # open | self-link | cycle of k | undefined name
    errno: int | None       # what the OS said when asked to RESOLVE

    @property
    def terminated(self) -> bool:
        return self.ending != "open"


class Inside:
    def __init__(self, path: str, entry: str):
        self.path = path
        self.entry = entry

    # ------------------------------------------------------------ the walk

    def walk(self, limit: int = 64) -> Walk:
        cur = os.path.join(self.path, self.entry)
        vals: list[Fraction] = []
        seen: dict[str, int] = {}
        hops, ending = 0, "open"
        while hops < limit:
            here = os.path.basename(os.path.realpath(cur))
            if here in seen:
                ending = f"cycle of {hops - seen[here]}"
                break
            seen[here] = hops
            try:
                n, d = here.split("_")
                vals.append(Fraction(int(n), int(d)))
            except ValueError:
                ending = "undefined name"
                break
            link = os.path.join(cur, "to")
            if not os.path.lexists(link):
                ending = "ran out (limit)"
                break
            tgt = os.path.basename(os.readlink(link))
            if tgt == here:
                ending = "self-link"
                break
            cur = os.path.join(self.path, tgt)
            hops += 1
        tau = sum((abs(vals[i] - vals[i - 1]) for i in range(1, len(vals))),
                  Fraction(0))
        return Walk(vals, tau, hops, ending, self._probe())

    def _probe(self) -> int | None:
        """What the OS says when asked to resolve rather than to read."""
        p = os.path.join(self.path, self.entry, "to")
        try:
            os.stat(p)
            return None
        except OSError as e:
            return e.errno

    # ------------------------------------------------------- the invariant

    def invariant(self, w: Walk) -> float | None:
        """
        D = r + 2 + 1/r, where r is the SIGNED limit of the ratio of
        consecutive differences -- the multiplier at the attracting fixed
        point. Measured from the walk alone. No matrix is ever seen.

        Returns None for finite orbits: a cycle gives no limit, and that
        limitation is reported rather than patched.
        """
        d = [w.values[i + 1] - w.values[i] for i in range(len(w.values) - 1)]
        d = [x for x in d if x != 0]
        if len(d) < 6:
            return None
        r = float(d[-1] / d[-2])
        if r == 0:
            return None
        return r + 2 + 1.0 / r
