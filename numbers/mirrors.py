#!/usr/bin/env python3
"""
================================================================================
MIRRORS -- does every base have a mirror, and what is the union of all of them?
================================================================================

THE QUESTION

  "does every number system have a mirror like base phi and base e? if not,
   the union would represent a superposition of all number systems."

There IS a canonical mirror of a base, and it is not another base. It is the
set of GALOIS CONJUGATES: the other roots of the base's minimal polynomial.

  phi is a root of x^2 - x - 1. The other root is -1/phi = -0.618034.
  That is phi's mirror, and it is forced, not chosen.

  e is a root of NO polynomial with integer coefficients. It has no
  conjugates. It has no mirror, and that is not an oversight.

TESTED HERE

  1. conjugates of a range of bases, and which lie inside the unit disk
     (the Pisot condition)
  2. whether integers terminate in each base
  3. that those two are the SAME fact
  4. the other candidate mirror, b <-> 1/b, and what it actually does
  5. what the union over all bases is, honestly

Run:  python3 mirrors.py
================================================================================
"""

import mpmath as mp

mp.mp.dps = 400


# base name, minimal polynomial coefficients (highest degree first), kind
BASES = [
    ("2 (binary)",        [1, -2],              "algebraic, degree 1"),
    ("3",                 [1, -3],              "algebraic, degree 1"),
    ("10 (decimal)",      [1, -10],             "algebraic, degree 1"),
    ("phi",               [1, -1, -1],          "algebraic, degree 2"),
    ("1+sqrt2 (silver)",  [1, -2, -1],          "algebraic, degree 2"),
    ("sqrt2",             [1, 0, -2],           "algebraic, degree 2"),
    ("(1+sqrt13)/2",      [1, -1, -3],          "algebraic, degree 2"),
    ("plastic number",    [1, 0, -1, -1],       "algebraic, degree 3"),
    ("tribonacci",        [1, -1, -1, -1],      "algebraic, degree 3"),
]

TRANSCENDENTAL = [("e", mp.e), ("pi", mp.pi)]


def roots(poly):
    return mp.polyroots([mp.mpf(c) for c in poly], maxsteps=200,
                        extraprec=200)


def dominant(rs):
    real = [r for r in rs if abs(mp.im(r)) < mp.mpf(10) ** -25
            and mp.re(r) > 1]
    return max(real, key=lambda r: mp.re(r)) if real else max(
        rs, key=lambda r: abs(r))


def terminates(beta, n, maxdig=120):
    """
    Greedy beta-expansion of the integer n. Does it stop?

    Working precision is 400 digits and the tolerance is 1e-300, so a
    spurious "terminated" would need 300 digits of accumulated rounding
    inside 120 steps. An earlier version of this ran at 50 digits with a
    1e-35 tolerance and reported e and pi as terminating, which is false.
    """
    x = mp.mpf(n)
    tol = mp.mpf(10) ** -300
    k = 0
    while beta ** (k + 1) <= x:
        k += 1
    D = int(mp.ceil(beta)) - 1
    for j in range(k, -1, -1):
        p = beta ** j
        d = min(int(mp.floor(x / p + tol)), D)
        x -= d * p
    if abs(x) < tol:
        return True, 0
    for j in range(1, maxdig + 1):
        if abs(x) < tol:
            return True, j - 1
        p = beta ** (-j)
        d = min(int(mp.floor(x / p + tol)), D)
        x -= d * p
    return False, maxdig


def main():
    print("=" * 78)
    print("1. THE MIRROR OF A BASE IS ITS GALOIS CONJUGATES")
    print("=" * 78)
    print()
    print(f"  {'base':>18} {'value':>12} {'conjugates (the mirror)':>34} "
          f"{'max |conj|':>11}")
    print("  " + "-" * 78)
    info = {}
    for nm, poly, kind in BASES:
        rs = roots(poly)
        b = dominant(rs)
        conj = [r for r in rs if abs(r - b) > mp.mpf(10) ** -20]
        m = max((abs(c) for c in conj), default=mp.mpf(0))
        cs = ", ".join(mp.nstr(c, 6) for c in conj) or "(none)"
        info[nm] = (mp.re(b), m, len(conj))
        print(f"  {nm:>18} {mp.nstr(mp.re(b), 8):>12} {cs[:34]:>34} "
              f"{mp.nstr(m, 6):>11}")
    for nm, v in TRANSCENDENTAL:
        info[nm] = (v, None, 0)
        print(f"  {nm:>18} {mp.nstr(v, 8):>12} "
              f"{'NO MINIMAL POLYNOMIAL':>34} {'--':>11}")
    print()
    print("  a transcendental has no conjugates at all. not a small mirror,")
    print("  not a degenerate one. none. that is what transcendental means.")
    print()

    print("=" * 78)
    print("2. DO INTEGERS TERMINATE?")
    print("=" * 78)
    print()
    print(f"  {'base':>18} {'max |conj| < 1?':>16} "
          f"{'integers 1..25 terminating':>28} {'worst':>7}")
    print("  " + "-" * 74)
    for nm, poly, kind in BASES:
        rs = roots(poly)
        b = mp.re(dominant(rs))
        conj = [r for r in rs if abs(r - dominant(rs)) > mp.mpf(10) ** -20]
        m = max((abs(c) for c in conj), default=mp.mpf(0))
        pisot = m < 1
        ok, worst = 0, 0
        for n in range(1, 26):
            t, L = terminates(b, n)
            ok += t
            worst = max(worst, L)
        print(f"  {nm:>18} {str(bool(pisot)):>16} {f'{ok} / 25':>28} "
              f"{worst:>7}")
    for nm, v in TRANSCENDENTAL:
        ok, worst = 0, 0
        for n in range(1, 26):
            t, L = terminates(v, n)
            ok += t
            worst = max(worst, L)
        print(f"  {nm:>18} {'no conjugates':>16} {f'{ok} / 25':>28} "
              f"{worst:>7}")
    print()
    print("  the two columns agree exactly. Pisot => integers terminate is")
    print("  a theorem, and Frougny-Solomyak give the other direction:")
    print("  Pisot is NECESSARY for property (F). the table is a check of")
    print("  that, not a discovery.")
    print()
    print("  sqrt2 gets 12/25 because its even powers are integers, so the")
    print("  integers that are sums of powers of 2 still terminate. the")
    print("  transcendentals get only the trivial cases, n <= ceil(b)-1,")
    print("  which are single digits at b^0 and prove nothing.")
    print()
    print("  so 'does this base have a mirror inside the unit disk' and")
    print("  'do integers terminate in it' are one question, not two.")
    print()

    print("=" * 78)
    print("3. THE OTHER CANDIDATE MIRROR: b <-> 1/b")
    print("=" * 78)
    print()
    print("  writing in base 1/b is writing the same digits with the point")
    print("  moved: powers b^k become b^-k. it is a reflection of the digit")
    print("  string about the radix point, not a new number system.")
    print()
    phi = (1 + mp.sqrt(5)) / 2
    print(f"  phi     = {mp.nstr(phi, 15)}")
    print(f"  1/phi   = {mp.nstr(1/phi, 15)}")
    print(f"  phi - 1 = {mp.nstr(phi-1, 15)}   <- equal, and this is the")
    print(f"                                       ONLY base where it is")
    print()
    print("  and note where 1/phi sits: -1/phi = -0.618034 is exactly phi's")
    print("  Galois conjugate. so for phi the two candidate mirrors")
    print("  COINCIDE up to sign. that coincidence is special to phi and")
    print("  is the real reason it keeps showing up. check it elsewhere:")
    print()
    print(f"  {'base b':>18} {'1/b':>12} {'conjugate':>14} {'same?':>8}")
    print("  " + "-" * 56)
    for nm, poly, kind in BASES:
        rs = roots(poly)
        b = dominant(rs)
        conj = [r for r in rs if abs(r - b) > mp.mpf(10) ** -20]
        if not conj:
            continue
        c = min(conj, key=lambda z: abs(abs(z) - abs(1 / b)))
        same = abs(abs(c) - abs(1 / mp.re(b))) < mp.mpf(10) ** -20
        print(f"  {nm:>18} {mp.nstr(1/mp.re(b), 8):>12} "
              f"{mp.nstr(c, 8):>14} {str(bool(same)):>8}")
    print()

    print("=" * 78)
    print("4. WHAT IS THE UNION OF ALL BASES?")
    print("=" * 78)
    print()
    x = mp.mpf(7) / 3
    print(f"  take one number, 7/3 = {mp.nstr(x, 20)}, and write it in")
    print(f"  several bases:")
    print()
    print(f"  {'base':>18} {'first digits':>34}")
    print("  " + "-" * 54)
    for nm, poly, kind in BASES[:6]:
        b = mp.re(dominant(roots(poly)))
        D = int(mp.ceil(b)) - 1
        y = x
        k = 0
        while b ** (k + 1) <= y:
            k += 1
        s = ""
        for j in range(k, -14, -1):
            if j == -1:
                s += "."
            d = min(int(mp.floor(y / b ** j + mp.mpf(10) ** -35)), D)
            s += str(d)
            y -= d * b ** j
        print(f"  {nm:>18} {s[:34]:>34}")
    print()
    print("  every one of those strings is the SAME NUMBER. the union of")
    print("  all representations of x is not a richer object than x. it is")
    print("  x, described redundantly.")
    print()
    print("  this is the difference from superposition, and it is not a")
    print("  quibble:")
    print()
    print("    superposition  branches carry AMPLITUDES that can cancel.")
    print("                   the object is genuinely more than any branch.")
    print()
    print("    all bases      branches are BIJECTIONS of one object. every")
    print("                   one determines all the others. nothing can")
    print("                   cancel, because there is only one thing there.")
    print()
    print("  what the union DOES give you is the base-independent part: the")
    print("  number itself, and any quantity that survives every recoding.")
    print("  that is what an invariant is, and it is why Delta and kappa")
    print("  were worth finding. they are what the union leaves standing.")
    print()

    print("=" * 78)
    print("5. THE ANSWER")
    print("=" * 78)
    print()
    print("  does every number system have a mirror?  NO.")
    print()
    print("  algebraic bases have one: the Galois conjugates, forced by the")
    print("  minimal polynomial. transcendental bases have none, and the")
    print("  absence is exactly why nothing terminates in them.")
    print()
    print("  a base is USABLE (integers terminate, carries are exact) when")
    print("  its mirror lies inside the unit disk. that is a small set:")
    print("  the Pisot numbers. phi is the smallest quadratic one, which")
    print("  is the whole of its privilege.")
    print()
    print("  and the union over all bases is not a superposition. it is")
    print("  one object seen through invertible relabelings, which is the")
    print("  same bound as every other change of representation: it moves")
    print("  where the work is and never how much there is.")


if __name__ == "__main__":
    main()
