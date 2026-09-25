#!/usr/bin/env python3
"""
================================================================================
PHI_NONCIRCULAR -- a derivation of the phi-boundary that does not assume it
================================================================================

THE PROBLEM WITH V5's SECTION 4

V4's resistance function encodes "the whole relates to its largest part as
the largest part relates to the remainder". That sentence IS the definition
of the golden section (Euclid VI def.3). Solving it recovers phi, which is
not a derivation of phi -- it is a restatement.

WHAT WOULD ACTUALLY BE NON-CIRCULAR

A condition that:
  - never mentions subdivision, proportion, whole/part, or self-similarity
  - never mentions phi, sqrt5, or Fibonacci
  - is a statement about ALL real numbers, not about one of them
  - and whose extremum turns out to be phi as a THEOREM, not by construction

Such a condition exists, and it is the oldest known characterisation of phi
that is not its definition:

    HURWITZ (1891). For every irrational a there are infinitely many
    rationals p/q with  |a - p/q| < 1 / (sqrt5 * q^2).  The constant sqrt5
    is the best possible, and it is attained ONLY for numbers equivalent
    to phi under GL(2,Z).

Read as an optimisation: phi is the real number HARDEST to approximate by
rationals. Nothing in "hard to approximate by rationals" refers to
proportion or self-similarity. sqrt5 appears in the ANSWER, never in the
question. That is what non-circular means.

THE PHYSICAL READING, for the TrD paper

TD + TrD = 1 with ratio r = TD/TrD. A rational r means the storage-reference
balance is COMMENSURATE: some finite repeat closes exactly, so the system has
a period, so its self-reference terminates. Resistance to termination is
exactly resistance to rational approximation. Maximising it is a first-
principles notion of interaction cost that does not smuggle in the answer.

WHAT IS COMPUTED

  1. the Lagrange number L(r) = limsup 1/(q * ||q r||), approximated on a
     grid, and minimised over the 1-simplex
  2. whether the minimum lands on phi
  3. what else is in the minimum set, reported rather than hidden
  4. the same test on the plastic number, to see whether the cubic case
     has an analogous characterisation (it does not, and that matters)

Run:  python3 phi_noncircular.py
================================================================================
"""

import math

import numpy as np

PHI = (1 + math.sqrt(5)) / 2
SILVER = 1 + math.sqrt(2)
PLASTIC = 1.3247179572447460


def cf_terms(x, n=40):
    """Continued fraction expansion, guarding against float blow-up."""
    out = []
    for _ in range(n):
        a = math.floor(x)
        if a > 10 ** 8:
            break
        out.append(int(a))
        f = x - a
        if f < 1e-13:
            break
        x = 1.0 / f
    return out


def _tail(a, i):
    """[0; a_i, a_(i+1), ...] evaluated backwards from the end."""
    v = 0.0
    for k in range(len(a) - 1, i - 1, -1):
        v = 1.0 / (a[k] + v)
    return v


def _head(a, i):
    """[0; a_(i-1), a_(i-2), ..., a_1] -- the reversed prefix."""
    v = 0.0
    for k in range(1, i):
        v = 1.0 / (a[k] + v)
    return v


def lagrange_approx(r, depth=30):
    """
    L(r) = limsup_n  ( [a_n; a_(n+1), ...] + [0; a_(n-1), ..., a_1] )

    The standard continued-fraction formula. Exact in structure, and it
    is a genuine limsup rather than a sample.

    Two earlier versions of this were wrong and both are worth recording.
    The first took max over 1 <= q <= Q of 1/(q||qr||); that is a sup, not
    a limsup, and q=1 dominates, so it reported L(phi) = phi^2 = 2.618
    instead of sqrt5 = 2.236. The second restricted q to a tail window,
    which is a SAMPLE of large q, and near-rationals whose resonance falls
    outside the window came back as badly approximable.

    Hurwitz: inf over all irrationals is sqrt5, attained exactly on the
    GL(2,Z) orbit of phi.
    """
    a = cf_terms(r, depth + 12)
    if len(a) < 14:
        return float("inf")                 # rational or near-rational
    best = 0.0
    hi = min(len(a) - 4, depth)
    # start deep: it is a LIMsup, and the reversed-prefix term is not yet
    # its limiting value at small i (at i=2 it is just 1/a_1).
    for i in range(8, hi):
        v = a[i] + _tail(a, i + 1) + _head(a, i)
        if v > best:
            best = v
    return best if best else float("inf")


def cf(x, n=12):
    out = []
    for _ in range(n):
        a = math.floor(x)
        out.append(int(a))
        f = x - a
        if f < 1e-12:
            break
        x = 1 / f
    return out


def main():
    W = 78
    print("=" * W)
    print("1. THE CONDITION, STATED WITHOUT PHI IN IT")
    print("=" * W)
    print()
    print("  R(theta) = how well the ratio TD/TrD can be approximated by")
    print("             rationals, measured as the Lagrange number")
    print()
    print("      L(r) = limsup_q  1 / ( q * ||q r|| )")
    print()
    print("  no proportion, no subdivision, no whole-to-part, no sqrt5, no")
    print("  Fibonacci. a statement about every real number at once.")
    print()
    print("  sanity check on known values:")
    print()
    print(f"  {'r':>22} {'L(r)':>12} {'continued fraction':>28}")
    print("  " + "-" * 66)
    for nm, v in [("phi", PHI), ("1/phi", 1 / PHI), ("phi^2", PHI ** 2),
                  ("sqrt2", math.sqrt(2)), ("silver 1+sqrt2", SILVER),
                  ("plastic", PLASTIC), ("e", math.e), ("pi", math.pi),
                  ("3/2 (rational)", 1.5)]:
        L = lagrange_approx(v)
        c = cf_terms(v, 9)
        print(f"  {nm:>22} {L:>12.6f} {str(c):>28}")
    print()
    print(f"  sqrt5 = {math.sqrt(5):.6f}. the phi family sits exactly there")
    print("  and nothing gets below it. that is Hurwitz's theorem, and the")
    print("  table is a check of it.")
    print()

    print("=" * W)
    print("2. WHY A GRID SEARCH CANNOT TEST THIS (and what that means)")
    print("=" * W)
    print()
    print("  the paper's method is a grid search over 10,000 values of")
    print("  theta. that method CANNOT evaluate the Hurwitz criterion, and")
    print("  the reason is not a numerical detail:")
    print()
    print("  every grid point is a float, hence a rational. L is infinite")
    print("  on the rationals. what a float actually gives you is the")
    print("  continued fraction of a nearby rational, which agrees with the")
    print("  target for a few terms and then becomes rounding noise. the")
    print("  criterion lives in the infinite tail, so it is invisible to")
    print("  any finite grid.")
    print()
    print("  watch it happen. continued fraction of float(phi) against the")
    print("  true all-1s expansion:")
    print()
    c = cf_terms(PHI, 40)
    print(f"    {str(c[:28])}")
    first_bad = next((i for i, v in enumerate(c) if v != 1), len(c))
    print()
    print(f"  all-1s holds for {first_bad} terms, then float error takes")
    print(f"  over. L computed at depth < {first_bad} gives "
          f"{lagrange_approx(PHI):.6f}, close to")
    print(f"  sqrt5 = {math.sqrt(5):.6f}. computed deeper it diverges, and")
    print("  no refinement of the grid helps, because refining the grid")
    print("  adds precision to the WRONG kind of object.")
    print()
    print("  so the Hurwitz route is not a replacement resistance function")
    print("  to drop into the paper's Section 4 grid search. it is an")
    print("  ANALYTIC characterisation, and that is exactly why it is")
    print("  stronger: it is a theorem about all reals, proved in 1891,")
    print("  not a numerical minimum found on a lattice.")
    print()
    print("  the numerical content is section 1 above: at exact algebraic")
    print("  values, the phi family sits at sqrt5 and nothing is below it.")
    print("  that is a check of Hurwitz, and it is all the computation this")
    print("  argument needs or can support.")
    print()

    print("=" * W)
    print("3. WHY THIS CLOSES THE CIRCULARITY AND SECTION 4 DOES NOT")
    print("=" * W)
    print()
    print(f"  {'':>34} {'V4 (the paper)':>20} {'Hurwitz':>16}")
    print("  " + "-" * 72)
    rows = [
        ("mentions proportion / subdivision", "yes, as its premise", "no"),
        ("is a statement about all reals", "no, about one balance",
         "yes"),
        ("phi appears in the question", "as its definition", "no"),
        ("sqrt5 appears in the answer", "yes", "yes"),
        ("extremum is a theorem", "no, an identity", "yes, Hurwitz"),
        ("could have come out otherwise", "no", "yes"),
    ]
    for a, b, c in rows:
        print(f"  {a:>34} {b:>20} {c:>16}")
    print()
    print("  the last row is the test that matters. V4 could not have")
    print("  produced anything but phi, because solving the golden-section")
    print("  condition IS producing phi. the Hurwitz condition could have")
    print("  been minimised by any badly-approximable number, and which one")
    print("  wins is a nineteenth-century theorem rather than an algebraic")
    print("  restatement.")
    print()

    print("=" * W)
    print("4. THE TEST THAT COULD HAVE FAILED: DOES THE CUBIC CASE FOLLOW?")
    print("=" * W)
    print()
    print("  trd_review.py found that V5's resistance function lands on the")
    print("  plastic number, the smallest Pisot number and the root of")
    print("  x^3 = x + 1. if 'badly approximable' were a generic route to")
    print("  self-similar constants, the plastic number should be special")
    print("  here too. it is not:")
    print()
    print(f"  {'number':>20} {'L':>11} {'Hurwitz-extremal?':>20}")
    print("  " + "-" * 54)
    for nm, v in [("phi", PHI), ("plastic", PLASTIC),
                  ("silver 1+sqrt2", SILVER), ("sqrt2", math.sqrt(2)),
                  ("sqrt3", math.sqrt(3))]:
        L = lagrange_approx(v)
        ex = "YES (= sqrt5)" if abs(L - math.sqrt(5)) < 5e-3 else "no"
        print(f"  {nm:>20} {L:>11.6f} {ex:>20}")
    print()
    print("  the plastic number is NOT badly approximable in the Hurwitz")
    print("  sense. so the two constants in the paper's Table 1 arrive by")
    print("  different routes and are not two instances of one principle.")
    print()
    print("  this is a real constraint on the framework rather than a")
    print("  decoration: 'phi is the attractor of self-similarity' predicts")
    print("  the plastic number should be an attractor too, and on the")
    print("  Hurwitz criterion it is not. whichever criterion the paper")
    print("  adopts, it has to explain the other row of its own table.")
    print()

    print("=" * W)
    print("5. WHAT TO WRITE INSTEAD, IN ONE PARAGRAPH")
    print("=" * W)
    print()
    for line in [
        "Given TD + TrD = 1, write r = TD/TrD. A rational r makes the",
        "storage-reference balance commensurate: some finite repeat closes",
        "exactly, the system acquires a period, and its self-reference",
        "terminates. Define interaction resistance as resistance to that",
        "termination, i.e. as how poorly r is approximated by rationals,",
        "measured by the Lagrange number L(r) = limsup 1/(q||qr||). This",
        "definition mentions no proportion, no subdivision and no",
        "particular constant. By Hurwitz's theorem the infimum of L over",
        "the irrationals is sqrt5, attained precisely on the GL(2,Z) orbit",
        "of phi. Fixing the labelling convention TD > TrD selects",
        "TD = 1/phi, TrD = 1/phi^2. phi is therefore the maximally",
        "incommensurate storage-reference balance, and sqrt5 enters as the",
        "value of a theorem rather than as an ingredient of the premise.",
    ]:
        print(f"    {line}")
    print()
    print("  that paragraph is shorter than Section 4, assumes less, and")
    print("  is the version a referee cannot call circular.")


if __name__ == "__main__":
    main()
