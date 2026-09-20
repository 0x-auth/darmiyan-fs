"""
κ = x² + y² + z² − xyz

Δ([A,B]) = κ(κ−4). Two parabolic surfaces: κ=0, κ=4.
Follow κ and see what it is.
"""

import numpy as np
import sympy as sp

x, y, z = sp.symbols('x y z', real=True)
kappa = x**2 + y**2 + z**2 - x*y*z

print("κ =", kappa)
print()

# --- Markov / Vieta structure
print("κ is quadratic in each variable separately:")
print("   in z:", sp.collect(sp.expand(kappa), z))
print()
print("fix x,y and κ. the two roots in z:")
zr = sp.solve(sp.Eq(kappa, sp.Symbol('k')), z)
for r in zr:
    print("   ", sp.simplify(r))
print("   sum  =", sp.simplify(zr[0] + zr[1]), "  (= xy)")
print("   prod =", sp.simplify(sp.expand(zr[0]*zr[1])))
print()
print("so z → xy − z maps a solution to a solution, keeping κ.")
print("this is the Vieta involution. it generates a group action")
print("on each level set of κ.")
print()

# --- the three involutions
print("three involutions, one per coordinate:")
print("   Vx: (x,y,z) → (yz−x, y, z)")
print("   Vy: (x,y,z) → (x, xz−y, z)")
print("   Vz: (x,y,z) → (x, y, xy−z)")
print()

def Vx(p): a,b,c = p; return (b*c-a, b, c)
def Vy(p): a,b,c = p; return (a, a*c-b, c)
def Vz(p): a,b,c = p; return (a, b, a*b-c)

def K(p): a,b,c = p; return a*a+b*b+c*c-a*b*c

print("check κ invariance numerically:")
rng = np.random.default_rng(1)
for _ in range(4):
    p = tuple(rng.normal(0,1,3))
    print(f"   κ={K(p):+.9f}  Vx→{K(Vx(p)):+.9f}  "
          f"Vy→{K(Vy(p)):+.9f}  Vz→{K(Vz(p)):+.9f}")
print()

# --- κ = 0 : the Markov-like surface
print("=" * 70)
print("κ = 0  →  x² + y² + z² = xyz")
print()
print("this is the Markov equation with the 3 dropped.")
print("Markov proper: x²+y²+z² = 3xyz, solutions 1,1,1 / 1,1,2 / ...")
print()
print("integer solutions of x²+y²+z² = xyz:")
sols = []
for a_ in range(1, 40):
    for b_ in range(a_, 40):
        for c_ in range(b_, 400):
            if a_*a_+b_*b_+c_*c_ == a_*b_*c_:
                sols.append((a_,b_,c_))
for s_ in sols[:12]:
    print("   ", s_, "  κ =", K(s_))
print()
print("generated from (3,3,3) by the Vieta moves:")
seed = (3,3,3)
seen = {seed}
frontier = [seed]
for _ in range(4):
    nf = []
    for p in frontier:
        for V in (Vx, Vy, Vz):
            q = tuple(sorted(V(p)))
            if q not in seen and all(v > 0 for v in q):
                seen.add(q); nf.append(q)
    frontier = nf
for q in sorted(seen)[:14]:
    print("   ", q, "  κ =", K(q))
print()
print("these are 3× the Markov triples. the tree is the same tree.")
print()

# --- κ = 4
print("=" * 70)
print("κ = 4  →  x² + y² + z² − xyz = 4")
print()
print("parametrise: x=2cos α, y=2cos β, z=2cos γ")
print("then κ=4 ⟺ α ± β ± γ = 0 mod 2π  (the reducible locus)")
print()
for al, be in [(0.3, 0.7), (1.1, 0.4), (2.0, 1.3)]:
    for sgn in (+1, -1):
        ga = al + sgn*be
        p = (2*np.cos(al), 2*np.cos(be), 2*np.cos(ga))
        print(f"   α={al:.2f} β={be:.2f} γ=α{'+' if sgn>0 else '−'}β"
              f"={ga:.2f}   κ = {K(p):.12f}")
print()
print("κ=4 is where the pair (A,B) has a common fixed point —")
print("reducible. both live in one Borel subgroup.")
print()

# --- sign of κ(κ-4) partitions the trace space
print("=" * 70)
print("Δ([A,B]) = κ(κ−4). sign:")
print()
print("   κ < 0        → Δ > 0   commutator is a BOOST")
print("   0 < κ < 4    → Δ < 0   commutator is a ROTATION")
print("   κ > 4        → Δ > 0   commutator is a BOOST")
print("   κ = 0 or 4   → Δ = 0   PARABOLIC")
print()
print("so the rotation sector is the strip 0 < κ < 4, bounded")
print("by the two parabolic surfaces. exactly what the s-sweep")
print("found: elliptic between the two lightlike points.")
print()
print(f"{'κ':>8} {'Δ=κ(κ−4)':>12} {'sector':>10}")
print("-" * 32)
for kv in (-2, -0.5, 0, 0.5, 2, 3.5, 4, 5, 9):
    d = kv*(kv-4)
    sec = "0" if abs(d)<1e-12 else ("BOOST" if d>0 else "ROTATION")
    print(f"{kv:8.2f} {d:12.4f} {sec:>10}")
print()

# --- the earlier s-sweep in kappa coordinates
print("=" * 70)
print("the conflict sweep, re-read in κ:")
print()
a_,b_,c_,d_ = 1.0, 1.0, 1.0, 0.0
print(f"{'s':>7} {'x=trA':>9} {'y=trB':>9} {'z=trAB':>10} "
      f"{'κ':>10} {'κ(κ−4)':>12}")
print("-" * 60)
for s_ in (0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0):
    Mp = np.array([[a_+s_, b_],[c_, d_]])
    Mm = np.array([[a_-s_, b_],[c_, d_]])
    # normalise to det +1 where possible
    dp, dm = np.linalg.det(Mp), np.linalg.det(Mm)
    if dp < 0 or dm < 0:
        Mp2, Mm2 = Mp/np.sqrt(abs(dp)), Mm/np.sqrt(abs(dm))
    else:
        Mp2, Mm2 = Mp/np.sqrt(dp), Mm/np.sqrt(dm)
    xv, yv = np.trace(Mp2), np.trace(Mm2)
    zv = np.trace(Mp2@Mm2)
    kv = xv*xv+yv*yv+zv*zv-xv*yv*zv
    print(f"{s_:7.2f} {xv:9.4f} {yv:9.4f} {zv:10.4f} "
          f"{kv:10.5f} {kv*(kv-4):12.5f}")
print()
print("(dets are negative here so these are GL not SL — the κ")
print(" formula needs det +1. shown for shape only.)")
