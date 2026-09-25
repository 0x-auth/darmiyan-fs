#!/usr/bin/env python3
"""
================================================================================
PRIMES_BASES -- do primes look different in base phi, base e, or Zeckendorf?
================================================================================

THE QUESTION

  "what do primes look like in base phi or base e? and is there a
   correlation with the Fibonacci index and the value?"

Testable, so tested. For each n we compute representation statistics that
have nothing to do with divisibility, then ask whether primes differ from
non-primes on them. A real signal would be a distribution difference with a
p-value that survives the number of things being tested.

STATISTICS COMPUTED

  base phi   digit weight (count of 1s), integer-part length,
             fractional-part length
  Zeckendorf weight (number of Fibonacci terms), largest index used,
             and index/value relationship
  base e     digit sum, leading digit
  irrational rotation  {n*phi} -- the classic equidistribution test

PRE-REGISTERED EXPECTATION

  Almost certainly nothing. A change of base is a bijection computable in
  polynomial time. If a base-phi digit statistic separated primes from
  composites, it would be a polynomial-time primality-related structure
  discovered by accident, and more importantly {n*alpha} is known to be
  equidistributed over primes (Vinogradov). So the honest prediction is
  null, and the point of running it is to see the size of the null.

  Writing the expectation down first so the result cannot be re-read
  favourably afterwards.

Run:  python3 primes_bases.py
================================================================================
"""

import math
from fractions import Fraction

import mpmath as mp

mp.mp.dps = 80
PHI = (1 + mp.sqrt(5)) / 2
E = mp.e

N = 20000


def sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0] = s[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return s


# ---------------------------------------------------------------- base phi

def base_phi(n):
    """Greedy. Returns (n_ones, len_int, len_frac)."""
    x = mp.mpf(n)
    k = 0
    while PHI ** (k + 1) <= x:
        k += 1
    ones = 0
    li = k + 1
    tol = mp.mpf(10) ** -60
    for j in range(k, -1, -1):
        p = PHI ** j
        if p <= x + tol:
            ones += 1
            x -= p
    lf = 0
    for j in range(1, 90):
        if abs(x) < tol:
            break
        p = PHI ** (-j)
        if p <= x + tol:
            ones += 1
            x -= p
            lf = j
    return ones, li, lf


# -------------------------------------------------------------- Zeckendorf

FIB = [1, 2]
while FIB[-1] < 10 ** 7:
    FIB.append(FIB[-1] + FIB[-2])


def zeck(n):
    """Greedy Zeckendorf. Returns (weight, largest index, smallest index)."""
    w, hi, lo = 0, -1, -1
    i = len(FIB) - 1
    while n > 0 and i >= 0:
        if FIB[i] <= n:
            n -= FIB[i]
            w += 1
            if hi < 0:
                hi = i
            lo = i
        i -= 1
    return w, hi, lo


# ------------------------------------------------------------------ base e

def base_e(n):
    """Returns (integer-part digit sum, leading digit, int-part length)."""
    x = mp.mpf(n)
    k = 0
    while E ** (k + 1) <= x:
        k += 1
    s, lead = 0, None
    for j in range(k, -1, -1):
        p = E ** j
        d = int(mp.floor(x / p))
        d = min(d, 2)
        if lead is None:
            lead = d
        s += d
        x -= d * p
    return s, lead, k + 1


# -------------------------------------------------------------------- stats

def welch(a, b):
    na, nb = len(a), len(b)
    if na < 5 or nb < 5:
        return float("nan"), float("nan")
    ma, mb = sum(a) / na, sum(b) / nb
    va = sum((x - ma) ** 2 for x in a) / (na - 1)
    vb = sum((x - mb) ** 2 for x in b) / (nb - 1)
    se = math.sqrt(va / na + vb / nb)
    if se == 0:
        return float("nan"), float("nan")
    t = (ma - mb) / se
    # normal approximation for p, fine at these sample sizes
    p = math.erfc(abs(t) / math.sqrt(2))
    return t, p


def ks(a, b):
    # CAVEAT: KS assumes continuous distributions. Most statistics here are
    # integer valued with heavy ties, so these p-values are not trustworthy
    # and are printed only to show they disagree with Welch. The within-
    # length control in section 3 is the result that counts.
    a, b = sorted(a), sorted(b)
    na, nb = len(a), len(b)
    i = j = 0
    d = 0.0
    while i < na and j < nb:
        if a[i] <= b[j]:
            i += 1
        else:
            j += 1
        d = max(d, abs(i / na - j / nb))
    en = math.sqrt(na * nb / (na + nb))
    lam = (en + 0.12 + 0.11 / en) * d
    q = 2 * sum((-1) ** (k - 1) * math.exp(-2 * k * k * lam * lam)
                for k in range(1, 100))
    return d, min(max(q, 0.0), 1.0)


def main():
    S = sieve(N)
    print("=" * 78)
    print(f"SETUP: n = 2..{N:,}")
    print("=" * 78)
    print()
    feats = {k: ([], []) for k in
             ("phi_ones", "phi_lenint", "phi_lenfrac", "phi_density",
              "zeck_w", "zeck_hi", "zeck_span", "e_digitsum", "e_lead",
              "rot_phi")}
    for n in range(2, N + 1):
        pr = bool(S[n])
        o, li, lf = base_phi(n)
        w, hi, lo = zeck(n)
        es, el, eli = base_e(n)
        rot = float(mp.frac(mp.mpf(n) * PHI))
        vals = {
            "phi_ones": o, "phi_lenint": li, "phi_lenfrac": lf,
            "phi_density": o / (li + lf) if (li + lf) else 0,
            "zeck_w": w, "zeck_hi": hi, "zeck_span": hi - lo,
            "e_digitsum": es, "e_lead": el, "rot_phi": rot,
        }
        for k, v in vals.items():
            feats[k][0 if pr else 1].append(v)
    np_ = len(feats["phi_ones"][0])
    nc = len(feats["phi_ones"][1])
    print(f"  primes {np_:,}   non-primes {nc:,}")
    print()

    print("=" * 78)
    print("1. DOES ANY REPRESENTATION STATISTIC SEPARATE PRIMES?")
    print("=" * 78)
    print()
    print("  Bonferroni threshold for 10 tests at 0.05: p < 0.005")
    print()
    print(f"  {'statistic':>14} {'prime mean':>12} {'other mean':>12} "
          f"{'t':>9} {'p (Welch)':>12} {'p (KS)':>11} {'sig?':>6}")
    print("  " + "-" * 82)
    hits = []
    for k, (a, b) in feats.items():
        t, p = welch(a, b)
        d, pk = ks(a, b)
        sig = "YES" if (p < 0.005 or pk < 0.005) else "no"
        if sig == "YES":
            hits.append(k)
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        print(f"  {k:>14} {ma:>12.5f} {mb:>12.5f} {t:>9.3f} "
              f"{p:>12.3e} {pk:>11.3e} {sig:>6}")
    print()

    print("=" * 78)
    print("2. WHAT THE SIGNIFICANT ONES ACTUALLY ARE")
    print("=" * 78)
    print()
    if not hits:
        print("  none. the null held on every statistic.")
    for k in hits:
        a, b = feats[k]
        ma, mb = sum(a) / len(a), sum(b) / len(b)
        sd = math.sqrt(sum((x - mb) ** 2 for x in b) / (len(b) - 1))
        print(f"  {k}: prime mean {ma:.5f}, other {mb:.5f}, "
              f"difference {abs(ma-mb)/sd if sd else float('nan'):.4f} SD")
    print()
    print("  IMPORTANT: length statistics separate trivially, because")
    print("  primes thin out as n grows, so the prime set is weighted")
    print("  toward larger n and therefore longer representations. that is")
    print("  a density effect, not a representation effect. the controlled")
    print("  version is below.")
    print()

    print("=" * 78)
    print("3. CONTROLLED: WITHIN FIXED LENGTH")
    print("=" * 78)
    print()
    print("  compare primes and non-primes that have the SAME base-phi")
    print("  integer-part length, so magnitude cannot carry the effect.")
    print()
    print(f"  {'len':>5} {'n primes':>10} {'n other':>9} "
          f"{'prime weight':>14} {'other weight':>14} {'p':>11}")
    print("  " + "-" * 68)
    by = {}
    for n in range(2, N + 1):
        o, li, lf = base_phi(n)
        by.setdefault(li, ([], []))[0 if S[n] else 1].append(o)
    for li in sorted(by):
        a, b = by[li]
        if len(a) < 30 or len(b) < 30:
            continue
        t, p = welch(a, b)
        print(f"  {li:>5} {len(a):>10,} {len(b):>9,} "
              f"{sum(a)/len(a):>14.4f} {sum(b)/len(b):>14.4f} {p:>11.3e}")
    print()

    print("=" * 78)
    print("4. THE ROTATION TEST: IS {n*phi} DIFFERENT FOR PRIMES?")
    print("=" * 78)
    print()
    a, b = feats["rot_phi"]
    print(f"  {'bin':>12} {'primes %':>11} {'non-primes %':>14} {'ratio':>9}")
    print("  " + "-" * 50)
    B = 10
    for i in range(B):
        lo, hi = i / B, (i + 1) / B
        pa = sum(1 for x in a if lo <= x < hi) / len(a) * 100
        pb = sum(1 for x in b if lo <= x < hi) / len(b) * 100
        print(f"  [{lo:.1f},{hi:.1f})  {pa:>11.3f} {pb:>14.3f} "
              f"{pa/pb if pb else float('nan'):>9.4f}")
    d, pk = ks(a, b)
    print()
    print(f"  KS statistic {d:.5f}, p = {pk:.4f}")
    print()
    print("  {n*phi} is equidistributed for primes. this is a theorem")
    print("  (Vinogradov, for {p*alpha} with alpha irrational), and the")
    print("  numbers above are what a theorem looks like when you check it.")
    print()

    print("=" * 78)
    print("5. FIBONACCI INDEX AGAINST VALUE")
    print("=" * 78)
    print()
    print("  are any Fibonacci numbers prime, and does the index predict it?")
    print()
    F = [1, 1]
    while len(F) < 40:
        F.append(F[-1] + F[-2])
    def isp(m):
        if m < 2:
            return False
        if m % 2 == 0:
            return m == 2
        i = 3
        while i * i <= m:
            if m % i == 0:
                return False
            i += 2
        return True
    print(f"  {'index':>7} {'F(index)':>14} {'prime?':>8} {'index prime?':>14}")
    print("  " + "-" * 46)
    for i in range(3, 32):
        print(f"  {i:>7} {F[i-1]:>14,} {str(isp(F[i-1])):>8} "
              f"{str(isp(i)):>14}")
    print()
    print("  the pattern: F(n) prime REQUIRES n prime (except F(4) = 3),")
    print("  because F(a) divides F(ab). the converse fails: 19 is prime")
    print("  but F(19) = 4181 = 37 x 113 is not. the implication runs one")
    print("  way only.")
    print("  this is the index/value relation, and it is a divisibility")
    print("  fact about the recurrence, not a representation fact.")


if __name__ == "__main__":
    main()
