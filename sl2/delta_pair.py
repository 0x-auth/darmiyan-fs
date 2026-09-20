"""
Delta of the pair.

Every quantity computed last night had an x in it -- C_space(x),
C_time(x), looking(beta), living(x0). All state-dependent, all
measured by sampling and averaging, all failed to hold still.

Darmiyan, line 15: "Delta has no x in it. It is a property of the
relation between before and after, not of any state."

So compute the invariant of the RELATION, not its action on states.
No sampling. No p-values. No nulls. It either has the structure or
it does not.

--------------------------------------------------------------------
SETUP

Two accounts of one event, as Mobius maps in SL(2,R):

    M_+ = [[a + s,  b], [c, d]]        account: the event was +
    M_- = [[a - s,  b], [c, d]]        account: the event was -

For a single map M, the discriminant

    Delta(M) = tr(M)^2 - 4 det(M)

sorts it:  Delta > 0  hyperbolic  -> boost, arrowed time
           Delta = 0  parabolic   -> lightlike, the between
           Delta < 0  elliptic    -> rotation, phase only

THE PAIR. The relation between the two accounts is their
commutator in the group:

    K = M_+ M_-  (M_+ M_-)^{-1} ... no. the group commutator is
    K = M_+ M_- M_+^{-1} M_-^{-1}

K is identity iff the accounts commute. Its Delta classifies HOW
they fail to commute -- and that classification has no x in it.

QUESTIONS
  1. Does Delta(K) sort into the three sectors?
  2. Where is Delta(K) = 0 -- the lightlike between?
  3. Is there a relation among Delta(M_+), Delta(M_-), Delta(K)?
  4. The claim "light is the darmiyan between space and time":
     at Delta(K) = 0, what happens to C_space and C_time?
"""

import numpy as np
import sympy as sp


# ============================================================ symbolic

def symbolic():
    a, b, c, d, s = sp.symbols('a b c d s', real=True)

    Mp = sp.Matrix([[a + s, b], [c, d]])
    Mm = sp.Matrix([[a - s, b], [c, d]])

    print("=" * 74)
    print("THE TWO ACCOUNTS")
    print("=" * 74)
    print()
    for nm, M in (("M_+", Mp), ("M_-", Mm)):
        tr = sp.simplify(M.trace())
        dt = sp.simplify(M.det())
        D = sp.simplify(tr ** 2 - 4 * dt)
        print(f"  {nm}:  tr = {tr}")
        print(f"        det = {dt}")
        print(f"        Delta = {sp.expand(D)}")
        print()

    # group commutator
    K = sp.simplify(Mp * Mm * Mp.inv() * Mm.inv())
    trK = sp.simplify(sp.expand(sp.trace(K)))
    detK = sp.simplify(K.det())
    DK = sp.simplify(sp.expand(trK ** 2 - 4 * detK))

    print("=" * 74)
    print("THE PAIR:  K = M+ M- M+^-1 M-^-1")
    print("=" * 74)
    print()
    print("  det K =", detK, "   (must be 1 -- commutators are unimodular)")
    print()
    print("  tr K =")
    print("   ", sp.simplify(trK))
    print()
    print("  Delta(K) = tr(K)^2 - 4 =")
    DK2 = sp.simplify(sp.factor(sp.expand(trK ** 2 - 4)))
    print("   ", DK2)
    print()

    # when is Delta(K) = 0?
    print("=" * 74)
    print("WHERE IS THE BETWEEN?   Delta(K) = 0")
    print("=" * 74)
    print()
    sols = sp.solve(sp.Eq(DK2, 0), s)
    print("  solving for s:")
    for sol in sols:
        print("   ", sp.simplify(sol))
    print()

    # trace as a function of s, expanded
    print("=" * 74)
    print("tr(K) expanded in s")
    print("=" * 74)
    print()
    ser = sp.series(trK, s, 0, 5).removeO()
    print("  tr K =", sp.simplify(sp.expand(ser)))
    print()
    print("  at s = 0:  tr K =", sp.simplify(trK.subs(s, 0)))
    print("  (identity has trace 2 -- accounts commute, no conflict)")
    print()

    return a, b, c, d, s, trK, DK2


# ============================================================ numeric

def sector(D, tol=1e-12):
    if abs(D) < tol:
        return "LIGHTLIKE"
    return "BOOST" if D > 0 else "ROTATION"


def numeric():
    print("=" * 74)
    print("NUMERIC SCAN: Delta(K) across conflict strength s")
    print("=" * 74)
    print()

    def K_of(a, b, c, d, s):
        Mp = np.array([[a + s, b], [c, d]], float)
        Mm = np.array([[a - s, b], [c, d]], float)
        return Mp @ Mm @ np.linalg.inv(Mp) @ np.linalg.inv(Mm)

    for (a, b, c, d) in [(1.0, 1.0, 1.0, 0.0),      # x -> 1 + 1/x
                         (1.5, 1.0, 1.0, 0.0),
                         (0.5, 1.0, 1.0, 0.0),
                         (1.0, 1.0, 1.0, 1.0)]:
        print(f"  base map  a={a} b={b} c={c} d={d}")
        D0 = (a + d) ** 2 - 4 * (a * d - b * c)
        print(f"    base Delta = {D0:+.6f}  ({sector(D0)})")
        print(f"    {'s':>8} {'tr K':>14} {'Delta(K)':>16} {'sector':>12}")
        print("    " + "-" * 52)
        for s in [0.0, 1e-3, 0.01, 0.1, 0.25, 0.5, 1.0, 2.0]:
            try:
                K = K_of(a, b, c, d, s)
                tr = np.trace(K)
                DK = tr ** 2 - 4 * np.linalg.det(K)
                print(f"    {s:8.3f} {tr:14.8f} {DK:16.8e} "
                      f"{sector(DK, 1e-10):>12}")
            except np.linalg.LinAlgError:
                print(f"    {s:8.3f} {'singular':>14}")
        print()


def connect_to_commutator():
    """
    Does Delta(K) predict the C_space / C_time behaviour measured
    in commute.py? The claim to test: at Delta(K) = 0 the two
    halves coincide -- the between.
    """
    print("=" * 74)
    print("DOES Delta(K) SORT THE COMMUTATOR BEHAVIOUR?")
    print("=" * 74)
    print()
    print("  Mobius map f(x) = (ax+b)/(cx+d) applied as a real map,")
    print("  the two accounts differing by s in the a-entry.")
    print()
    print(f"  {'s':>8} {'Delta(K)':>15} {'|C_space|':>13} "
          f"{'|C_time|':>13} {'ratio':>9}")
    print("  " + "-" * 62)

    a, b, c, d = 1.0, 1.0, 1.0, 0.0
    x0 = 1.3

    def mob(m, x):
        return (m[0, 0] * x + m[0, 1]) / (m[1, 0] * x + m[1, 1])

    for s in [1e-4, 1e-3, 0.01, 0.05, 0.1, 0.3, 0.7, 1.0]:
        Mp = np.array([[a + s, b], [c, d]], float)
        Mm = np.array([[a - s, b], [c, d]], float)
        K = Mp @ Mm @ np.linalg.inv(Mp) @ np.linalg.inv(Mm)
        DK = np.trace(K) ** 2 - 4 * np.linalg.det(K)

        cs = abs(mob(Mp, mob(Mm, x0)) - mob(Mm, mob(Mp, x0)))
        F = np.array([[a, b], [c, d]], float)
        ct = abs(mob(F, mob(Mp, x0)) - mob(Mp, mob(F, x0)))
        r = cs / ct if ct else np.nan
        print(f"  {s:8.4f} {DK:15.6e} {cs:13.6e} {ct:13.6e} {r:9.5f}")
    print()
    print("  Mobius maps compose exactly -- no tanh, no truncation.")
    print("  so this is the clean version of last night's measurement.")


if __name__ == "__main__":
    symbolic()
    numeric()
    connect_to_commutator()
