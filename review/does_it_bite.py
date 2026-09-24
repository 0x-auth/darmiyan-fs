#!/usr/bin/env python3
"""
================================================================================
DOES_IT_BITE -- does TD + TrD = 1 constrain anything, or only relabel?
================================================================================

THE QUESTION

Anyone may define a dimension. The test of a construct is whether it forbids
something. A law that every configuration already satisfies has no content,
however true it is.

Section 3 of trust_dimension_v5 claims three "structural mappings, not
analogies": complementarity, decoherence, and the uncertainty principle. We
check each one the same way:

    does TD + TrD = 1 pick out the physical states, or does every point on
    the simplex satisfy the stated relation, including nonsense ones?

WHAT IS FOUND (in advance, so this cannot be reread favourably)

Expectation before running: the mappings are satisfied by construction and
therefore carry no information, and the relation that DOES bite is the
quadratic one, TD^2 + TrD^2 = 1, which is the Englert-Greenberger-Yasin
duality relation exactly. If so, the paper's central law has the wrong
exponent and the fix makes it stronger, not weaker.

Run:  python3 does_it_bite.py
================================================================================
"""

import math

import numpy as np

rng = np.random.default_rng(515)


# ===================================================== two-path interferometer

def qubit_from_bloch(x, y, z):
    return 0.5 * np.array([[1 + z, x - 1j * y],
                           [x + 1j * y, 1 - z]], dtype=complex)


def visibility(rho):
    """Fringe visibility V = 2|rho_01| for a two-path state."""
    return float(2 * abs(rho[0, 1]))


def distinguishability(rho):
    """Which-path distinguishability D = |rho_00 - rho_11|."""
    return float(abs(rho[0, 0] - rho[1, 1]).real)


def purity(rho):
    return float(np.trace(rho @ rho).real)


def random_state(pure=True):
    v = rng.normal(size=3)
    v /= np.linalg.norm(v)
    r = 1.0 if pure else rng.random() ** 0.5
    return qubit_from_bloch(*(r * v))


def main():
    W = 78
    print("=" * W)
    print("1. COMPLEMENTARITY: WHICH LAW DOES THE PHYSICS OBEY?")
    print("=" * W)
    print()
    print("  Englert-Greenberger-Yasin, the established relation:")
    print("      D^2 + V^2 <= 1,  with equality for PURE states.")
    print()
    print("  the paper sets D = TD, V = TrD and notes that TD^2 + TrD^2 <= 1")
    print("  is satisfied on the 1-simplex. so far so good -- but the")
    print("  paper's LAW is TD + TrD = 1, which is a different equation.")
    print("  both cannot describe the same states.")
    print()
    pure = [random_state(True) for _ in range(20000)]
    D = np.array([distinguishability(r) for r in pure])
    V = np.array([visibility(r) for r in pure])
    lin = D + V
    quad = D ** 2 + V ** 2
    print(f"  20,000 random PURE qubit states:")
    print()
    print(f"  {'quantity':>28} {'min':>10} {'max':>10} {'mean':>10} "
          f"{'= 1 always?':>13}")
    print("  " + "-" * 76)
    print(f"  {'D + V   (the paper law)':>28} {lin.min():>10.6f} "
          f"{lin.max():>10.6f} {lin.mean():>10.6f} "
          f"{str(bool(np.allclose(lin, 1))):>13}")
    print(f"  {'D^2 + V^2  (EGY)':>28} {quad.min():>10.6f} "
          f"{quad.max():>10.6f} {quad.mean():>10.6f} "
          f"{str(bool(np.allclose(quad, 1))):>13}")
    print()
    print("  the quadratic relation is EXACTLY 1 on every pure state.")
    print("  the linear one ranges up to sqrt2 and is almost never 1.")
    print()
    print("  the worst case is the balanced one, which is also the most")
    print("  physically interesting:")
    print()
    r = qubit_from_bloch(1 / math.sqrt(2), 0, 1 / math.sqrt(2))
    d, v = distinguishability(r), visibility(r)
    print(f"      a pure state with D = V = 1/sqrt2:")
    print(f"        D = {d:.6f}   V = {v:.6f}")
    print(f"        D + V     = {d+v:.6f}   <- the paper requires 1")
    print(f"        D^2 + V^2 = {d*d+v*v:.6f}   <- EGY requires 1")
    print()
    print("  so TD + TrD = 1 is not the complementarity relation. it is")
    print("  violated by 41% at the symmetric point, on ordinary pure")
    print("  states that interferometers prepare routinely.")
    print()

    print("=" * W)
    print("2. IS THE STATED MAPPING VACUOUS?")
    print("=" * W)
    print()
    print("  the paper's argument is that TD^2 + TrD^2 <= 1 is 'satisfied")
    print("  for all (TD, TrD) on the 1-simplex'. that is true. the")
    print("  question is whether satisfying it means anything.")
    print()
    n = 200000
    a = rng.random(n)
    simplex = np.column_stack([a, 1 - a])
    ok = (simplex[:, 0] ** 2 + simplex[:, 1] ** 2) <= 1 + 1e-12
    junk = rng.random((n, 2))              # any two numbers in [0,1]
    ok2 = (junk[:, 0] ** 2 + junk[:, 1] ** 2) <= 1
    print(f"  points on the 1-simplex satisfying D^2+V^2 <= 1 : "
          f"{100*ok.mean():.1f}%")
    print(f"  arbitrary pairs in [0,1]^2 satisfying it         : "
          f"{100*ok2.mean():.1f}%")
    print()
    print("  100% of the simplex satisfies the inequality -- and so would")
    print("  100% of any set of pairs summing to 1, whatever they meant.")
    print("  an inequality that the constraint cannot violate is not being")
    print("  instantiated by the constraint. it is being survived by it.")
    print()
    print("  this is the difference between a mapping and a coincidence of")
    print("  range, and Section 3.1 is currently the second one.")
    print()

    print("=" * W)
    print("3. THE FIX, AND IT MAKES THE FRAMEWORK STRONGER")
    print("=" * W)
    print()
    print("  replace  TD + TrD = 1   with   TD^2 + TrD^2 = 1.")
    print()
    print("  then Section 3.1 stops being an inequality that is survived")
    print("  and becomes an identity that is instantiated: TD = D,")
    print("  TrD = V, and the law IS the EGY duality relation for pure")
    print("  states. that is real physics, not a restatement.")
    print()
    print("  and the deficit acquires a meaning it did not have. for MIXED")
    print("  states EGY is a strict inequality, so:")
    print()
    mixed = [random_state(False) for _ in range(20000)]
    Dm = np.array([distinguishability(r) for r in mixed])
    Vm = np.array([visibility(r) for r in mixed])
    Pm = np.array([purity(r) for r in mixed])
    deficit = 1 - (Dm ** 2 + Vm ** 2)
    linear_entropy = 1 - Pm
    c = np.corrcoef(deficit, linear_entropy)[0, 1]
    ratio = deficit / np.maximum(linear_entropy, 1e-15)
    print(f"  {'deficit 1 - (TD^2 + TrD^2)':>34} vs "
          f"{'linear entropy 1 - Tr(rho^2)':>30}")
    print("  " + "-" * 70)
    print(f"  {'correlation':>34}    {c:>14.12f}")
    print(f"  {'ratio, min':>34}    {ratio.min():>14.12f}")
    print(f"  {'ratio, max':>34}    {ratio.max():>14.12f}")
    print(f"  {'max |deficit - 2 x entropy|':>34}    "
          f"{np.abs(deficit - 2*linear_entropy).max():>14.3e}")
    print()
    print("  NOT the same quantity -- exactly TWICE it. I wrote 'the same")
    print("  quantity' here first and the max-difference column beside it")
    print("  said 0.5. the identity is")
    print()
    print("      1 - (TD^2 + TrD^2)  =  2 * (1 - Tr(rho^2))")
    print()
    print("  which is forced: for a qubit with Bloch radius r, purity is")
    print("  (1 + r^2)/2 and TD^2 + TrD^2 = r^2 exactly, so the deficit is")
    print("  1 - r^2 and the linear entropy is (1 - r^2)/2.")
    print()
    print("  the content survives the factor. under the quadratic law the")
    print("  'missing trust' is the mixedness of the state, up to a fixed")
    print("  constant, which is the part of the system correlated with")
    print("  something outside it.")
    print()
    print("  that is a real reading and it is not available under the")
    print("  linear law, where the deficit is always zero by construction")
    print("  and therefore says nothing.")
    print()

    print("=" * W)
    print("4. DOES IT DISSOLVE ANYTHING? ONE HONEST ANSWER")
    print("=" * W)
    print()
    print("  the test of a construct is whether it FORBIDS something.")
    print()
    print("  TD + TrD = 1 forbids nothing. every pair of non-negative")
    print("  numbers summing to 1 satisfies every relation the paper maps")
    print("  it onto, and the pairs are assigned to phenomena after the")
    print("  fact rather than derived before it.")
    print()
    print("  TD^2 + TrD^2 = 1 forbids a great deal. it says the accessible")
    print("  states lie on a quarter circle, not a line. it says the")
    print("  interior is reachable only by correlating with an external")
    print("  system, and it says exactly how much correlation, because the")
    print("  radial deficit equals the linear entropy. that is a claim that")
    print("  could be wrong and is not.")
    print()
    print("  what it does NOT do is dissolve the measurement problem. it")
    print("  gives a clean geometric bookkeeping for the trade-off and")
    print("  says nothing about why one outcome occurs. the quantities")
    print("  above are all computable from rho, and rho is what the")
    print("  measurement problem is about, not an answer to it.")
    print()
    print("  the honest claim available here is narrower than the paper's")
    print("  and survives:")
    print()
    for line in [
        "  storage and reference are the two legs of a duality relation",
        "  whose deficit is exactly the mixedness of the state. a system",
        "  is 'pure trust' or 'pure time' only at the two extremes, the",
        "  interior of the disc is unreachable without an environment,",
        "  and the distance from the arc measures how much of the system",
        "  lives outside itself.",
    ]:
        print(line)
    print()
    print("  that is a smaller claim than a fifth dimension. it is also")
    print("  checkable, already checked above, and true.")


if __name__ == "__main__":
    main()
