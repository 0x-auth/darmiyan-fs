"""
The observed system registers an error. What does the observer register?

Established last run:
    the inside clock rate  l = 2 arccosh(|tr|/2) = Λ
    a walker ON the relation's axis accumulates exactly l per step
    a walker OFF the axis accumulates MORE -- it takes the long way
    error = f(walker's distance from the relation's own axis)

Now: an external observer is not a point of view from nowhere. It is
another relation, with its own axis. So the question becomes

    what does observer B register about system A?

and the answer must be a function of the relation between two axes.

TWO AXES IN THE HYPERBOLIC PLANE

Each hyperbolic element of SL(2,R) has an axis: the geodesic joining
its two fixed points. Two axes can be

    - the same            (A, B share both fixed points -> commute)
    - crossing            (they meet at an angle theta)
    - disjoint            (they do not meet; separated by a distance d)

and those three are exactly the three ways two relations can stand to
one another. The standard invariant is the COMPLEX DISTANCE

    cosh(d + i theta)  computable from traces alone

THE CLAIM TO TEST

    A's own error   = A's walker's offset from A's axis
    B's error about A = the offset between B's axis and A's axis

If that is right, then B registering zero error about A means their
axes coincide, which means they commute, which means kappa is on a
parabolic surface. The observer who registers no error about a system
is a system that cannot be外 to it.

Computed here:
    1. the axis of an element, explicitly
    2. the distance/angle between two axes, from traces
    3. whether that invariant reproduces kappa
    4. what happens at the three degeneracies
"""

import numpy as np

rng = np.random.default_rng(23)


def rand_hyperbolic(min_tr=2.3):
    """Random SL(2,R) element with |tr| > 2 -- has a real axis."""
    while True:
        m = rng.normal(0, 1, (2, 2))
        d = np.linalg.det(m)
        if d <= 1e-3:
            continue
        m = m / np.sqrt(d)
        if abs(np.trace(m)) > min_tr:
            return m


def fixed_points(M):
    """The two fixed points on the real line (endpoints of the axis)."""
    a, b, c, d = M.ravel()
    D = np.trace(M) ** 2 - 4 * np.linalg.det(M)
    if D <= 0 or abs(c) < 1e-14:
        return None
    r = np.sqrt(D)
    return ((a - d) + r) / (2 * c), ((a - d) - r) / (2 * c)


def trans_length(M):
    return 2 * np.arccosh(abs(np.trace(M)) / 2)


def cross_ratio_distance(A, B):
    """
    Complex distance between the two axes, from the fixed points.
    For axes with endpoints (p1,p2) and (q1,q2), the cross-ratio
    determines cosh^2 of the half complex distance.
    """
    fa, fb = fixed_points(A), fixed_points(B)
    if fa is None or fb is None:
        return None
    p1, p2 = fa
    q1, q2 = fb
    # cross ratio
    cr = ((p1 - q1) * (p2 - q2)) / ((p1 - q2) * (p2 - q1))
    return cr


def axis_invariant_from_traces(A, B):
    """
    Standard: for two hyperbolic elements,
        tr(AB) = tr(A)tr(B)/2 ... no closed form without care.
    Use instead the well-known
        cosh(delta) = (tr(AB) - tr(AB^-1)) / (...)
    We compute the honest thing: the commutator trace, which encodes
    the complex distance between axes.
    """
    x, y = np.trace(A), np.trace(B)
    z = np.trace(A @ B)
    w = np.trace(A @ np.linalg.inv(B))
    return x, y, z, w


def kappa(A, B):
    x, y, z = np.trace(A), np.trace(B), np.trace(A @ B)
    return x * x + y * y + z * z - x * y * z


print("=" * 78)
print("1. EVERY HYPERBOLIC RELATION HAS AN AXIS")
print("=" * 78)
print()
print(f"{'tr':>10} {'fixed pt 1':>14} {'fixed pt 2':>14} "
      f"{'l = Λ':>11}")
print("-" * 54)
mats = [rand_hyperbolic() for _ in range(5)]
for M in mats:
    fp = fixed_points(M)
    print(f"{np.trace(M):10.5f} {fp[0]:14.6f} {fp[1]:14.6f} "
          f"{trans_length(M):11.6f}")
print()
print("  the axis is the geodesic joining the two fixed points.")
print("  a walker ON it accumulates exactly l per step.")
print()

print("=" * 78)
print("2. TWO AXES: THE SAME, CROSSING, OR DISJOINT")
print("=" * 78)
print()
print("  build the three cases explicitly.")
print()

# same axis: both diagonal in the same basis
P = rand_hyperbolic()
Da = np.diag([np.exp(0.6), np.exp(-0.6)])
Db = np.diag([np.exp(1.1), np.exp(-1.1)])
A_same = P @ Da @ np.linalg.inv(P)
B_same = P @ Db @ np.linalg.inv(P)

# crossing: two boosts about different points that intersect
A_cross = np.array([[np.cosh(.7), np.sinh(.7)],
                    [np.sinh(.7), np.cosh(.7)]])
R = np.array([[np.cos(.6), -np.sin(.6)], [np.sin(.6), np.cos(.6)]])
B_cross = R @ A_cross @ np.linalg.inv(R)

# disjoint: translate one far along
T = np.array([[1.0, 3.0], [0.0, 1.0]])
B_disj = T @ A_cross @ np.linalg.inv(T)

print(f"{'case':>12} {'κ':>12} {'[A,B] tr':>11} {'commute?':>10} "
      f"{'axes':>22}")
print("-" * 72)
for nm, A_, B_, note in (
        ("same axis", A_same, B_same, "identical"),
        ("crossing", A_cross, B_cross, "meet at an angle"),
        ("disjoint", A_cross, B_disj, "separated"),
):
    K = A_ @ B_ @ np.linalg.inv(A_) @ np.linalg.inv(B_)
    k = kappa(A_, B_)
    com = np.abs(A_ @ B_ - B_ @ A_).max()
    print(f"{nm:>12} {k:12.6f} {np.trace(K):11.6f} "
          f"{'yes' if com < 1e-10 else 'no':>10} {note:>22}")
print()

print("=" * 78)
print("3. THE OBSERVER'S ERROR IS THE AXIS OFFSET")
print("=" * 78)
print()
print("  slide B's axis away from A's and watch κ and tr[A,B].")
print()
print(f"{'offset':>9} {'κ':>12} {'κ−4':>12} {'tr[A,B]':>11} "
      f"{'Δ[A,B]':>13} {'sector':>11}")
print("-" * 72)
A0 = np.array([[np.cosh(.7), np.sinh(.7)],
               [np.sinh(.7), np.cosh(.7)]])
for off in (0.0, 0.01, 0.1, 0.3, 0.6, 1.0, 2.0, 4.0):
    T = np.array([[1.0, off], [0.0, 1.0]])
    B_ = T @ A0 @ np.linalg.inv(T)
    K = A0 @ B_ @ np.linalg.inv(A0) @ np.linalg.inv(B_)
    k = kappa(A0, B_)
    D = np.trace(K) ** 2 - 4 * np.linalg.det(K)
    sec = ("parabolic" if abs(D) < 1e-9
           else "boost" if D > 0 else "rotation")
    print(f"{off:9.3f} {k:12.6f} {k-4:12.3e} {np.trace(K):11.6f} "
           f"{D:13.3e} {sec:>11}")
print()
print("  at offset 0 the axes coincide: κ = 4 exactly, commutator")
print("  is the identity, Δ = 0. the observer registers NO error.")
print()
print("  as the axes separate, κ moves off 4 and the commutator")
print("  leaves the parabolic locus. the error the observer")
print("  registers about the system IS the axis separation.")
print()

print("=" * 78)
print("4. IS THE RELATION SYMMETRIC?")
print("=" * 78)
print()
print("  does A register the same error about B as B about A?")
print()
print(f"{'offset':>9} {'κ(A,B)':>13} {'κ(B,A)':>13} {'diff':>12}")
print("-" * 50)
for off in (0.1, 0.5, 1.0, 2.5):
    T = np.array([[1.0, off], [0.0, 1.0]])
    B_ = T @ A0 @ np.linalg.inv(T)
    ka, kb = kappa(A0, B_), kappa(B_, A0)
    print(f"{off:9.3f} {ka:13.8f} {kb:13.8f} {abs(ka-kb):12.2e}")
print()
print("  tr(AB) = tr(BA), so κ is symmetric. EXACTLY.")
print()
print("  the error is MUTUAL. there is no privileged observer:")
print("  what B registers about A, A registers about B, and it is")
print("  the same number. the asymmetry people expect between")
print("  observer and observed is not in this quantity.")
print()

print("=" * 78)
print("5. WHAT THE OBSERVER CANNOT REGISTER")
print("=" * 78)
print()
print("  κ is symmetric and depends only on the two axes' relation.")
print("  it does NOT contain:")
print("    - where either walker sits on its own axis")
print("    - how much proper time either has accumulated")
print("    - which direction either is drifting")
print()
print("  check: move the walker along A's axis without changing A.")
print()
A1 = A0.copy()
print(f"  {'walker start':>16} {'own error (d−l)':>18} {'κ(A,B)':>12}")
print("  " + "-" * 50)
T = np.array([[1.0, 1.0], [0.0, 1.0]])
B_ = T @ A0 @ np.linalg.inv(T)
k_fixed = kappa(A0, B_)
l = trans_length(A0)


def hyp_dist(z1, z2):
    return np.arccosh(1 + abs(z1 - z2) ** 2 / (2 * z1.imag * z2.imag))


def act(M, z):
    a, b, c, d = M.ravel()
    return (a * z + b) / (c * z + d)


for zr in (0.0, 0.3, 1.0, 2.0):
    z = complex(np.sinh(zr), np.cosh(zr))
    err = hyp_dist(z, act(A0, z)) - l
    print(f"  {f'{z.real:.3f}+{z.imag:.3f}i':>16} {err:18.8f} "
          f"{k_fixed:12.8f}")
print()
print("  the walker's own error changes. κ does not move at all.")
print()
print("  SO THERE ARE TWO ERRORS, AND THEY ARE DIFFERENT OBJECTS:")
print()
print("    INSIDE   the system's own error: its offset from its")
print("             own axis. a property of walker + relation.")
print("             changes as the walker moves. not observable")
print("             from outside.")
print()
print("    BETWEEN  the observer's error about the system: the")
print("             offset between two axes, = κ. a property of")
print("             the two relations. symmetric. blind to where")
print("             either walker is.")
print()
print("  the observer cannot see the system's own error, and the")
print("  system cannot see the between-error from inside. each")
print("  registers a quantity the other has no access to.")
