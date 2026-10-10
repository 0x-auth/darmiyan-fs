"""
The bridge -- the framework's one enforced contract.

Two resolvers compute the same invariant from disjoint information. If they
disagree, NO RESULT IS RETURNED. That refusal is what distinguishes a
framework from a collection of scripts: you cannot get an answer out of this
system without both charts agreeing on what they are looking at.

The invariant is D = tr^2 / det, which is scale-free. Outside derives it by
exact algebra over the rationals. Inside measures it from its own error
sequence. Neither can see the other's input.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

from .inside import Inside, Walk
from .outside import Outside
from .relation import Relation

TOL = 1e-6
LOOSE = 1e-2


class BridgeViolation(Exception):
    """The charts disagree. There is no result to return."""


@dataclass
class Reading:
    name: str
    d_inside: float | None
    d_outside: float | None
    agreement: str                 # exact | close | one-sided | none
    tau: float                     # inside only; outside has no clock
    hops: int
    inside_says: str
    outside_says: list[str]
    disagreement: str | None       # the payload
    errno: int | None

    def as_dict(self) -> dict:
        return asdict(self)


def classify(w: Walk, fixed: list[str]) -> str | None:
    """
    The two chart disagreements, which are the point of the pair.

    CLASS 1: inside reports a terminating failure where outside reports an
             ordinary object. Deadlock, stall, control lock.
    CLASS 2: inside reaches a name it cannot parse where outside reports an
             ordinary point in another chart. Gimbal lock -- the coordinate
             died, the system did not.
    """
    if w.ending in ("self-link",) or w.ending.startswith("cycle"):
        return (f"CLASS 1  inside: {w.ending}  |  outside: "
                f"{'fixed point' if w.ending == 'self-link' else 'finite orbit'}"
                f" {', '.join(fixed) if fixed else '(not recoverable)'}")
    if w.ending == "undefined name":
        return (f"CLASS 2  inside: unparseable name at the horizon  |  "
                f"outside: ordinary points {', '.join(fixed)}")
    return None


def read(rel: Relation, limit: int = 64, materialise: bool = True) -> Reading:
    """
    The framework's single operation. Walk, read, cross-check, refuse on
    disagreement.

    `materialise=False` reads whatever is already on disk. That matters more
    than it looks: an earlier version always rebuilt the artifact from the
    law before reading it, which silently repaired any corruption and made
    the contract untestable. A framework whose reader regenerates what it is
    supposed to discover is not reading anything.
    """
    path = rel.materialise() if materialise else rel.path
    ins, out = Inside(path, rel.entry), Outside(path)

    w = ins.walk(limit=limit)
    d_in = ins.invariant(w)
    d_out = out.invariant()
    fixed = out.fixed_points()

    if d_in is None and d_out is None:
        agreement = "none"
    elif d_in is None or d_out is None:
        agreement = "one-sided"
    else:
        diff = abs(d_in - d_out)
        if diff < TOL:
            agreement = "exact"
        elif diff < LOOSE:
            agreement = "close"
        else:
            raise BridgeViolation(
                f"{rel.name}: inside says D = {d_in:.9f}, outside says "
                f"D = {d_out:.9f}, difference {diff:.3e}. The two charts are "
                f"not describing the same relation. No result returned."
            )

    return Reading(
        name=rel.name,
        d_inside=d_in,
        d_outside=d_out,
        agreement=agreement,
        tau=float(w.tau),
        hops=w.hops,
        inside_says=w.ending,
        outside_says=fixed,
        disagreement=classify(w, fixed),
        errno=w.errno,
    )
