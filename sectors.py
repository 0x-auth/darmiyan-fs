#!/usr/bin/env python3
"""sectors.py — one Möbius family, three physics, three laws of emergent time.
f_t(x) = t - 1/x  (det 1). |t| > 2 hyperbolic (boost), |t| < 2 elliptic (rotation),
t = 2 parabolic (null / lightlike). Carried over from self-referential-seed's
filesystem-model (UNIVERSE.md, map.py), including its involution C(x) = 1 - x.
    python3 sectors.py
"""
import math
from decimal import Decimal as D, getcontext

PHI, PSI = (1 + 5**.5) / 2, (1 - 5**.5) / 2
f = lambda x: 1 + 1/x          # forward
g = lambda x: 1/(x - 1)        # exact inverse
C = lambda x: 1 - x            # swaps phi <-> psi  (phi + psi = 1)
R = lambda x: -1/x             # swaps phi <-> psi  (phi * psi = -1), fixed points ±i

def mirrors():
    print("1) two different mirrors, one identity  X∘f∘X = f⁻¹")
    for name, X in (("C(x)=1-x", C), ("R(x)=-1/x", R)):
        err = max(abs(X(f(X(x))) - g(x)) for x in (0.3, 2.7, -4.1, 7.9))
        print(f"   {name:10} max |X f X - f⁻¹| = {err:.1e}")

def closure(t, digits, cap=60000):
    """darmiyan.fs rule: tick until |f(x)-x| < ε, or a state recurs (content recognition)."""
    getcontext().prec = digits; eps = D(10) ** -(digits - 1)
    x = D(3); seen = {str(x): 0}
    for n in range(1, cap):
        fx = +(D(t) - 1/x)
        if abs(fx - x) < eps: return f"{n-1} closes"
        if str(fx) in seen: return f"cycle {n - seen[str(fx)]}"
        seen[str(fx)] = n; x = fx
    return f">{cap}"

def sector(t):
    if t > 2:  return "hyperbolic", f"boost γ={(t*t-2)/2:.3f}"
    if t == 2: return "parabolic", "null (lightlike)"
    return "elliptic", f"rotation {math.degrees(2*math.acos(t/2)):.1f}°"

def classify(s):  # identical to self-referential-seed/organism.py
    if 10000 not in s or 100000 not in s: return "?"
    a, b = s[10000], s[100000]
    if a < 1e-12: return "shunya (T = 0)"
    r = b / a
    return "settled" if r < 1.05 else "drifting (~log n)" if r < 3 else "unresolved (~linear)"

def fate(t):
    fp = (t + math.sqrt(t*t - 4)) / 2 if t >= 2 else None
    x = prev = 3.0; T = 0.0; s = {}
    for n in range(1, 100001):
        x = t - 1/x
        T += abs(x - fp) if fp is not None else abs(x - prev)
        prev = x
        if n in (10000, 100000): s[n] = T
    return classify(s)

if __name__ == "__main__":
    mirrors()
    print("\n2) ticks to closure (darmiyan.fs rule) and organism fate (organism.py classifier)")
    print(f"   {'t':>6} {'sector':>11} {'Lorentz':>18} | {'ε=1e-8':>12} {'ε=1e-16':>12} {'ε=1e-32':>12} | fate")
    for t in (2.5, 2.1, 2.01, 2.0, 1.0, 0.0, 2*math.cos(1.0)):
        s, l = sector(t)
        c = [closure(t, d) for d in (8, 16, 32)] if t != 2.0 else [closure(2, 8), "~1e8 (ε^-½)", "~1e16"]
        print(f"   {t:>6.3f} {s:>11} {l:>18} | {c[0]:>12} {c[1]:>12} {c[2]:>12} | {fate(t)}")
    print("\n   boosts: ticks ∝ log(1/ε)      -> settled, arrowed time")
    print("   light:  ticks ∝ ε^(-1/2)      -> drifting, the seam")
    print("   rotations: no closure         -> cyclic or never-repeating, no arrow")
