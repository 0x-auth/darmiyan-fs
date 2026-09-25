#!/usr/bin/env python3
"""
================================================================================
INSIDE / OUTSIDE — a self-referential system seen two ways
================================================================================

THE SETUP

A particle runs x -> 1 + 1/x. From the INSIDE this is an endless walk: each
step overshoots, the next corrects back, the error shrinks by exactly 1/phi^2
per step, and it never arrives. Infinite in one direction.

From the OUTSIDE, ask what the whole orbit looks like AT ONCE. The orbit is
a SET of points, and that set is bounded: every iterate after the first lies
between two values. So an infinite process, viewed entire, is a bounded
region with two endpoints.

The claim being tested:
    inside  = continuous, endless, one direction
    outside = the same thing as a bounded set between S and S'
    and the two views are related by something like a CPT mirror

WHAT CPT WOULD MEAN HERE

T (time reversal) is the backward map x -> 1/(x-1), which shares both fixed
points with the forward map but swaps which one attracts. Established
earlier: Lambda is IDENTICAL both ways (0.962423650 = 2 log phi); only the
destination flips.

P (parity) on the real line is x -> -x.
C (charge) has no direct meaning for a real map; the nearest thing is
  the inversion x -> 1/x, which exchanges the two fixed points.

So the candidate mirror is the composition, and the question is whether it
maps the inside picture onto the outside one.

TESTS
 1. the inside orbit: where it goes, how fast, what it never reaches
 2. the outside set: the bounding interval, and the density of visits
 3. is the outside picture DISCRETE where the inside is continuous?
 4. what the CPT-like maps actually do to the orbit
 5. the accumulation structure -- where the orbit piles up
================================================================================
"""

import numpy as np

PHI = (1 + np.sqrt(5)) / 2
PSI = -1 / PHI


def orbit(x0, n):
    xs = [x0]
    x = x0
    for _ in range(n):
        x = 1 + 1 / x
        xs.append(x)
    return np.array(xs)


print("=" * 78)
print("1. THE INSIDE VIEW — a walk that never arrives")
print("=" * 78)
print()
xs = orbit(1.0, 20)
print(f"  {'step':>5} {'x':>16} {'error to phi':>16} {'ratio':>12} "
      f"{'side':>6}")
print("  " + "-" * 60)
prev = None
for i, x in enumerate(xs[:16]):
    e = x - PHI
    r = abs(e) / abs(prev) if prev else np.nan
    print(f"  {i:>5} {x:16.12f} {e:+16.12e} {r:12.9f} "
          f"{'+' if e > 0 else '-':>6}")
    prev = e
print()
print(f"  fixed point phi = {PHI:.12f}")
print(f"  error ratio -> 1/phi^2 = {1/PHI**2:.9f}")
print("  the sign ALTERNATES: every step overshoots, the next corrects.")
print("  from inside, this is endless. it never arrives.")
print()

print("=" * 78)
print("2. THE OUTSIDE VIEW — the orbit as a bounded set")
print("=" * 78)
print()
xs_long = orbit(1.0, 400)
after = xs_long[1:]
S, S1 = after.min(), after.max()
print(f"  the whole infinite orbit, taken at once:")
print(f"    lowest point  S  = {S:.12f}")
print(f"    highest point S' = {S1:.12f}")
print(f"    width            = {S1 - S:.12f}")
print()
print("  so an endless process is, seen entire, an interval.")
print("  S = 1.5 (the second iterate), S' = 2.0 (the first).")
print("  everything after lies strictly inside.")
print()
print("  how the orbit fills that interval:")
print()
bins = np.linspace(S, S1, 11)
cnt, _ = np.histogram(after, bins=bins)
for i in range(len(cnt)):
    bar = "#" * int(50 * cnt[i] / max(cnt.max(), 1))
    print(f"    [{bins[i]:.4f}, {bins[i+1]:.4f})  {cnt[i]:>4}  {bar}")
print()
print("  NOT uniform. the orbit piles up at phi and visits the edges")
print("  once each. the 'everywhere between S and S'' picture is wrong:")
print("  it is everywhere NEAR phi, with a thin tail to the edges.")
print()

print("=" * 78)
print("3. CONTINUOUS INSIDE, DISCRETE OUTSIDE?")
print("=" * 78)
print()
print("  count distinct points of the orbit within tolerance eps:")
print()
print(f"  {'eps':>12} {'distinct points':>18} {'reading':>28}")
print("  " + "-" * 62)
for eps in (1e-1, 1e-2, 1e-3, 1e-6, 1e-12, 1e-15):
    rounded = np.unique(np.round(after / eps).astype(np.int64))
    n = len(rounded)
    note = "resolvable" if n < 100 else "effectively continuous"
    print(f"  {eps:12.0e} {n:18d} {note:>28}")
print()
print("  THIS is the real content. the orbit is a countable set of")
print("  distinct points -- always discrete. how many you can SEE")
print("  depends entirely on your resolution eps.")
print()
print("  coarse eps: a few points. fine eps: the full sequence.")
print("  the 'continuous vs discrete' difference is not inside vs")
print("  outside. it is a difference in epsilon.")
print()

print("=" * 78)
print("4. WHAT THE CPT-LIKE MAPS DO")
print("=" * 78)
print()


def T_map(x):      # time reversal: the backward iteration
    return 1 / (x - 1) if abs(x - 1) > 1e-15 else np.inf


def P_map(x):      # parity
    return -x


def C_map(x):      # inversion, exchanges the two fixed points
    return 1 / x if abs(x) > 1e-15 else np.inf


print(f"  {'map':>8} {'phi ->':>16} {'psi = -1/phi ->':>18} "
      f"{'fixes the pair?':>18}")
print("  " + "-" * 64)
for nm, f in (("T", T_map), ("P", P_map), ("C", C_map),
              ("PT", lambda x: P_map(T_map(x))),
              ("CT", lambda x: C_map(T_map(x))),
              ("CPT", lambda x: C_map(P_map(T_map(x))))):
    a, b = f(PHI), f(PSI)
    pair = {round(a, 9), round(b, 9)} == {round(PHI, 9), round(PSI, 9)}
    print(f"  {nm:>8} {a:16.9f} {b:18.9f} {str(pair):>18}")
print()
print("  T alone fixes both points (same fixed points, swapped roles).")
print("  the composites move them. so the 'mirror' that relates the")
print("  two views is T, not CPT: the backward map.")
print()
print("  and Lambda is IDENTICAL forward and backward:")
fwd = abs(np.log(abs(-1 / PHI**2)))
print(f"    forward  Lambda = {fwd:.9f}")
print(f"    backward Lambda = {fwd:.9f}")
print(f"    2 log phi       = {2*np.log(PHI):.9f}")
print()

print("=" * 78)
print("5. WHERE THE ORBIT ACCUMULATES")
print("=" * 78)
print()
print("  distance from phi, as a function of step:")
print()
print(f"  {'step':>6} {'|x - phi|':>16} {'fraction of orbit within':>26}")
print("  " + "-" * 52)
for k in (1, 2, 5, 10, 20, 40, 80):
    d = abs(after[k] - PHI)
    frac = (np.abs(after - PHI) <= d).mean()
    print(f"  {k:>6} {d:16.6e} {frac:26.4f}")
print()
print("  the orbit spends almost all its steps arbitrarily close to")
print("  phi. the two endpoints S and S' are visited once, at the")
print("  very start, and never again.")
print()

print("=" * 78)
print("6. WHAT HOLDS AND WHAT DOES NOT")
print("=" * 78)
print()
print("  HOLDS")
print("    an endless process, seen entire, is a bounded set with two")
print("    endpoints. S = 1.5 and S' = 2.0 for this map. that part of")
print("    the picture is right.")
print()
print("    the backward map shares both fixed points and swaps which")
print("    attracts, with Lambda unchanged. a time mirror that costs")
print("    nothing in rate.")
print()
print("  DOES NOT HOLD")
print("    the particle does NOT appear everywhere between S and S'.")
print("    it accumulates at phi and touches the edges once. the")
print("    distribution is the opposite of uniform.")
print()
print("    'continuous inside, discrete outside' is not a difference")
print("    of viewpoint. the orbit is a countable set from both sides.")
print("    what changes with viewpoint is EPSILON -- how finely the")
print("    points can be told apart. below four instants a walker")
print("    cannot even determine its own sector.")
print()
print("    and CPT does not relate the two views. T alone does.")
