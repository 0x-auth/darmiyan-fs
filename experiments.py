#!/usr/bin/env python3
"""Reproduce the darmiyan.fs findings. Needs: numpy, sympy.
   python3 experiments.py"""
import math, sympy as sp, numpy as np

x = sp.symbols('x')

def fixed_point_symmetry():
    print("1) Möbius rules: slopes at the two fixed points multiply to 1")
    a, b, c, d = sp.symbols('a b c d')
    f = (a*x + b)/(c*x + d); fps = sp.solve(sp.Eq(x, f), x); df = sp.diff(f, x)
    print("   general:", sp.simplify(df.subs(x, fps[0]) * df.subs(x, fps[1])))

def metallic_ladder():
    print("2) x -> n + 1/x as boosts:  v/c = n√(n²+4)/(n²+2),  γ = (n²+2)/2")
    for n in range(1, 6):
        m = (n + math.sqrt(n*n + 4)) / 2; eta = 2*math.log(m)
        print(f"   n={n}  v/c={math.tanh(eta):.6f}  γ={math.cosh(eta):.4f}  ticks/digit={math.log(10)/eta:.4f}")

def lorentz(A):
    basis = [np.eye(2), np.diag([1., -1.]), np.array([[0., 1.], [1., 0.]])]
    L = np.zeros((3, 3))
    for j, E in enumerate(basis):
        Y = A @ E @ A.T; L[:, j] = [(Y[0,0]+Y[1,1])/2, (Y[0,0]-Y[1,1])/2, Y[0,1]]
    return L / abs(np.linalg.det(A))

def boost(v):
    g = 1/math.sqrt(1 - v@v); n = v/np.linalg.norm(v); B = np.eye(3)
    B[0,0] = g; B[0,1:] = B[1:,0] = g*v; B[1:,1:] += (g-1)*np.outer(n, n); return B

def split(L):
    g = L[0,0]; v = L[1:,0]/g; return g, v, np.linalg.inv(boost(v)) @ L

def angle(R): return math.degrees(math.atan2(R[2,1], R[1,1]))

def composition():
    print("3) Composition: Einstein addition + Wigner rotation")
    M = lambda n: np.array([[n, 1.], [1., 0.]])
    G, S = lorentz(M(1)), lorentz(M(2))
    gG, vG, RG = split(G); gS, vS, RS = split(S)
    for lab, L, g1, v1, R1, v2 in [("gold·silver", S@G, gS, vS, RS, vG), ("silver·gold", G@S, gG, vG, RG, vS)]:
        g, _, R = split(L); pred = gS*gG*(1 + v1 @ (R1[1:,1:] @ v2))
        print(f"   {lab}: γ={g:.4f} Einstein={pred:.4f} rotation={angle(R):+.3f}°")
    gr, _, Rr = split(np.linalg.inv(boost(vS)) @ boost(vG))
    print(f"   gold relative to silver: γ={gr:.4f}  Wigner={angle(Rr):.3f}°")
    print(f"   G·G (collinear): γ={split(G@G)[0]:.4f}  (Einstein: 3.5)")
    print(f"   mirror in each rule: det(spatial) = {np.linalg.det(split(G)[2][1:,1:]):+.0f}")

if __name__ == "__main__":
    fixed_point_symmetry(); metallic_ladder(); composition()
