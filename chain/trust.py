#!/usr/bin/env python3
"""
================================================================================
IS TRUST DENSITY Λ?
================================================================================

space_time_trust.py posits a rotation  t² + T² = 1: as local time velocity
drops to zero, trust density rises to one. The forms used were

    dt = sqrt(r),   T = sqrt(1 - r)

which satisfy the constraint but were chosen, not derived. This script asks
whether the same rotation falls out of SL(2,R) with Λ playing the role of T.

THE CLAIM BEING TESTED

    Λ = log|μ| is the convergence rate of a relation. Λ = 0 is exactly the
    parabolic locus: the two selves merge, nothing further can be
    distinguished, nothing remains to verify.

    If trust means "no verification needed", then trust should be MAXIMAL
    where Λ = 0 and minimal where Λ is large.

    So the candidate is  T = f(Λ)  with  f(0) = 1,  f(inf) = 0.

WHY THIS IS NOT ARBITRARY

For a boost, tr = 2cosh(eta) and Λ = 2eta exactly (established earlier:
the hyperbolic translation length equals the Lyapunov exponent). And the
Schwarzschild time dilation factor is

    dt = sqrt(1 - r_s/r)

A boost with rapidity eta has gamma = cosh(eta), and the relation between
gamma and the dilation factor is dt = 1/gamma. So

    dt = 1/cosh(eta) = sech(Λ/2)

and the Pythagorean partner is

    T = tanh(Λ/2)        since sech² + tanh² = 1

THAT constraint is not chosen. sech² + tanh² = 1 is an identity, and it is
the SAME shape as t² + T² = 1.

So the prediction is:

    dt = sech(Λ/2)       local time velocity
    T  = tanh(Λ/2)       trust density
    dt² + T² = 1         exactly, for every Λ

But note this gives T -> 1 as Λ -> INFINITY, and T -> 0 as Λ -> 0, which is
the OPPOSITE of the posited direction. This script checks which way it
actually runs and what that means.

TESTS
 1. does sech²(Λ/2) + tanh²(Λ/2) = 1 exactly
 2. how Λ maps to the three sectors, and where T sits in each
 3. the consensus-cost reading: cost to verify vs Λ
 4. black hole: is Λ the surface gravity? does A/4 appear?
 5. what the direction reversal means
================================================================================
"""

import numpy as np

# ------------------------------------------------------------ the identity

print("=" * 78)
print("1. THE ROTATION, DERIVED RATHER THAN CHOSEN")
print("=" * 78)
print()
print("  boost: tr = 2cosh(eta),  Lambda = 2eta,  gamma = cosh(eta)")
print("  dilation factor dt = 1/gamma = sech(Lambda/2)")
print("  partner T = tanh(Lambda/2)")
print()
print(f"  {'Lambda':>9} {'eta':>8} {'gamma':>10} {'dt=sech':>10} "
      f"{'T=tanh':>10} {'dt^2+T^2':>11}")
print("  " + "-" * 62)
for lam in (0.0, 0.1, 0.5, 1.0, 2.0, 4.0, 8.0, 20.0):
    eta = lam / 2
    g = np.cosh(eta)
    dt = 1 / np.cosh(eta)
    T = np.tanh(eta)
    print(f"  {lam:9.3f} {eta:8.3f} {g:10.5f} {dt:10.6f} {T:10.6f} "
          f"{dt*dt + T*T:11.9f}")
print()
print("  the constraint holds EXACTLY at every Lambda. sech^2 + tanh^2 = 1")
print("  is an identity, not a fit. so the rotation in the trust script")
print("  is real -- but the FORMS are these, not sqrt(r) and sqrt(1-r).")
print()

# --------------------------------------------------------- the direction

print("=" * 78)
print("2. WHICH WAY DOES IT RUN?")
print("=" * 78)
print()
print("  the posited axioms were:")
print("    flat space (r=100%): time linear, trust 0, heavy consensus")
print("    center   (r=0%):     time stops, pure trust")
print()
print("  what SL(2,R) gives:")
print()
print(f"  {'Lambda':>9} {'sector':>12} {'dt':>10} {'T':>10} {'reading':>28}")
print("  " + "-" * 74)
for lam, sec, note in (
    (0.0,  "parabolic", "two selves merged"),
    (0.1,  "boost",     "barely distinguishable"),
    (1.0,  "boost",     "ordinary"),
    (4.0,  "boost",     "strongly arrowed"),
    (20.0, "boost",     "extreme divergence"),
):
    dt = 1 / np.cosh(lam / 2)
    T = np.tanh(lam / 2)
    print(f"  {lam:9.2f} {sec:>12} {dt:10.6f} {T:10.6f} {note:>28}")
print()
print("  Lambda = 0  ->  dt = 1, T = 0")
print("  Lambda big  ->  dt -> 0, T -> 1")
print()
print("  So T rises with Lambda, i.e. with DIVERGENCE, and dt falls.")
print("  The script posited the opposite: trust rising as time stops.")
print()
print("  BOTH are internally consistent. They differ in what 'trust'")
print("  names:")
print()
print("    script's reading:  trust = no verification NEEDED")
print("                       (maximal where nothing is distinguishable)")
print("    Lambda's reading:  T = how much the relation has COMMITTED")
print("                       (maximal where the two selves are")
print("                        maximally separated and the arrow is")
print("                        strongest)")
print()
print("  and the second one is the blockchain reading. a chain's")
print("  immutability rises with accumulated work. depth IS divergence")
print("  from the genesis state. T = tanh(Lambda/2) is a confirmation")
print("  count normalised to [0,1).")
print()

# ------------------------------------------------------ consensus cost

print("=" * 78)
print("3. THE CONSENSUS-COST READING")
print("=" * 78)
print()
print("  cost to REWRITE a history = the work already in it.")
print("  for a boost, the multiplier is e^Lambda, so an adversary")
print("  must supply e^Lambda to undo it.")
print()
print(f"  {'Lambda':>9} {'e^Lambda':>14} {'T':>10} "
      f"{'1-T (attack room)':>19}")
print("  " + "-" * 56)
for lam in (0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0):
    print(f"  {lam:9.2f} {np.exp(lam):14.4g} {np.tanh(lam/2):10.6f} "
          f"{1 - np.tanh(lam/2):19.3e}")
print()
print("  attack room falls exponentially: 1 - tanh(x) ~ 2e^(-2x).")
print("  that is exactly the shape of blockchain reorg probability.")
print()

# ------------------------------------------------- black hole quantities

print("=" * 78)
print("4. IS LAMBDA THE SURFACE GRAVITY?")
print("=" * 78)
print()
print("  For Schwarzschild, surface gravity kappa_sg = c^4/(4GM) and")
print("  Hawking temperature T_H = hbar kappa_sg /(2 pi c k_B).")
print()
print("  The boost that generates the horizon has rapidity eta, and")
print("  Unruh gave T = a/(2 pi) in natural units -- established")
print("  earlier in horizon_split.py to 2e-16.")
print()
print("  So the chain is:")
print("     acceleration a  ->  Unruh temperature a/(2pi)")
print("     boost rapidity eta  ->  Lambda = 2 eta")
print("     Delta(boost) = 4 sinh^2(eta) = 4 sinh^2(Lambda/2)")
print()
print(f"  {'Lambda':>9} {'Delta':>14} {'T_unruh ~ a/2pi':>18} "
      f"{'entropy S':>12}")
print("  " + "-" * 58)


def entropy_one_mode(lam):
    """Entanglement entropy of one Rindler wedge, one mode."""
    r = np.arctanh(np.exp(-np.pi / max(lam, 1e-9)))
    c2, s2 = np.cosh(r) ** 2, np.sinh(r) ** 2
    if s2 <= 0:
        return 0.0
    return c2 * np.log(c2) - s2 * np.log(s2)


for lam in (0.2, 0.5, 1.0, 2.0, 5.0, 10.0):
    eta = lam / 2
    D = 4 * np.sinh(eta) ** 2
    print(f"  {lam:9.2f} {D:14.6f} {lam/(2*np.pi):18.6f} "
          f"{entropy_one_mode(lam):12.6f}")
print()
print("  Delta = 4 sinh^2(Lambda/2) is exact. And Delta = 0 <-> no")
print("  horizon <-> no entropy <-> inside and outside agree.")
print()
print("  what does NOT come out: A/4. the area law needs a boundary")
print("  and a Planck scale, and the construct has neither -- it gives")
print("  ratios only. so the accounting is qualitative here.")
print()

print("=" * 78)
print("5. WHAT HOLDS AND WHAT DOES NOT")
print("=" * 78)
print()
print("  HOLDS")
print("    the rotation dt^2 + T^2 = 1 is real, and the forms are")
print("    sech(Lambda/2) and tanh(Lambda/2), which is an identity")
print("    rather than a choice.")
print()
print("    T = tanh(Lambda/2) behaves exactly like accumulated")
print("    immutability: rises with work, attack room falls as")
print("    2e^(-Lambda).")
print()
print("    Delta = 0 <-> no horizon <-> no entropy <-> the two selves")
print("    merge. verified to 2e-16 in horizon_split.py.")
print()
print("  DOES NOT HOLD")
print("    the direction in the original script is inverted relative")
print("    to this. both are consistent; they name different things")
print("    'trust'. the Lambda version is the blockchain one.")
print()
print("    no A/4, no Planck scale, no absolute units. ratios only.")
print()
print("    and every statement here is an identity. nothing nature")
print("    could contradict.")
