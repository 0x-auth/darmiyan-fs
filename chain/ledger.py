#!/usr/bin/env python3
"""
================================================================================
THE LEDGER: states in 4D spacetime, split into storage and reference
================================================================================

THE PROPOSAL BEING TESTED

Every event in 4D spacetime carries a state. Split that state two ways:

    TD  time domain      = position   = STORAGE (the value held)
    TrD trust domain     = momentum   = REFERENCE (what points at it)

    TrD^2 + TD^2 = 1     (established: sech^2(L/2) + tanh^2(L/2) = 1)

And index the states by integers, so that FTA's unique factorisation is the
addressing scheme: a composite is a value at a uniquely determined address,
built from orthogonal (independent) primes.

QUESTION: do primes and composites CLUSTER when laid out this way, or is the
structure uniform?

HOW THE MAPPING IS BUILT -- and this is the part to be suspicious of

Nothing forces a particular map from integer n to a state. Any choice is a
choice. So this script uses the least arbitrary one available:

    Omega(n)  = number of prime factors WITH multiplicity
    omega(n)  = number of DISTINCT primes
    mu(n)     = +1 / -1 / 0

    Lambda(n) = log(n) / Omega(n)    the average log-size per factor
                                      = "how much divergence per step"

That is not invented: log n = sum of log p over the factorisation, so
log(n)/Omega(n) is literally the mean log-prime, and Lambda has been the
per-step divergence rate throughout this work. A prime has Omega = 1, so
Lambda(p) = log p exactly -- the whole of the number in one step.

Then:
    TrD = tanh(Lambda/2)        reference density
    TD  = sech(Lambda/2)        storage rate

TESTS
 1. do primes and composites separate in the (TD, TrD) plane?
 2. is the separation real or an artifact of Lambda = log n / Omega?
 3. what does mu = 0 (non-squarefree) do -- is it a third region?
 4. NULL: random integers with matched log n but shuffled Omega
 5. does anything here connect to the Delta sectors
================================================================================
"""

import numpy as np
from collections import Counter

N = 20000


def sieve_factor(n):
    """Smallest prime factor sieve."""
    spf = np.zeros(n + 1, dtype=np.int64)
    for i in range(2, n + 1):
        if spf[i] == 0:
            for j in range(i, n + 1, i):
                if spf[j] == 0:
                    spf[j] = i
    return spf


SPF = sieve_factor(N)


def factorise(n):
    f = Counter()
    while n > 1:
        p = SPF[n]
        f[p] += 1
        n //= p
    return f


def stats(n):
    f = factorise(n)
    Om = sum(f.values())          # with multiplicity
    om = len(f)                   # distinct
    mu = 0 if any(v > 1 for v in f.values()) else (-1) ** om
    lam = np.log(n) / Om
    return Om, om, mu, lam


print("=" * 78)
print("1. THE LAYOUT")
print("=" * 78)
print()
print("  Lambda(n) = log(n)/Omega(n) = mean log-prime in the factorisation")
print("  TrD = tanh(Lambda/2)   TD = sech(Lambda/2)   TrD^2 + TD^2 = 1")
print()
print(f"  {'n':>6} {'factorisation':>18} {'Omega':>6} {'mu':>4} "
      f"{'Lambda':>9} {'TD':>9} {'TrD':>9}")
print("  " + "-" * 70)
for n in (2, 3, 4, 6, 8, 12, 15, 16, 30, 64, 97, 210, 1024, 9973):
    f = factorise(n)
    fs = "*".join(f"{p}^{v}" if v > 1 else str(p) for p, v in sorted(f.items()))
    Om, om, mu, lam = stats(n)
    print(f"  {n:>6} {fs:>18} {Om:>6} {mu:>+4} {lam:9.5f} "
          f"{1/np.cosh(lam/2):9.6f} {np.tanh(lam/2):9.6f}")
print()

# ---------------------------------------------------------- the separation

print("=" * 78)
print("2. DO PRIMES AND COMPOSITES SEPARATE?")
print("=" * 78)
print()
ns = np.arange(2, N + 1)
data = np.array([stats(int(n)) for n in ns])
Om, om, mu, lam = data[:, 0], data[:, 1], data[:, 2], data[:, 3]
TrD = np.tanh(lam / 2)
TD = 1 / np.cosh(lam / 2)
is_prime = (Om == 1)
sqfree = (mu != 0)

print(f"  {'class':>22} {'count':>7} {'mean Lambda':>12} "
      f"{'mean TrD':>10} {'sd TrD':>9} {'range TrD':>20}")
print("  " + "-" * 84)
for label, mask in (("primes", is_prime),
                    ("semiprimes p*q", (Om == 2) & (mu == 1)),
                    ("p^2", (Om == 2) & (mu == 0)),
                    ("squarefree composites", (~is_prime) & sqfree),
                    ("non-squarefree", mu == 0),
                    ("all composites", ~is_prime)):
    m = mask
    if m.sum() == 0:
        continue
    print(f"  {label:>22} {m.sum():>7} {lam[m].mean():12.5f} "
          f"{TrD[m].mean():10.6f} {TrD[m].std():9.6f} "
          f"{f'{TrD[m].min():.4f} - {TrD[m].max():.4f}':>20}")
print()
print("  primes have the highest Lambda by construction: Omega=1 means")
print("  the whole of log n is spent in one step. so they sit at high TrD")
print("  and low TD -- maximal reference, minimal storage.")
print()

# ----------------------------------------------------------- the artifact

print("=" * 78)
print("3. IS THE SEPARATION REAL, OR JUST log n / Omega?")
print("=" * 78)
print()
print("  control: compare integers in a NARROW window of n, so log n is")
print("  nearly constant. any remaining spread is due to Omega alone.")
print()
print(f"  {'window':>16} {'class':>18} {'count':>6} {'mean TrD':>10} "
      f"{'mean TD':>10}")
print("  " + "-" * 64)
for lo, hi in ((1000, 1100), (5000, 5100), (15000, 15100)):
    w = (ns >= lo) & (ns < hi)
    for label, extra in (("prime", is_prime),
                         ("Omega=2", Om == 2),
                         ("Omega=3", Om == 3),
                         ("Omega>=5", Om >= 5)):
        m = w & extra
        if m.sum() == 0:
            continue
        print(f"  {f'{lo}-{hi}':>16} {label:>18} {m.sum():>6} "
              f"{TrD[m].mean():10.6f} {TD[m].mean():10.6f}")
    print()
print("  within a narrow window log n is fixed, so Lambda = log n / Omega")
print("  is a deterministic function of Omega. the 'separation' is that")
print("  function, nothing more. it is an artifact of the chosen map.")
print()

# --------------------------------------------------------- the mu=0 check

print("=" * 78)
print("4. IS mu = 0 A THIRD REGION?")
print("=" * 78)
print()
print("  mu has three values like Delta has three sectors. do the")
print("  non-squarefree numbers occupy their own place in (TD, TrD)?")
print()
print(f"  {'mu':>5} {'count':>8} {'mean TrD':>10} {'sd':>9} "
      f"{'overlap with others':>22}")
print("  " + "-" * 58)
for v in (+1, -1, 0):
    m = (mu == v)
    others = ~m
    lo_, hi_ = TrD[m].min(), TrD[m].max()
    ov = ((TrD[others] >= lo_) & (TrD[others] <= hi_)).mean()
    print(f"  {v:>+5} {m.sum():>8} {TrD[m].mean():10.6f} "
          f"{TrD[m].std():9.6f} {ov:22.4f}")
print()
print("  overlap = fraction of the OTHER classes falling inside this")
print("  class's TrD range. near 1.0 means no separation at all.")
print()

# ------------------------------------------------------------- the null

print("=" * 78)
print("5. NULL: shuffle Omega, keep log n")
print("=" * 78)
print()
rng = np.random.default_rng(3)
Om_shuf = rng.permutation(Om)
lam_null = np.log(ns) / np.maximum(Om_shuf, 1)
TrD_null = np.tanh(lam_null / 2)
print(f"  {'':>18} {'real spread':>13} {'shuffled spread':>17}")
print("  " + "-" * 52)
print(f"  {'sd of TrD':>18} {TrD.std():13.6f} {TrD_null.std():17.6f}")
print(f"  {'mean TrD':>18} {TrD.mean():13.6f} {TrD_null.mean():17.6f}")
print()
print("  if shuffling Omega leaves the distribution essentially")
print("  unchanged, the structure is in the FORMULA, not in the")
print("  arithmetic.")
print()

print("=" * 78)
print("6. VERDICT")
print("=" * 78)
print()
print("  WHAT IS TRUE")
print("    the rotation TrD^2 + TD^2 = 1 holds exactly, for any Lambda.")
print("    a prime has Omega = 1, so Lambda(p) = log p: the whole")
print("    number in a single step. maximal reference, minimal storage.")
print("    that reading is coherent.")
print()
print("    unique factorisation IS an addressing scheme with no slack.")
print("    that part needs no simulation -- it is FTA.")
print()
print("  WHAT IS NOT ESTABLISHED")
print("    no clustering beyond what Lambda = log n / Omega puts in by")
print("    hand. within a fixed window the map is a deterministic")
print("    function of Omega, so 'primes cluster' restates 'primes have")
print("    Omega = 1'.")
print()
print("    mu = 0 does not occupy a distinct region. the three values of")
print("    mu do not map onto the three Delta sectors -- they overlap")
print("    almost completely in TrD.")
print()
print("    and the map from n to a state was CHOSEN. nothing in 4D")
print("    spacetime says an event is indexed by an integer, or that its")
print("    momentum is tanh of a mean log-prime. until something forces")
print("    that map, this is a labelling, not a physics.")
