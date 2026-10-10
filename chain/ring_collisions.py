#!/usr/bin/env python3
"""
================================================================================
RING_COLLISIONS -- when is the ring -> secret map one-to-one?
================================================================================

THE FRONTIER, from darmiyan-recognition:

    "For which nonlinear families is the ring -> secret map one-to-one?"

That repo measured 29 of 40 secrets sharing a ring in one family. One number
from one family is an observation. This turns it into a measurement: vary the
family along declared structural axes and see which axis drives the collision
rate.

EXPECTATION, WRITTEN BEFORE RUNNING (method/refute.py discipline)

  H1  Collisions are driven by the map being MANY-TO-ONE on the state space,
      not by nonlinearity as such. A nonlinear BIJECTION should ring
      one-to-one; a non-bijective map collapses secrets together.

  H1 is probably WRONG as stated, and I expect the run to show it, because
  ECC point multiplication IS a bijection on the group and is still hard.
  So bijectivity cannot be sufficient. The interesting outcome is finding
  what it is necessary-but-not-sufficient FOR.

  H2  Collision rate rises as the orbit's period falls relative to the
      secret space. If there are more secrets than distinguishable orbits,
      the pigeonhole does the collapsing and nothing about nonlinearity is
      involved. This is the boring explanation and it must be controlled for
      before any structural claim is made.

WHAT IS MEASURED

  For each family and each secret S:
    - run the recurrence, take its orbit
    - compute the "ring": the normalised power spectrum, binned
    - two secrets COLLIDE if their rings are indistinguishable

  Reported: collision rate, distinct-ring count, period statistics, and
  whether the family's map is a bijection on the state space.

Run:  python3 ring_collisions.py
================================================================================
"""

import math
from collections import Counter, defaultdict

import numpy as np

rng = np.random.default_rng(515)

P = 1021          # prime modulus for the state space
NSEC = 200        # secrets tested per family
ORBIT = 256       # orbit length sampled
BINS = 48         # spectral resolution of "the ring"


# ============================================================ the families

def f_linear(x, s, p=P):
    return (x + s) % p


def f_affine(x, s, p=P):
    return (s * x + 1) % p


def f_quadratic(x, s, p=P):
    return (x * x + s) % p


def f_cubic(x, s, p=P):
    return (x * x * x + s) % p


def f_pow_bijection(x, s, p=P):
    """x -> x^(2s+1) mod p. Odd exponents coprime to p-1 are bijections."""
    e = 2 * s + 1
    return pow(x, e, p)


def f_mul_bijection(x, s, p=P):
    """x -> s*x mod p for s != 0. A nonlinear-looking but exact bijection."""
    return ((s % (p - 1)) + 1) * x % p


def f_sbox(x, s, p=P):
    """x -> (x^3 + s*x) mod p. Nonlinear, bijective only for some s."""
    return (x * x * x + s * x) % p


FAMILIES = {
    "linear  x+s":            f_linear,
    "affine  s*x+1":          f_affine,
    "quadratic  x^2+s":       f_quadratic,
    "cubic  x^3+s":           f_cubic,
    "power  x^(2s+1)":        f_pow_bijection,
    "multiply  (s+1)*x":      f_mul_bijection,
    "sbox  x^3+s*x":          f_sbox,
}


# ================================================================ the ring

def orbit(f, s, x0=2, n=ORBIT):
    x, out = x0, []
    for _ in range(n):
        out.append(x)
        x = f(x, s)
    return np.array(out, float)


def ring(seq, bins=BINS):
    """
    The normalised power spectrum, coarse-binned. This is 'what the system
    rings at' with amplitude information discarded, which is the point: a
    ring is a set of frequencies, not a waveform.
    """
    v = seq - seq.mean()
    if v.std() == 0:
        return ("silent",)
    sp = np.abs(np.fft.rfft(v * np.hanning(len(v))))
    sp = sp / (sp.max() or 1)
    idx = np.linspace(0, len(sp), bins + 1).astype(int)
    coarse = [sp[idx[i]:idx[i + 1]].max() if idx[i + 1] > idx[i] else 0.0
              for i in range(bins)]
    return tuple(int(round(c * 7)) for c in coarse)      # 3-bit quantisation


def period(f, s, x0=2, limit=4000):
    seen, x = {}, x0
    for i in range(limit):
        if x in seen:
            return i - seen[x]
        seen[x] = i
        x = f(x, s)
    return limit


def is_bijection(f, s, p=P):
    return len({f(x, s) for x in range(p)}) == p


# ==================================================================== run

def main():
    W = 78
    print("=" * W)
    print("  EXPECTATION, RECORDED BEFORE THE RUN")
    print("=" * W)
    print()
    for line in [
        "H1 collisions are driven by the map being many-to-one on the state",
        "   space, not by nonlinearity. I expect this to be WRONG as stated,",
        "   because ECC point multiplication is a bijection and still hard.",
        "H2 collision rate rises when there are more secrets than",
        "   distinguishable orbits. the boring explanation; control first.",
    ]:
        print("  " + line)
    print()

    print("=" * W)
    print("  THE MEASUREMENT")
    print("=" * W)
    print()
    print(f"  modulus {P}, {NSEC} secrets per family, orbit {ORBIT}, "
          f"{BINS} spectral bins")
    print()
    print(f"  {'family':>22} {'bijection':>10} {'distinct':>9} {'collide':>9} "
          f"{'biggest':>8} {'med period':>11}")
    print("  " + "-" * 74)

    rows = []
    for name, f in FAMILIES.items():
        secrets = list(range(1, NSEC + 1))
        rings = {}
        periods = []
        for s in secrets:
            rings[s] = ring(orbit(f, s))
            periods.append(period(f, s))
        groups = defaultdict(list)
        for s, r in rings.items():
            groups[r].append(s)
        distinct = len(groups)
        collided = sum(len(v) for v in groups.values() if len(v) > 1)
        biggest = max(len(v) for v in groups.values())
        bij = is_bijection(f, secrets[0])
        med = int(np.median(periods))
        rows.append((name, bij, distinct, collided, biggest, med,
                     len(secrets)))
        print(f"  {name:>22} {str(bij):>10} {distinct:>9} "
              f"{f'{collided}/{len(secrets)}':>9} {biggest:>8} {med:>11}")
    print()

    print("=" * W)
    print("  H2 FIRST: IS IT JUST PIGEONHOLE?")
    print("=" * W)
    print()
    print("  if a family has fewer distinguishable orbits than secrets, the")
    print("  collapse is counting, not structure. compare distinct rings")
    print("  against distinct PERIODS -- if rings track periods, the ring is")
    print("  reading orbit length and nothing deeper.")
    print()
    print(f"  {'family':>22} {'distinct rings':>15} {'distinct periods':>17} "
          f"{'ratio':>8}")
    print("  " + "-" * 66)
    for name, f in FAMILIES.items():
        secrets = list(range(1, NSEC + 1))
        dr = len({ring(orbit(f, s)) for s in secrets})
        dp = len({period(f, s) for s in secrets})
        print(f"  {name:>22} {dr:>15} {dp:>17} "
              f"{(dr / dp if dp else float('nan')):>8.2f}")
    print()

    print("=" * W)
    print("  H1: DOES BIJECTIVITY PREDICT THE COLLISION RATE?")
    print("=" * W)
    print()
    bij_rates = [(r[3] / r[6]) for r in rows if r[1]]
    non_rates = [(r[3] / r[6]) for r in rows if not r[1]]
    print(f"  {'group':>28} {'n families':>12} {'mean collision rate':>21}")
    print("  " + "-" * 64)
    if bij_rates:
        print(f"  {'bijective on state space':>28} {len(bij_rates):>12} "
              f"{np.mean(bij_rates):>21.4f}")
    if non_rates:
        print(f"  {'not bijective':>28} {len(non_rates):>12} "
              f"{np.mean(non_rates):>21.4f}")
    print()

    print("=" * W)
    print("  THE CONTROL THAT MATTERS: SHUFFLE THE SECRET LABELS")
    print("=" * W)
    print()
    print("  if the ring carried NO information about the secret, randomly")
    print("  relabelling secrets would not change the collision structure.")
    print("  so: compare each family's collision rate against the rate for")
    print("  a family whose 'secret' is ignored entirely.")
    print()

    def f_ignore(x, s, p=P):
        return (x * x + 7) % p          # same shape, secret does nothing

    secrets = list(range(1, NSEC + 1))
    rr = {s: ring(orbit(f_ignore, s)) for s in secrets}
    g = defaultdict(list)
    for s, r in rr.items():
        g[r].append(s)
    print(f"  {'secret-ignoring control':>28} distinct rings {len(g):>4}  "
          f"collide {sum(len(v) for v in g.values() if len(v) > 1)}"
          f"/{len(secrets)}")
    print()
    print("  a family whose collision rate matches this control is a family")
    print("  whose ring tells you nothing about its secret.")
    print()

    print("=" * W)
    print("  WHAT THIS DOES AND DOES NOT SETTLE")
    print("=" * W)
    print()
    print("  read the tables above, not this paragraph. the structure of the")
    print("  question is: collision rate is the dependent variable,")
    print("  bijectivity and period are the declared candidates, and the")
    print("  secret-ignoring family is the floor.")
    print()
    print("  what this CANNOT settle: real ECC and SHA are bijective, have")
    print("  astronomically long periods, and ring many-to-one anyway. so")
    print("  whatever drives collisions here, a family can satisfy it and")
    print("  still be hard. this measures a necessary condition at best.")


if __name__ == "__main__":
    main()
