#!/usr/bin/env python3
"""instants.py — how many instants must a system see of itself before it can
know its own law?

A Möbius law f(x) = (ax+b)/(cx+d) is defined only up to overall scale, so it
has 3 degrees of freedom. Each observed transition x -> y gives ONE homogeneous
linear equation in (a, b, c, d):

        y (c x + d) = a x + b      ->      a·x + b·1 − c·(x y) − d·y = 0

k instants of self-observation give k−1 transitions. With k−1 equations in 4
unknowns the solution is a linear subspace of dimension 4 − (k−1); dividing out
the scale leaves 3 − (k−1) genuinely free directions. The law is pinned only
at k = 4.

The point is not accuracy. Every number below is an exact rational, so the
sensing is perfect. What is missing is instants, not precision.

    python3 instants.py
"""
import sympy as sp

A, B, C, D = sp.Rational(17, 10), sp.Rational(-9, 10), sp.Integer(1), sp.Integer(0)
f = lambda x: (A * x + B) / (C * x + D)                 # the true law

def delta(v):
    """Δ = (tr² − 4 det)/|det|, scale-free. Sign: + arrow (boost), − phase (rotation)."""
    a, b, c, d = v
    det = sp.simplify(a * d - b * c)
    if det == 0:
        return None
    return sp.simplify(((a + d) ** 2 - 4 * det) / abs(det))

def trajectory(x0, n):
    xs = [sp.Rational(x0)]
    for _ in range(n):
        xs.append(sp.nsimplify(f(xs[-1])))
    return xs

def constraints(xs, k):
    """One homogeneous row per transition: [x, 1, −x·y, −y]."""
    return sp.Matrix([[xs[i], 1, -xs[i] * xs[i + 1], -xs[i + 1]] for i in range(k - 1)])

def believable(xs, k, spread=12, step=1):
    """Every law still consistent with k instants -> the Δ values the system could hold."""
    M = constraints(xs, k)
    basis = M.nullspace() if M.rows else [sp.Matrix(e) for e in sp.eye(4).tolist()]
    dim = len(basis)
    out = []
    if dim == 1:                                        # pinned (up to scale)
        return [delta(list(basis[0]))], dim
    coeffs = [sp.Rational(i, 2) for i in range(-spread, spread + 1, step)]
    def walk(i, vec):
        if i == dim:
            if any(vec):
                dl = delta(list(vec))
                if dl is not None and abs(dl) < 10**6:
                    out.append(dl)
            return
        for t in coeffs:
            walk(i + 1, vec + t * basis[i])
    walk(0, sp.zeros(4, 1))
    return out, dim

if __name__ == "__main__":
    xs = trajectory(sp.Rational(4, 5), 6)
    true = delta([A, B, C, D])
    print(f"true law: x -> ({float(A)}·x {float(B):+})/({float(C)}·x {float(D):+})"
          f"      Δ = {float(true):+.6f}   ({'arrow' if true > 0 else 'phase'})\n")
    print(f"{'instants':>9}{'transitions':>13}{'free dirs':>11}{'pinned?':>9}"
          f"{'   Δ the system could believe':>32}{'  sector right':>15}")
    for k in (1, 2, 3, 4, 5):
        ds, dim = believable(xs, k, spread=(12 if k > 1 else 6))
        free = dim - 1
        if free == 0:
            print(f"{k:>9}{k-1:>13}{free:>11}{'yes':>9}{float(ds[0]):>32.6f}{'exact':>15}")
        else:
            lo, hi = min(ds), max(ds)
            ok = sum(1 for d in ds if (d > 0) == (true > 0)) / len(ds)
            rng = f"{float(lo):.1f} … {float(hi):.1f}"
            print(f"{k:>9}{k-1:>13}{free:>11}{'no':>9}{rng:>32}{ok*100:>14.0f}%")
    print("\n  free dirs  = 3 − transitions: the space of laws still consistent with what was seen")
    print("  sector right = share of those laws that agree on whether an arrow of time exists")
    print("\n  1 instant  -> no transition: the law is entirely unconstrained")
    print("  2, 3       -> the motion is known, the law is not, and neither is the SECTOR:")
    print("                the system cannot yet tell whether it has a before and after")
    print("  4 instants -> the law, exactly")
    print("\n  Every value here is an exact rational: precision was never the limit.")
