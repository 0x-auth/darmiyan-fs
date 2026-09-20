"""
Δ, followed.

No claims. Compute what SL(2,R) gives and print it.
"""

import numpy as np
import sympy as sp

# ---------------------------------------------------------------- symbolic

a, b, c, d, s, t, x, e = sp.symbols('a b c d s t x epsilon', real=True)

M = sp.Matrix([[a, b], [c, d]])
D = sp.expand(M.trace()**2 - 4*M.det())

print("Δ = tr² − 4det =", D)
print()

# fixed points
fx = sp.solve(sp.Eq((a*x + b)/(c*x + d), x), x)
print("fixed points:")
for f in fx:
    print("   ", sp.simplify(f))
print()

# multipliers
mu = [sp.simplify(M.det()/(c*f + d)**2) for f in fx]
print("multipliers:")
for m in mu:
    print("   ", sp.simplify(m))
print("product:", sp.simplify(sp.expand(mu[0]*mu[1])))
print()

# the generator
print("one-parameter subgroups, exp(tX), X traceless:")
for nm, X in (("boost   ", sp.Matrix([[1, 0], [0, -1]])),
              ("rotation", sp.Matrix([[0, -1], [1, 0]])),
              ("shear   ", sp.Matrix([[0, 1], [0, 0]]))):
    E = sp.simplify(sp.exp(X*t))
    dd = sp.simplify(sp.expand(E.trace()**2 - 4*E.det()))
    print(f"  {nm}  exp(tX) = {E.tolist()}")
    print(f"            Δ = {dd}")
print()

# X^2 = kI classification
print("X traceless ⇒ X² = −det(X)·I. So:")
Xg = sp.Matrix([[sp.Symbol('p'), sp.Symbol('q')],
                [sp.Symbol('r'), -sp.Symbol('p')]])
print("   det X =", sp.expand(Xg.det()))
print("   Δ(exp(tX)) = 4 sinh²(t√(−det X))  when det X < 0")
print("              = 4 sin²(t√(det X))·(−1) when det X > 0")
print("              = 0 identically       when det X = 0")
print()

# ---------------------------------------------------------------- numeric

print("=" * 70)
print()

def delta(m):
    m = np.asarray(m, float)
    return np.trace(m)**2 - 4*np.linalg.det(m)

def sector(D, tol=1e-12):
    return "0" if abs(D) < tol else ("+" if D > 0 else "−")

# the generator plane: X = [[p,q],[r,-p]], det X = -p²-qr
print("Δ(exp X) across the generator plane, det X = −p²−qr:")
print()
print(f"{'p':>6} {'q':>6} {'r':>6} {'detX':>9} {'Δ(exp X)':>13} {'sec':>5}")
print("-" * 48)
import scipy.linalg as sla
for p_, q_, r_ in [(1,0,0), (0,1,-1), (0,1,0), (0,0,1),
                   (1,1,-1), (1,1,0), (0.5,1,-0.5), (1,2,-1),
                   (0,2,-0.5), (1,0.5,-2)]:
    X = np.array([[p_, q_], [r_, -p_]], float)
    E = sla.expm(X)
    print(f"{p_:6.2f} {q_:6.2f} {r_:6.2f} {np.linalg.det(X):9.4f} "
          f"{delta(E):13.6e} {sector(delta(E)):>5}")
print()
print("det X < 0 → Δ > 0.  det X > 0 → Δ < 0.  det X = 0 → Δ = 0.")
print("the generator's determinant sets the sector. one number.")
print()

# the null cone in the Lie algebra
print("=" * 70)
print()
print("det X = −p² − qr = 0 is a cone in the 3d space (p,q,r).")
print("its signature:")
Q = np.array([[-1, 0, 0], [0, 0, -0.5], [0, -0.5, 0]], float)
w = np.linalg.eigvalsh(Q)
print(f"   quadratic form eigenvalues: {w}")
print(f"   signature: {(w>0).sum()}+ {(w<0).sum()}−  → SO(2,1)")
print()
print("the Killing form on sl(2,R) IS the Minkowski metric in 2+1.")
print("the light cone of that metric IS the parabolic locus.")
print()

# Δ under conjugation and composition
print("=" * 70)
print()
rng = np.random.default_rng(0)
def rand_sl2():
    while True:
        m = rng.normal(0, 1, (2, 2))
        dt = np.linalg.det(m)
        if dt > 1e-3:                    # need det = +1, not -1
            return m / np.sqrt(dt)

A_ = rand_sl2(); B_ = rand_sl2(); G = rand_sl2()
print("invariance:")
print(f"   Δ(A)            = {delta(A_):+.9f}")
print(f"   Δ(G A G⁻¹)      = {delta(G@A_@np.linalg.inv(G)):+.9f}")
print(f"   Δ(A⁻¹)          = {delta(np.linalg.inv(A_)):+.9f}")
print()
print("not additive under composition:")
print(f"   Δ(A) + Δ(B)     = {delta(A_)+delta(B_):+.9f}")
print(f"   Δ(AB)           = {delta(A_@B_):+.9f}")
print(f"   Δ(BA)           = {delta(B_@A_):+.9f}")
print(f"   Δ(AB) − Δ(BA)   = {delta(A_@B_)-delta(B_@A_):+.3e}")
print()
print("tr(AB) = tr(BA) always ⇒ Δ(AB) = Δ(BA) always.")
print("the sector of a composition does not depend on order,")
print("even though the composition itself does.")
print()

# the trace identity
print("=" * 70)
print()
print("Fricke / trace identity for SL(2):")
print("   tr(AB) + tr(AB⁻¹) = tr(A)tr(B)")
lhs = np.trace(A_@B_) + np.trace(A_@np.linalg.inv(B_))
rhs = np.trace(A_)*np.trace(B_)
print(f"   lhs = {lhs:.12f}")
print(f"   rhs = {rhs:.12f}")
print(f"   diff = {abs(lhs-rhs):.3e}")
print()
print("so the pair (A,B) is determined up to conjugacy by")
print("   x = tr A,  y = tr B,  z = tr AB")
print("and the commutator trace is:")
K = A_@B_@np.linalg.inv(A_)@np.linalg.inv(B_)
xx, yy, zz = np.trace(A_), np.trace(B_), np.trace(A_@B_)
pred = xx**2 + yy**2 + zz**2 - xx*yy*zz - 2
print(f"   tr[A,B] = x²+y²+z²−xyz−2")
print(f"   computed = {np.trace(K):.12f}")
print(f"   formula  = {pred:.12f}")
print(f"   diff     = {abs(np.trace(K)-pred):.3e}")
print()
print("Δ([A,B]) = (x²+y²+z²−xyz−2)² − 4")
print("        = (x²+y²+z²−xyz)(x²+y²+z²−xyz−4)")
kappa = xx**2+yy**2+zz**2-xx*yy*zz
print(f"   κ = x²+y²+z²−xyz = {kappa:.9f}")
print(f"   κ(κ−4) = {kappa*(kappa-4):.9f}")
print(f"   Δ([A,B]) = {delta(K):.9f}")
print()
print("so the commutator is parabolic exactly when κ = 0 or κ = 4.")
print("two surfaces in trace space. nothing else.")
print()

# where are they
print("=" * 70)
print()
print("κ = 0 and κ = 4 in the (x,y,z) trace coordinates:")
print()
print(f"{'x':>6} {'y':>6} {'z':>8} {'κ':>10} {'κ−4':>10} {'Δ[A,B]':>12}")
print("-" * 56)
for xv, yv in [(2,2), (2,3), (3,3), (1,1), (0,0), (2.5,2.5)]:
    # solve κ=0 for z:  z² − xy·z + (x²+y²) = 0
    disc = (xv*yv)**2 - 4*(xv**2+yv**2)
    if disc >= 0:
        for sgn in (+1, -1):
            zv = (xv*yv + sgn*np.sqrt(disc))/2
            k = xv**2+yv**2+zv**2-xv*yv*zv
            print(f"{xv:6.2f} {yv:6.2f} {zv:8.4f} {k:10.6f} "
                  f"{k-4:10.6f} {k*(k-4):12.6e}")
    else:
        print(f"{xv:6.2f} {yv:6.2f} {'—':>8} {'no real z':>10}")
print()
print("κ = 0 ⇔ the commutator is the identity ⇔ A and B commute.")
print("κ = 4 ⇔ the commutator is −identity ⇔ the other parabolic.")
