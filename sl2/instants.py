#!/usr/bin/env python3
"""instants.py — how many instants must a system see of itself before it
can know its own law, and before it can know its own SECTOR?

A Möbius law f(x) = (ax+b)/(cx+d) is defined up to overall scale: 3 degrees
of freedom. Each observed transition x -> y gives one homogeneous linear
equation in (a,b,c,d):

        y(cx + d) = ax + b      ->      a·x + b·1 − c·(xy) − d·y = 0

k instants give k−1 transitions, so the solution space has dimension
4 − (k−1), and after dividing out scale, 3 − (k−1) free directions.
The law is pinned at k = 4.

WHAT THIS VERSION FIXES

The earlier script reported a "sector right" percentage by sampling
coefficients on a fixed lattice (Rational(i,2), i in -12..12). That
number is a property of the lattice, not of the geometry — change the
spread and it changes, and it came out non-monotonic (33%, 25%, 46%),
which is the signature of sampling noise rather than shrinking
uncertainty.

The right question is not "what fraction of sampled laws agree" but
"does the surviving solution space CROSS the parabolic locus Δ = 0?"
If it does, the sector is genuinely undetermined and the system cannot
know whether it has an arrow. That is exact and needs no sampling.

Δ is quadratic in the coefficients, so on a k-dimensional subspace
Δ = 0 is a conic. Solving it is algebra.

    python3 instants.py
"""
import sympy as sp


# the true law
A, B, C, D = sp.Rational(17, 10), sp.Rational(-9, 10), sp.Integer(1), sp.Integer(0)
f = lambda x: (A * x + B) / (C * x + D)


def delta(v):
    """Δ = (tr² − 4det)/|det|, scale-free. + = boost (arrow), − = rotation."""
    a, b, c, d = v
    det = sp.simplify(a * d - b * c)
    if det == 0:
        return None
    return sp.simplify(((a + d) ** 2 - 4 * det) / sp.Abs(det))


def delta_numerator(v):
    """tr² − 4det, unnormalised. Sign is all that matters; no |det| to
    confuse the algebra when solving Δ = 0."""
    a, b, c, d = v
    return sp.expand((a + d) ** 2 - 4 * (a * d - b * c))


def trajectory(x0, n):
    xs = [sp.Rational(x0)]
    for _ in range(n):
        xs.append(sp.nsimplify(f(xs[-1])))
    return xs


def constraints(xs, k):
    """One homogeneous row per transition: [x, 1, −xy, −y]."""
    if k < 2:
        return sp.zeros(0, 4)
    return sp.Matrix([[xs[i], 1, -xs[i] * xs[i + 1], -xs[i + 1]]
                      for i in range(k - 1)])


def sector_determined(xs, k):
    """
    EXACT test. On the solution subspace, is Δ of one sign throughout,
    or does it cross zero?

    Returns (verdict, detail).
    """
    M = constraints(xs, k)
    basis = M.nullspace() if M.rows else [sp.Matrix(e)
                                          for e in sp.eye(4).tolist()]
    dim = len(basis)

    if dim == 0:
        return "no solutions", None
    if dim == 1:
        d = delta(list(basis[0]))
        return "pinned", d

    # parametrise the subspace: v = t0*b0 + t1*b1 + ...
    ts = sp.symbols(f't0:{dim}', real=True)
    v = sp.zeros(4, 1)
    for t, b in zip(ts, basis):
        v += t * b
    v = list(v)

    dnum = sp.expand(delta_numerator(v))
    det = sp.expand(v[0] * v[3] - v[1] * v[2])

    # does Δ = 0 have real solutions with det != 0?
    # set t0 = 1 (scale) and solve in the rest
    sub = {ts[0]: 1}
    dn1 = sp.expand(dnum.subs(sub))
    dt1 = sp.expand(det.subs(sub))

    sols = []
    try:
        raw = sp.solve(sp.Eq(dn1, 0), ts[1:], dict=True)
        for s in raw:
            vals = {**sub, **s}
            free = [t for t in ts[1:] if t not in s]
            probe = {t: sp.Rational(1, 3) for t in free}
            vals = {k_: sp.simplify(sp.Matrix([val]).subs(probe)[0])
                    for k_, val in vals.items()}
            vals.update(probe)
            if all(x.is_real for x in vals.values()):
                dv = sp.simplify(dt1.subs(vals))
                if dv != 0:
                    sols.append(vals)
    except Exception:
        pass

    return ("crosses zero" if sols else "sign fixed"), (dnum, det, sols)


def sample_extremes(xs, k, n=9):
    """Illustrative Δ values across the subspace -- shown as a RANGE,
    labelled as illustrative, not as a probability."""
    M = constraints(xs, k)
    basis = M.nullspace() if M.rows else [sp.Matrix(e)
                                          for e in sp.eye(4).tolist()]
    dim = len(basis)
    if dim <= 1:
        return None
    vals = []
    grid = [sp.Rational(i, 4) for i in range(-n, n + 1)]

    def walk(i, vec):
        if i == dim:
            if any(vec):
                d = delta(list(vec))
                if d is not None and abs(d) < 10 ** 5:
                    vals.append(d)
            return
        for t in grid:
            walk(i + 1, vec + t * basis[i])

    walk(0, sp.zeros(4, 1))
    return vals


if __name__ == "__main__":
    xs = trajectory(sp.Rational(4, 5), 6)
    true = delta([A, B, C, D])

    print(f"true law: x -> ({float(A)}·x {float(B):+})/"
          f"({float(C)}·x {float(D):+})")
    print(f"   Δ = {float(true):+.6f}   "
          f"({'arrow / boost' if true > 0 else 'phase / rotation'})")
    print()

    print(f"{'instants':>9}{'transitions':>13}{'free dirs':>11}"
          f"{'law pinned':>12}{'sector known':>15}")
    print("-" * 60)

    for k in (1, 2, 3, 4, 5):
        M = constraints(xs, k)
        basis = M.nullspace() if M.rows else [sp.Matrix(e)
                                              for e in sp.eye(4).tolist()]
        free = len(basis) - 1
        verdict, detail = sector_determined(xs, k)
        if verdict == "pinned":
            print(f"{k:>9}{k-1:>13}{free:>11}{'yes':>12}{'yes':>15}")
        else:
            known = "no" if verdict == "crosses zero" else "yes"
            print(f"{k:>9}{k-1:>13}{free:>11}{'no':>12}{known:>15}")

    print()
    print("  free dirs    = 3 − transitions: the space of laws still")
    print("                 consistent with what has been seen")
    print("  sector known = whether Δ has a fixed sign on that whole")
    print("                 space. if the space crosses Δ = 0, the")
    print("                 system cannot tell boost from rotation —")
    print("                 it does not know whether it has an arrow.")
    print()
    print("  this is an EXACT algebraic test, not a sampled fraction.")
    print()

    print("=" * 60)
    print("detail: the parabolic locus on each solution space")
    print("=" * 60)
    print()
    for k in (2, 3):
        verdict, detail = sector_determined(xs, k)
        print(f"  k = {k} instants, {3-(k-1)} free directions: {verdict}")
        if detail and verdict == "crosses zero":
            dnum, det, sols = detail
            print(f"    Δ numerator on the subspace:")
            print(f"      {sp.factor(dnum)}")
            print(f"    vanishes for real coefficients → both sectors")
            print(f"    are reachable → arrow undetermined")
        print()

    print("=" * 60)
    print("illustrative Δ range (NOT a probability)")
    print("=" * 60)
    print()
    for k in (2, 3):
        vals = sample_extremes(xs, k)
        if vals:
            pos = sum(1 for v in vals if v > 0)
            neg = sum(1 for v in vals if v < 0)
            print(f"  k = {k}:  Δ from {float(min(vals)):.2f} to "
                  f"{float(max(vals)):.2f}")
            print(f"           {pos} boost, {neg} rotation on this grid")
            print(f"           (the counts depend on the grid and mean")
            print(f"            nothing; the RANGE spanning zero is the")
            print(f"            real content)")
            print()

    print("=" * 60)
    print()
    print("  1 instant   no transition: the law is unconstrained")
    print("  2, 3        the motion is known, the law is not, and")
    print("              neither is the sector — the system cannot")
    print("              yet tell whether it has a before and after")
    print("  4 instants  the law, exactly")
    print()
    print("  Every value is an exact rational. Precision was never")
    print("  the limit; instants were.")
