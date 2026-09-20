"""
Error as the gap between two definitions of time.

Λ measures one thing: how fast a relation leaves its own fixed point.
One clock. It is unsigned, and Λ_+ + Λ_- = 0 means the relation itself
supplies no direction.

A DIFFERENT quantity: the mismatch between a clock counted INSIDE the
relation and one counted OUTSIDE it. That is a difference of two
clocks, and a difference is signed by construction -- one runs slow
relative to the other, and which is which is a fact.

TWO CLOCKS, DEFINED

  OUTSIDE (coordinate):  n -- the number of applications of the map.
      the walker who counts steps from outside. every step counts 1.

  INSIDE (proper):       the arc length the walker actually traverses
      in the geometry the map preserves. for a Mobius map acting on
      the upper half plane, that is the hyperbolic metric
          ds = |dz| / Im(z)
      which the map preserves exactly. this is the walker's own
      ruler, carried along.

ERROR = the gap between them.

For a hyperbolic (boost) element the hyperbolic translation length is
      l = 2 arccosh(|tr|/2)
per application. So after n steps:
      outside reads  n
      inside reads   n * l
      gap per step   l - 1

For an elliptic (rotation) element there is no translation -- the
walker returns. l = 0, and the gap is -1 per step: the outside clock
counts, the inside does not.

For a parabolic element l = 0 as well, but the walker does NOT return;
it drifts to the single fixed point without ever arriving.

WHAT IS TESTED
  1. is l a relation invariant (no x)?          -- should be yes
  2. does it distinguish the three sectors?
  3. is the SIGN of the gap a relation property or a walker property?
  4. how does it relate to Lambda?
"""

import numpy as np
import sympy as sp

rng = np.random.default_rng(11)


def rand_sl2():
    while True:
        m = rng.normal(0, 1, (2, 2))
        d = np.linalg.det(m)
        if d > 1e-3:
            return m / np.sqrt(d)


def delta(M):
    return np.trace(M) ** 2 - 4 * np.linalg.det(M)


def sector(M, tol=1e-10):
    D = delta(M)
    return "parabolic" if abs(D) < tol else ("boost" if D > 0
                                             else "rotation")


def translation_length(M):
    """
    Hyperbolic translation length per application.
    l = 2 arccosh(|tr|/2) for |tr| > 2, else 0.
    This is the INSIDE clock's reading per OUTSIDE tick.
    """
    tr = abs(np.trace(M))
    return 2 * np.arccosh(tr / 2) if tr > 2 else 0.0


def Lam(M):
    """Λ = log|μ| at the repelling fixed point, i.e. |log| of the rate."""
    a, b, c, d = M.ravel()
    D = delta(M)
    if abs(c) < 1e-14 or D <= 0:
        return 0.0
    r = np.sqrt(D)
    x1 = ((a - d) + r) / (2 * c)
    det = np.linalg.det(M)
    mu = det / (c * x1 + d) ** 2
    return abs(np.log(abs(mu)))


def act(M, z):
    a, b, c, d = M.ravel()
    return (a * z + b) / (c * z + d)


def hyp_dist(z1, z2):
    """Hyperbolic distance in the upper half plane."""
    num = abs(z1 - z2) ** 2
    den = 2 * z1.imag * z2.imag
    return np.arccosh(1 + num / den)


print("=" * 78)
print("1. IS THE INSIDE CLOCK A RELATION INVARIANT?")
print("=" * 78)
print()
print("  measure the hyperbolic distance a point moves under one")
print("  application, from DIFFERENT starting points.")
print()
M = rand_sl2() * 1.0
# force a boost
M = np.array([[np.cosh(0.8), np.sinh(0.8)],
              [np.sinh(0.8), np.cosh(0.8)]])
print(f"  map: boost, tr = {np.trace(M):.6f}, "
      f"predicted l = {translation_length(M):.9f}")
print()
print(f"  {'start z':>22} {'d(z, Mz)':>14} {'matches l?':>12}")
print("  " + "-" * 50)
l_pred = translation_length(M)
for z in (1j, 2j, 0.5 + 1j, -1 + 3j, 0.1 + 0.1j, 5 + 0.2j):
    zz = complex(z)
    d = hyp_dist(zz, act(M, zz))
    print(f"  {str(zz):>22} {d:14.9f} "
          f"{'yes' if abs(d - l_pred) < 1e-6 else 'NO':>12}")
print()
print("  the distance DEPENDS on the starting point -- it equals l")
print("  only on the geodesic between the fixed points (the axis).")
print("  so the inside clock is a property of the relation PLUS")
print("  where the walker is. l is the MINIMUM over all starts:")
print(f"    min over the axis = l = {l_pred:.9f}")
print()

print("=" * 78)
print("2. THE TWO CLOCKS ACROSS THE SECTORS")
print("=" * 78)
print()
print(f"{'':>12} {'tr':>10} {'Δ':>12} {'outside/step':>13} "
      f"{'inside/step':>12} {'gap':>11} {'Λ':>10}")
print("-" * 84)
cases = []
for nm, eta in (("rotation", None),):
    pass
for nm, M_ in (
    ("rotation θ=1", np.array([[np.cos(1), -np.sin(1)],
                               [np.sin(1), np.cos(1)]])),
    ("rotation θ=2", np.array([[np.cos(2), -np.sin(2)],
                               [np.sin(2), np.cos(2)]])),
    ("parabolic", np.array([[1.0, 1.0], [0.0, 1.0]])),
    ("parabolic 2", np.array([[1.0, 5.0], [0.0, 1.0]])),
    ("boost η=0.1", np.array([[np.cosh(.1), np.sinh(.1)],
                              [np.sinh(.1), np.cosh(.1)]])),
    ("boost η=0.8", np.array([[np.cosh(.8), np.sinh(.8)],
                              [np.sinh(.8), np.cosh(.8)]])),
    ("boost η=2.0", np.array([[np.cosh(2.), np.sinh(2.)],
                              [np.sinh(2.), np.cosh(2.)]])),
):
    l = translation_length(M_)
    lam = Lam(M_)
    print(f"{nm:>12} {np.trace(M_):10.5f} {delta(M_):12.5f} "
          f"{1.0:13.1f} {l:12.6f} {l-1:11.6f} {lam:10.6f}")
    cases.append((nm, M_, l, lam))
print()

print("=" * 78)
print("3. l AND Λ ARE THE SAME QUANTITY")
print("=" * 78)
print()
print("  for a boost,  tr = 2cosh(η),  l = 2η,  and the multiplier")
print("  at the repelling point is μ = e^{2η}, so Λ = 2η = l.")
print()
print(f"{'map':>14} {'l':>12} {'Λ':>12} {'l − Λ':>12}")
print("-" * 54)
for nm, M_, l, lam in cases:
    print(f"{nm:>14} {l:12.8f} {lam:12.8f} {l-lam:12.2e}")
print()
print("  identical. the INSIDE clock rate IS Λ.")
print("  so 'error of time' and 'arrow of time' are not two")
print("  quantities that happen to agree -- they are one quantity")
print("  read two ways: as a rate of divergence, and as a rate of")
print("  proper-time accumulation.")
print()

print("=" * 78)
print("4. WHERE THE SIGN LIVES")
print("=" * 78)
print()
print("  l ≥ 0 always. Λ ≥ 0 as computed. neither carries direction.")
print()
print("  the DIRECTION comes from which fixed point the walker is")
print("  near. same map, two starting points, opposite drift:")
print()
Mb = np.array([[np.cosh(.8), np.sinh(.8)],
               [np.sinh(.8), np.cosh(.8)]])
print(f"  {'start':>12} {'after 1':>16} {'after 5':>16} {'drift':>10}")
print("  " + "-" * 58)
for z0 in (0.3 + 1j, -0.3 + 1j, 2 + 1j, -2 + 1j):
    z = complex(z0)
    z1 = act(Mb, z)
    z5 = z
    for _ in range(5):
        z5 = act(Mb, z5)
    drift = "→ +1" if z5.real > z.real else "→ −1"
    print(f"  {str(z0):>12} {f'{z1.real:.4f}+{z1.imag:.4f}i':>16} "
          f"{f'{z5.real:.4f}+{z5.imag:.4f}i':>16} {drift:>10}")
print()
print("  the relation has two fixed points, +1 and −1 here, one")
print("  attracting and one repelling. EVERY walker not exactly on")
print("  the repelling point drifts to the attracting one.")
print()
print("  so the direction IS determined by the relation (which point")
print("  attracts), but the MAGNITUDE of a walker's error depends on")
print("  where it started. the opposite of what I said last turn.")
print()

print("=" * 78)
print("5. THE INSIDE/OUTSIDE GAP AS A FUNCTION OF POSITION")
print("=" * 78)
print()
print("  outside counts 1 per step. inside counts d(z, Mz), which")
print("  is ≥ l and equals l only on the axis.")
print()
print(f"  {'distance from axis':>20} {'d(z,Mz)':>12} {'gap over l':>12}")
print("  " + "-" * 48)
axis_pt = 1j
for off in (0.0, 0.2, 0.5, 1.0, 2.0, 4.0):
    z = complex(np.sinh(off) * 0 + off, np.cosh(off) * 1) if off else 1j
    z = 1j * np.cosh(off) + np.sinh(off)
    d = hyp_dist(z, act(Mb, z))
    print(f"  {off:20.2f} {d:12.8f} {d - l_pred:12.8f}")
print()
print("  the further from the axis, the more the inside clock")
print("  over-counts relative to the relation's own minimum.")
print()
print("  THAT is the error between the two definitions of time:")
print("  not a property of the relation, and not a property of the")
print("  walker, but of the walker's DISTANCE FROM THE RELATION'S")
print("  OWN AXIS.")
print()
print("  on the axis: inside and outside agree up to the factor l.")
print("  off the axis: the walker accumulates more proper time than")
print("  the relation requires. it takes the long way.")
