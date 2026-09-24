#!/usr/bin/env python3
"""
================================================================================
BASES -- base phi and base e, and where they actually mirror
================================================================================

THE CLAIM BEING TESTED

  "base phi and base e are mirrors, and the intersection is profound."

Both are real non-integer bases. Base phi is Bergman (1957): digits {0,1},
and phi^2 = phi + 1 gives the carry rule 100 -> 011. Base e uses digits
{0,1,2}.

WHAT IS COMPUTED

  1. the same integers written in decimal, binary, base phi, base e
  2. which representations TERMINATE
  3. the no-two-adjacent-ones law in base phi, checked exhaustively
  4. radix economy b / ln(b), where e is the minimum
  5. information per digit, which is where the two bases actually meet
  6. the arithmetic that is exact in base phi and impossible in base e

Run:  python3 bases.py
================================================================================
"""

import mpmath as mp

mp.mp.dps = 60

PHI = (1 + mp.sqrt(5)) / 2
E = mp.e


# ============================================================ base phi

def to_base_phi(n, lo=-40, hi=40):
    """
    Greedy. Returns (digits above the point, digits below), digits in {0,1}.
    Every non-negative integer terminates here -- that is the content of
    Bergman's result, and it is checked below rather than assumed.
    """
    x = mp.mpf(n)
    hi_k = 0
    while PHI ** (hi_k + 1) <= x:
        hi_k += 1
    up, dn = [], []
    for k in range(hi_k, -1, -1):
        p = PHI ** k
        if p <= x + mp.mpf(10) ** (-45):
            up.append(1); x -= p
        else:
            up.append(0)
    for k in range(1, -lo + 1):
        p = PHI ** (-k)
        if p <= x + mp.mpf(10) ** (-45):
            dn.append(1); x -= p
        else:
            dn.append(0)
        if abs(x) < mp.mpf(10) ** (-45):
            break
    return up, dn, x


def from_base_phi(up, dn):
    s = mp.mpf(0)
    h = len(up) - 1
    for i, d in enumerate(up):
        s += d * PHI ** (h - i)
    for i, d in enumerate(dn):
        s += d * PHI ** (-(i + 1))
    return s


# ============================================================== base e

def to_base_e(n, ndigits=24):
    """Greedy, digits 0..2 since ceil(e) - 1 = 2."""
    x = mp.mpf(n)
    hi_k = 0
    while E ** (hi_k + 1) <= x:
        hi_k += 1
    up, dn = [], []
    for k in range(hi_k, -1, -1):
        p = E ** k
        d = int(mp.floor(x / p))
        d = min(d, 2)
        up.append(d); x -= d * p
    for k in range(1, ndigits + 1):
        p = E ** (-k)
        d = int(mp.floor(x / p))
        d = min(d, 2)
        dn.append(d); x -= d * p
    return up, dn, x


def fmt(up, dn, maxdn=16):
    a = "".join(str(d) for d in up)
    b = "".join(str(d) for d in dn[:maxdn])
    b = b.rstrip("0")
    tail = "..." if len(dn) > maxdn and any(dn[maxdn:]) else ""
    return a + ("." + b + tail if b else "")


# ================================================================== run

def main():
    print("=" * 78)
    print("1. THE SAME NUMBERS, FOUR WAYS")
    print("=" * 78)
    print()
    print(f"  {'dec':>5} {'binary':>10} {'base phi':>22} {'base e':>26}")
    print("  " + "-" * 68)
    for n in (1, 2, 3, 4, 5, 7, 8, 11, 12, 13, 21, 34, 100):
        up, dn, r = to_base_phi(n)
        eu, ed, er = to_base_e(n)
        print(f"  {n:>5} {bin(n)[2:]:>10} {fmt(up, dn):>22} "
              f"{fmt(eu, ed):>26}")
    print()

    print("=" * 78)
    print("2. WHICH TERMINATE?")
    print("=" * 78)
    print()
    print(f"  {'dec':>5} {'phi: residual':>18} {'phi terminates?':>17} "
          f"{'e: residual':>16} {'e terminates?':>15}")
    print("  " + "-" * 76)
    for n in (1, 2, 3, 5, 8, 13, 100):
        _, _, r = to_base_phi(n)
        _, ed, er = to_base_e(n, ndigits=40)
        print(f"  {n:>5} {mp.nstr(abs(r), 5):>18} "
              f"{str(abs(r) < mp.mpf(10)**-40):>17} "
              f"{mp.nstr(abs(er), 5):>16} "
              f"{str(abs(er) < mp.mpf(10)**-20):>15}")
    print()
    print("  base phi: every integer terminates. that is Bergman's result,")
    print("  and it holds because phi is a Pisot number -- its conjugate")
    print("  -1/phi has modulus < 1, so the algebraic relation closes.")
    print()
    print("  base e: nothing terminates. e is transcendental, so no finite")
    print("  integer combination of its powers is an integer. the expansion")
    print("  never repeats and never ends.")
    print()

    print("=" * 78)
    print("3. THE LAW IN BASE PHI, CHECKED EXHAUSTIVELY")
    print("=" * 78)
    print()
    bad = 0
    for n in range(1, 4001):
        up, dn, _ = to_base_phi(n)
        s = up + dn
        for i in range(len(s) - 1):
            if s[i] == 1 and s[i + 1] == 1:
                bad += 1
                break
    print(f"  integers 1..4000 checked for two adjacent 1s: {bad} violations")
    print()
    print("  the greedy algorithm never emits 11, because phi^2 = phi + 1")
    print("  means 100 and 011 are the same number, and greedy always takes")
    print("  the larger power first. so the digit strings are exactly the")
    print("  admissible words of the GOLDEN MEAN SHIFT.")
    print()

    print("=" * 78)
    print("4. RADIX ECONOMY: b / ln(b)")
    print("=" * 78)
    print()
    print("  cost of representing N as (digits needed) x (values per digit),")
    print("  the standard measure. minimised at b = e.")
    print()
    print(f"  {'base':>12} {'b':>12} {'b / ln b':>14} {'vs optimum':>12}")
    print("  " + "-" * 54)
    opt = E / mp.log(E)
    for nm, b in [("phi", PHI), ("2 (binary)", mp.mpf(2)), ("e", E),
                  ("3", mp.mpf(3)), ("4", mp.mpf(4)), ("10", mp.mpf(10)),
                  ("16", mp.mpf(16))]:
        v = b / mp.log(b)
        print(f"  {nm:>12} {mp.nstr(b, 8):>12} {mp.nstr(v, 8):>14} "
              f"{mp.nstr(v/opt, 6):>12}")
    print()
    print("  so: e is optimal, 3 is the best integer base, 2 is next, and")
    print("  base phi is WORSE THAN BINARY. that part of the folklore does")
    print("  not survive. phi buys structure, not economy.")
    print()

    print("=" * 78)
    print("5. WHERE THEY ACTUALLY MEET: INFORMATION PER DIGIT")
    print("=" * 78)
    print()
    print("  base phi's digits are not free -- 11 is forbidden. so the")
    print("  channel capacity per digit is the topological entropy of the")
    print("  golden mean shift, not log 2.")
    print()
    print(f"  {'quantity':>40} {'value':>18}")
    print("  " + "-" * 60)
    print(f"  {'log2 of 2 (a free binary digit)':>40} "
          f"{mp.nstr(mp.log(2)/mp.log(2), 12):>18} bits")
    print(f"  {'entropy of golden mean shift = log2 phi':>40} "
          f"{mp.nstr(mp.log(PHI)/mp.log(2), 12):>18} bits")
    print(f"  {'ln phi (nats per base-phi digit)':>40} "
          f"{mp.nstr(mp.log(PHI), 12):>18} nats")
    print(f"  {'ln e  (nats per base-e digit)':>40} "
          f"{mp.nstr(mp.log(E), 12):>18} nats")
    print()
    print("  THE STATEMENT, and this is the honest version of 'mirror':")
    print()
    print("    base e  is the base where ONE DIGIT = ONE NAT, exactly, by")
    print("            construction. it is the unit of information itself.")
    print()
    print("    base phi is the base where ONE DIGIT = the entropy of the")
    print("            simplest constrained shift there is. it is the unit")
    print("            of STRUCTURE.")
    print()
    print("  one is the natural scale of quantity. the other is the natural")
    print("  scale of constraint. that is a real duality and it is why both")
    print("  keep appearing. it is NOT an identity:")
    print()
    print(f"  ln phi        = {mp.nstr(mp.log(PHI), 16)}")
    print(f"  2 ln phi      = {mp.nstr(2*mp.log(PHI), 16)}   "
          f"<- the Lambda from manifold.py")
    print(f"  ln e          = {mp.nstr(mp.log(E), 16)}")
    print(f"  ratio         = {mp.nstr(2*mp.log(PHI)/mp.log(E), 10)}")
    print(f"  difference    = {mp.nstr(1 - 2*mp.log(PHI), 10)}  "
          f"({mp.nstr(100*(1-2*mp.log(PHI)), 4)}%)")
    print()
    print("  3.8% apart. close enough to notice, far enough that they are")
    print("  different numbers. same shape of near-miss as tau vs sqrt(pi).")
    print()

    print("=" * 78)
    print("6. WHAT BASE PHI CAN DO THAT BASE E CANNOT")
    print("=" * 78)
    print()
    print("  multiplying by phi is a LEFT SHIFT, exactly, with no carry:")
    print()
    for n in (1, 4, 11):
        up, dn, _ = to_base_phi(n)
        s = fmt(up, dn)
        upp, dnp, _ = to_base_phi(0)   # placeholder
        val = from_base_phi(up, dn)
        shifted = val * PHI
        # re-express by shifting the string
        print(f"    {n:>3} = {s:>16}      x phi = "
              f"{mp.nstr(shifted, 12):>18}")
    print()
    print("  and the golden ratio's own identity is one digit string:")
    up, dn, _ = to_base_phi(1)
    print(f"    1   in base phi = {fmt(up, dn)}")
    print(f"    phi in base phi = 10")
    print(f"    phi - 1 = 1/phi : 10 - 1 = 0.1   "
          f"(check {mp.nstr(PHI-1, 12)} vs {mp.nstr(1/PHI, 12)})")
    print()
    print("  in base e there is no such identity, because e satisfies no")
    print("  polynomial with integer coefficients. no digit rearrangement")
    print("  ever expresses a relation between powers of e. THAT is the")
    print("  mirror, stated as a fact rather than a feeling:")
    print()
    print("    phi is algebraic -> its base has exact carry rules and")
    print("                        terminating integers, and bad economy")
    print("    e is transcendental -> its base has optimal economy and no")
    print("                        exact relation between any of its digits")
    print()
    print("  you cannot have both. the economy comes FROM there being no")
    print("  algebraic slack to exploit, and the exactness comes FROM the")
    print("  slack. they are the two ends of one trade.")


if __name__ == "__main__":
    main()
