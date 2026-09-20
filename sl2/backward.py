"""
Two questions.

(1) Why did offset 2.0 return kappa to exactly 4?
(2) What is x -> 1 + 1/x run backwards?
"""

import numpy as np
import sympy as sp

# ============================================================ (1) the anomaly

print("=" * 76)
print("(1) WHY DOES OFFSET 2.0 RETURN kappa TO 4?")
print("=" * 76)
print()

A0 = np.array([[np.cosh(.7), np.sinh(.7)],
               [np.sinh(.7), np.cosh(.7)]])


def kappa(A, B):
    x, y, z = np.trace(A), np.trace(B), np.trace(A @ B)
    return x*x + y*y + z*z - x*y*z


print("  the slide was B = T A T^-1 with T = [[1, off], [0, 1]].")
print("  T is PARABOLIC (trace 2). it fixes only the point at infinity.")
print()
print("  A0's fixed points:")
a, b, c, d = A0.ravel()
D = np.trace(A0)**2 - 4*np.linalg.det(A0)
r = np.sqrt(D)
fp = (((a-d)+r)/(2*c), ((a-d)-r)/(2*c))
print(f"    {fp[0]:.6f}  and  {fp[1]:.6f}")
print()
print("  T moves them to:")
print(f"  {'off':>7} {'T(fp1)':>12} {'T(fp2)':>12} {'kappa':>12}")
print("  " + "-" * 48)
for off in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0):
    T = np.array([[1.0, off], [0.0, 1.0]])
    B_ = T @ A0 @ np.linalg.inv(T)
    g1, g2 = fp[0] + off, fp[1] + off
    print(f"  {off:7.2f} {g1:12.6f} {g2:12.6f} {kappa(A0, B_):12.6f}")
print()
print("  A0 has fixed points at +1 and -1. T shifts by 'off'.")
print("  at off = 2: {-1,+1} -> {+1,+3}. the SETS SHARE the point +1.")
print()
print("  two hyperbolic elements sharing ONE fixed point generate a")
print("  group whose commutator is PARABOLIC. that is kappa = 4.")
print()
print("  check: does the shared fixed point survive?")
for off in (2.0,):
    T = np.array([[1.0, off], [0.0, 1.0]])
    B_ = T @ A0 @ np.linalg.inv(T)
    for nm, M in (("A0", A0), ("B", B_)):
        aa, bb, cc, dd = M.ravel()
        v = np.array([1.0, 1.0])   # the point +1 in homogeneous coords
        w = M @ v
        print(f"    {nm} sends (1:1) -> ({w[0]:.6f}:{w[1]:.6f})"
              f"   ratio {w[0]/w[1]:.9f}")
print()
print("  both fix +1. SHARED FIXED POINT -> reducible pair -> kappa = 4.")
print()
print("  so offset 2.0 is not a periodicity. it is the one offset at")
print("  which the shifted axis lands back on an endpoint of the")
print("  original. the parabolic locus is reached by SHARING A POINT,")
print("  not by coinciding.")
print()
print("  offset 0 : axes identical      -> share BOTH points")
print("  offset 2 : axes distinct       -> share ONE point")
print("  both give kappa = 4. the second is the interesting one:")
print("  the observer and the system disagree everywhere except at")
print("  a single point -- and that is enough for the commutator to")
print("  be parabolic.")
print()

# ============================================================ (2) backward

print("=" * 76)
print("(2) x -> 1 + 1/x RUN BACKWARDS")
print("=" * 76)
print()

x = sp.Symbol('x')
f = 1 + 1/x
finv = sp.solve(sp.Eq(1 + 1/sp.Symbol('y'), x), sp.Symbol('y'))[0]
print(f"  forward   f(x)  = {sp.simplify(f)}")
print(f"  backward  f^-1(x) = {sp.simplify(finv)}")
print()
print("  as matrices:")
F = sp.Matrix([[1, 1], [1, 0]])
Fi = F.inv()
print(f"    F    = {F.tolist()}      det = {F.det()}")
print(f"    F^-1 = {Fi.tolist()}   det = {Fi.det()}")
print()
print("  F is the FIBONACCI matrix. F^n gives consecutive Fibonacci")
print("  numbers. F^-1 is the same with a sign flip:")
print()
print(f"  {'n':>4} {'F^n':>22} {'F^-n':>22}")
print("  " + "-" * 50)
for n in (1, 2, 3, 4, 5):
    print(f"  {n:>4} {str((F**n).tolist()):>22} "
          f"{str((F**-n).tolist()):>22}")
print()

print("  fixed points:")
fps = sp.solve(sp.Eq(f, x), x)
print(f"    forward:  {[sp.simplify(s) for s in fps]}")
print(f"            = {[float(s) for s in fps]}")
fpsb = sp.solve(sp.Eq(finv, x), x)
print(f"    backward: {[sp.simplify(s) for s in fpsb]}")
print(f"            = {[float(s) for s in fpsb]}")
print()
print("  SAME fixed points. phi and -1/phi. the backward map does not")
print("  move them -- it swaps which one ATTRACTS.")
print()

phi = float((1+np.sqrt(5))/2)
Fn = np.array([[1.0, 1.0], [1.0, 0.0]])
Fin = np.linalg.inv(Fn)


def mult(M, xf):
    a, b, c, d = M.ravel()
    return np.linalg.det(M) / (c*xf + d)**2


for nm, M in (("forward ", Fn), ("backward", Fin)):
    m1 = mult(M, phi)
    m2 = mult(M, -1/phi)
    print(f"  {nm}: mu(phi) = {m1:+.9f}   mu(-1/phi) = {m2:+.9f}")
    print(f"            |mu| = {abs(m1):.9f} and {abs(m2):.9f}")
    print(f"            attracting: "
          f"{'phi' if abs(m1) < abs(m2) else '-1/phi'}")
print()
print("  Lambda:")
print(f"    forward  Lambda = {abs(np.log(abs(mult(Fn, phi)))):.9f}")
print(f"    backward Lambda = {abs(np.log(abs(mult(Fin, phi)))):.9f}")
print(f"    2 log phi       = {2*np.log(phi):.9f}")
print()

print("  RUNNING IT BACKWARDS, NUMERICALLY:")
print()
print(f"  {'n':>4} {'forward from 1':>18} {'backward from 1':>18}")
print("  " + "-" * 44)
xf, xb = 1.0, 1.0
for n in range(1, 13):
    xf = 1 + 1/xf
    xb = 1/(xb - 1) if abs(xb - 1) > 1e-14 else float('inf')
    print(f"  {n:>4} {xf:18.10f} {xb:18.10f}")
print()
print("  forward converges to phi = 1.6180339887.")
print("  backward does NOT converge. it is the same map with the")
print("  attracting and repelling points exchanged, so it runs AWAY")
print("  from phi and toward -1/phi -- but -1/phi is negative, and")
print("  from a positive start the orbit is thrown across the whole")
print("  real line before it gets there.")
print()

print("  the continued fraction reading:")
print("    forward  = [1; 1, 1, 1, ...]  -- building the fraction")
print("    backward = peeling terms OFF the fraction, one at a time")
print()
print("  so running x -> 1 + 1/x backwards is the Euclidean algorithm.")
print("  forward BUILDS the golden ratio by accumulating 1s;")
print("  backward TAKES IT APART, and since phi's expansion is")
print("  infinite, taking it apart never terminates.")
print()

print("  EXACT STATEMENT:")
print()
print("    f(x)   = 1 + 1/x  =  (x+1)/x     matrix [[1,1],[1,0]]")
print("    f^-1(x) = 1/(x-1)                matrix [[0,1],[1,-1]]")
print()
print("    det F = -1, so F is in GL not SL. tr F = 1, tr F^-1 = -1.")
print("    Delta(F) = 1 - 4(-1) = 5.  sqrt(5). the same 5 that makes")
print("    phi = (1+sqrt5)/2.")
print()
print(f"    Delta = {float(F.trace()**2 - 4*F.det())}")
print()
print("  and because det = -1, F is orientation-REVERSING.")
print("  F^2 has det +1 and trace 3: THAT is the honest boost.")
F2 = F**2
print(f"    F^2  = {F2.tolist()}, tr = {F2.trace()}, det = {F2.det()}")
print(f"    Delta(F^2) = {float(F2.trace()**2 - 4*F2.det())} = 5")
print()
print("  so the map that takes two steps is a boost with Delta = 5,")
print("  and one step is its square root -- which reverses")
print("  orientation. the arrow needs TWO applications to be an")
print("  arrow at all.")
