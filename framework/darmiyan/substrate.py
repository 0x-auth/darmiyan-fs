"""
The moving substrate -- added in 1.1.0.

Everything in 1.0.0 had a STATIC artifact: the relation was written once,
then walked. Only the walker moved. That was the framework's blind spot, and
it is exactly the thing cosmology is about -- space stretching between
things rather than things moving through space.

THE LAW

    D -> D - 1 + h * D^(1-p)

    D   separation, in nodes, between walker and target
    h   stretch rate
    p   dilution exponent: how fast the stretch falls off with separation

The walker removes exactly 1 per tick. The substrate adds h*D^(1-p). The
whole behaviour is the fight between a constant and a power.

THREE OUTCOMES, AND THE THIRD IS NEW

    ARRIVES   D reaches 0. the ordinary case.
    ESCAPES   D grows without bound. a HORIZON -- the substrate outruns the
              walker. not a fixed point of a map; the relation never stops
              and the walker never stops.
    STALLS    D converges to a FLOOR it can neither cross nor leave. a
              minimum separation. neither arrival nor horizon.

The floor is exact. Solving D - 1 + h*D^(1-p) = D:

    h * D*^(1-p) = 1      =>      D* = h^(1/(p-1))          for p > 1

and it is stable iff |f'(D*)| < 1, where f'(D*) = 1 - (p-1)/D*, hence

    STABLE  <=>  D* > (p-1)/2

Below that threshold the separation oscillates forever around a floor it
never reaches. Relaxation time is 1/(1-|f'|) = D*/(p-1), which matters in
practice: a SLOW floor and an UNSTABLE floor look identical if you do not
run long enough. That mistake was made during development and it is the
reason `relaxation_ticks` is part of the public result.

WHICH p THE SKY HAS

    p = 0   stretch h*D, grows with D        -> horizon at D = 1/h
    p = 1   stretch h, constant              -> marginal
    p > 1   stretch falls off                -> floor, no horizon ever

The real universe has an event horizon, so the real exponent is 0: Lambda is
CONSTANT. That is the whole content of "dark energy does not dilute". Any
inverse power of separation dilutes, and a diluting substrate cannot cut
anything off.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


class SubstrateError(ValueError):
    pass


@dataclass(frozen=True)
class Outcome:
    """What a walk against a moving substrate did."""
    outcome: str                 # arrives | escapes | stalls
    ticks: int
    final_D: float
    floor: float | None          # D* = h^(1/(p-1)), None for p <= 1
    floor_stable: bool | None
    relaxation_ticks: float | None
    h: float
    p: float
    D0: float

    def as_dict(self) -> dict:
        return {
            "outcome": self.outcome, "ticks": self.ticks,
            "final_D": self.final_D, "floor": self.floor,
            "floor_stable": self.floor_stable,
            "relaxation_ticks": self.relaxation_ticks,
            "h": self.h, "p": self.p, "D0": self.D0,
        }


def floor_of(h: float, p: float) -> float | None:
    """D* = h^(1/(p-1)). None when p <= 1, where no floor exists."""
    if p <= 1:
        return None
    if h <= 0:
        raise SubstrateError("h must be positive")
    return h ** (1.0 / (p - 1.0))


def floor_is_stable(h: float, p: float) -> bool | None:
    """|f'(D*)| < 1 iff D* > (p-1)/2."""
    ds = floor_of(h, p)
    if ds is None:
        return None
    return ds > (p - 1.0) / 2.0


def relaxation(h: float, p: float) -> float | None:
    """
    1/(1-|f'(D*)|) = D*/(p-1), computed ANALYTICALLY.

    Not from the float expression 1-(1-(p-1)/D*): for a large floor that
    subtraction underflows to zero and the relaxation comes out infinite.
    The algebraic form has no such problem, and some floors in this work
    have D* ~ 1e60 where it matters.
    """
    ds = floor_of(h, p)
    if ds is None:
        return None
    return ds / (p - 1.0)


def walk(D0: float, h: float, p: float = 0.0,
         ticks: int = 200_000, escape_at: float = 1e12) -> Outcome:
    """Step a walker against a substrate diluting as D^(1-p)."""
    if D0 <= 0:
        raise SubstrateError("D0 must be positive")
    if p < 0:
        raise SubstrateError("p must be non-negative")
    D = float(D0)
    res = "stalls"
    t = ticks
    for t in range(1, ticks + 1):
        if D <= 0:
            res = "arrives"
            break
        D = D - 1.0 + (h * D ** (1.0 - p) if h else 0.0)
        if D > escape_at:
            res = "escapes"
            break
    else:
        res = "arrives" if D <= 0 else "stalls"
    return Outcome(outcome=res, ticks=t, final_D=D,
                   floor=floor_of(h, p) if h else None,
                   floor_stable=floor_is_stable(h, p) if h else None,
                   relaxation_ticks=relaxation(h, p) if h else None,
                   h=h, p=p, D0=float(D0))


def horizon(h: float) -> float:
    """
    For p = 0 the boundary sits at D = 1/h, to the node.

    Measured, not asserted: see `darmiyan substrate --scan`.
    """
    if h <= 0:
        raise SubstrateError("h must be positive")
    return 1.0 / h
