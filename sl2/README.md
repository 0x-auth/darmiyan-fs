# sl2 — the between, computed

Work from 19–21 September 2026. Everything here is exact algebra or an
exactly-reproducible computation. No sampling, no p-values.

Nothing in this directory is new mathematics. It is standard SL(2,R)
theory — Fricke identities, character varieties, the Markov surface —
found by following one question: what is the invariant of a *pair* of
self-referential relations, as opposed to one.

## The core

    Δ = tr² − 4·det                     one relation
    κ = x² + y² + z² − xyz              a pair, x=trA, y=trB, z=trAB
    Δ([A,B]) = κ(κ − 4)                 verified to machine zero

Δ's sign sorts a relation into three kinds. The sign is fixed by the
generator alone: for X traceless, sector(exp X) = −sign(det X).

    det X < 0  →  Δ > 0   boost      two real fixed points, arrowed
    det X = 0  →  Δ = 0   parabolic  one merged fixed point
    det X > 0  →  Δ < 0   rotation   complex pair, cycles, no arrow

The Killing form on sl(2,R) has eigenvalues (−1, −½, +½): signature
1+, 2−. It is the Minkowski metric of 2+1 spacetime, and its light
cone is exactly the parabolic locus. The group carries its own causal
structure before any spacetime is mentioned.

## Files

| file | what it establishes |
|---|---|
| `structure.py` | Δ, the generator classification, the Killing form, Fricke |
| `kappa.py` | κ = 0 is the Markov surface (3× the Markov triples); κ = 4 is α ± β ± γ = 0 |
| `delta_pair.py` | closed form for Δ(K); the two between-points s = ±(ad−bc)/√(bc+d²) |
| `two_clocks.py` | **l = Λ exactly** — hyperbolic translation length equals the Lyapunov exponent |
| `observer_error.py` | two errors, mutually blind; κ(A,B) = κ(B,A) exactly |
| `instants.py` | four instants to know your own law — the one non-identity result |
| `backward.py` | x → 1+1/x backwards is the Euclidean algorithm; det F = −1 |
| `horizon_split.py` | Unruh: pure → thermal at T = a/2π to 2e-16; Δ(boost) tracks entropy |

## Two results worth reading first

**l = Λ.** The hyperbolic translation length of a map — how far a point
moves in the metric the map preserves — equals log|μ| at the fixed point,
to 1e-15, by two entirely separate derivations. So "error of time" and
"arrow of time" are one quantity read two ways: rate of divergence, and
rate of proper-time accumulation. The error between the two clocks is the
walker's distance from the relation's own axis. On the axis they agree.

**Four instants.** A Möbius law has 3 degrees of freedom; k observations
give k−1 constraints. Below four instants the surviving solution space
*crosses* the parabolic locus, so the system cannot determine whether it
has an arrow at all. At k=3 the Δ numerator factors as a product of two
real linear forms — two crossings, exactly. This is tested algebraically,
not by sampling.

## What is not here

No scale (Δ gives every ratio and no unit). No source (curvature from
incoherence, no stress-energy). 2+1 only — PSL(2,C) ≅ SO(3,1) has not
been taken. One pair, not a network. And nothing falsifiable: every
result is an identity, true by what the terms mean.
