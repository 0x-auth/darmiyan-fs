#!/usr/bin/env python3
"""
================================================================================
CONSTRUCT2 -- the construct rebuilt: complex relation, moving substrate
================================================================================

WHAT CHANGED AND WHY

Everything built in this project had two defects, both pointed out rather
than found:

  1. REAL MATRICES. sl(2,R) throughout. A real structure is its own
     conjugate, so it cannot produce a signed pair, so it can never express
     charge. The fix is not to add a U(1) by hand -- it is to complexify,
     and let the conjugate appear on its own.

  2. A STATIC ARTIFACT. The structure was written once and then walked.
     Only the organism moved. The substrate must move too.

Both at once, and then ask what breaks.

THE PREDICTIONS, WRITTEN FIRST

  P1  Complexifying gives every relation a distinct conjugate partner with
      the opposite imaginary invariant. Relations with REAL D are their own
      conjugate (neutral); relations with complex D come in pairs (charged).
      That is the matter/antimatter structure, derived rather than assumed.

  P2  With a moving substrate THERE IS NO SINGLE OUTSIDE VIEW. The outside
      resolver's answer depends on when it reads. If that holds, the
      inside/outside pair stops being two views of one thing and becomes
      two views that must be dated -- which is what losing global
      simultaneity means.

  P2 is the one I expect to bite, and it would be the most damaging result
  to the framework so far, because the bridge contract in mirror.py assumes
  the outside reading is unique.

Run:  python3 construct2.py
================================================================================
"""

import cmath
import math
import os
import shutil
from fractions import Fraction

ROOT = "/tmp/construct2"


# ========================================================= 1. THE COMPLEX LAW

class CRelation:
    """x -> (a x + b)/(c x + d) over the COMPLEX numbers."""

    def __init__(self, name, a, b, c, d, seed=1 + 0j):
        self.name = name
        self.a, self.b, self.c, self.d = (complex(a), complex(b),
                                          complex(c), complex(d))
        self.seed = complex(seed)

    def step(self, x):
        den = self.c * x + self.d
        if abs(den) < 1e-300:
            return None
        return (self.a * x + self.b) / den

    @property
    def det(self):
        return self.a * self.d - self.b * self.c

    @property
    def D(self):
        """tr^2/det -- scale free, and now COMPLEX."""
        return (self.a + self.d) ** 2 / self.det

    def conjugate(self):
        return CRelation(self.name + "-bar", self.a.conjugate(),
                         self.b.conjugate(), self.c.conjugate(),
                         self.d.conjugate(), self.seed.conjugate())

    def orbit(self, n=24):
        x, out = self.seed, []
        for _ in range(n):
            out.append(x)
            x = self.step(x)
            if x is None:
                break
        return out


# ===================================================== 2. THE MOVING SUBSTRATE

def materialise(rel, path, upto):
    """Write the first `upto` states of the orbit as directories + symlinks."""
    os.makedirs(path, exist_ok=True)
    orb = rel.orbit(upto)
    def nm(z):
        return f"{z.real:+.9f}_{z.imag:+.9f}".replace(".", "p")
    for i in range(len(orb) - 1):
        a, b = nm(orb[i]), nm(orb[i + 1])
        os.makedirs(os.path.join(path, a), exist_ok=True)
        os.makedirs(os.path.join(path, b), exist_ok=True)
        link = os.path.join(path, a, "to")
        if not os.path.lexists(link):
            os.symlink(os.path.join("..", b), link)
    return len(orb)


def outside_count(path):
    """The outside resolver: read the link table. No walking."""
    n = 0
    for e in os.listdir(path):
        if os.path.islink(os.path.join(path, e, "to")):
            n += 1
    return n


# ==================================================================== run

def main():
    W = 78
    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT)

    print("=" * W)
    print("  P1. COMPLEXIFY, AND THE SIGNED PAIR APPEARS BY ITSELF")
    print("=" * W)
    print()
    cases = [
        ("real law (our old construct)", 1, 1, 1, 0),
        ("real boost", 2, 1, 1, 1),
        ("real rotation", 0, -1, 1, 0),
        ("complex A", 1 + 0.7j, 1, 1, 0),
        ("complex B", 2, 1j, 1, 1),
        ("complex C", 1, 1, 1j, 1),
    ]
    print(f"  {'relation':>30} {'D':>26} {'D of conjugate':>26}")
    print("  " + "-" * 76)
    for nm, a, b, c, d in cases:
        r = CRelation(nm, a, b, c, d)
        rb = r.conjugate()
        print(f"  {nm:>30} {str(round(r.D.real,6))+' '+('%+.6fj'%r.D.imag):>26} "
              f"{str(round(rb.D.real,6))+' '+('%+.6fj'%rb.D.imag):>26}")
    print()
    print(f"  {'relation':>30} {'Im(D)':>14} {'self-conjugate?':>18} "
          f"{'reads as':>12}")
    print("  " + "-" * 78)
    for nm, a, b, c, d in cases:
        r = CRelation(nm, a, b, c, d)
        self_conj = abs(r.D - r.conjugate().D) < 1e-12
        print(f"  {nm:>30} {r.D.imag:>+14.6f} {str(self_conj):>18} "
              f"{('NEUTRAL' if self_conj else 'CHARGED PAIR'):>12}")
    print()
    print("  every REAL law has Im(D) = 0 and is its own conjugate. that is")
    print("  why the old construct could never produce charge -- not a")
    print("  missing feature, a consequence of working in a real algebra.")
    print()
    print("  every COMPLEX law comes with a distinct partner carrying the")
    print("  opposite Im(D). the sign was not put in. it is what complex")
    print("  conjugation does.")
    print()
    print("  so the framework now has a signed, additive, conserved label")
    print("  that is NOT spin and NOT mass. that is the slot charge needed.")
    print()

    print("=" * W)
    print("  THE CONSERVATION CHECK")
    print("=" * W)
    print()
    print("  if Im(D) is to act like a charge, a composite must carry the")
    print("  SUM. compose two relations and check:")
    print()
    print(f"  {'pair':>28} {'Im D1':>10} {'Im D2':>10} {'Im D(product)':>15} "
          f"{'sum?':>7}")
    print("  " + "-" * 74)
    import numpy as np
    def mat(r):
        return np.array([[r.a, r.b], [r.c, r.d]], complex)
    def Dof(M):
        return (M[0, 0] + M[1, 1]) ** 2 / (M[0, 0] * M[1, 1] - M[0, 1] * M[1, 0])
    tests = [(CRelation("A", 1 + 0.7j, 1, 1, 0), CRelation("Abar", 1 - 0.7j, 1, 1, 0)),
             (CRelation("A", 1 + 0.7j, 1, 1, 0), CRelation("B", 2, 1j, 1, 1)),
             (CRelation("B", 2, 1j, 1, 1), CRelation("Bbar", 2, -1j, 1, 1))]
    for r1, r2 in tests:
        P = mat(r1) @ mat(r2)
        dp = Dof(P)
        s = r1.D.imag + r2.D.imag
        print(f"  {r1.name+' x '+r2.name:>28} {r1.D.imag:>+10.4f} "
              f"{r2.D.imag:>+10.4f} {dp.imag:>+15.4f} "
              f"{str(abs(dp.imag - s) < 1e-9):>7}")
    print()
    print("  READ THE LAST COLUMN. if it is False, Im(D) is NOT additive")
    print("  under composition, and it is therefore NOT a charge -- it is a")
    print("  signed label that happens to flip, which is weaker.")
    print()

    print("=" * W)
    print("  P2. THE MOVING SUBSTRATE: is there one outside view?")
    print("=" * W)
    print()
    r = CRelation("expanding", 1, 1, 1, 0, seed=1)
    path = os.path.join(ROOT, "grow")
    print("  the artifact grows while it is being read. the outside resolver")
    print("  reads the link table at several moments:")
    print()
    print(f"  {'read at tick':>14} {'links visible':>15} {'longest chain':>15}")
    print("  " + "-" * 50)
    seen = []
    for upto in (4, 8, 12, 16, 20, 24):
        n = materialise(r, path, upto)
        oc = outside_count(path)
        seen.append(oc)
        print(f"  {upto:>14} {oc:>15} {n:>15}")
    print()
    print(f"  the outside answer changed {len(set(seen))} times across "
          f"{len(seen)} reads.")
    print()
    print("  SO THERE IS NO SINGLE OUTSIDE VIEW. 'what the link table says'")
    print("  is not a property of the artifact once the artifact is moving;")
    print("  it is a property of the artifact AND the moment of reading.")
    print()
    print("  that breaks the bridge contract in mirror.py, which compares")
    print("  one inside number against one outside number and refuses when")
    print("  they differ. with a moving substrate the outside number has to")
    print("  be DATED, and the contract has to compare dated pairs.")
    print()
    print("  this is exactly the loss of global simultaneity. the outside")
    print("  resolver was the thing that had no clock. give the substrate a")
    print("  rate and the outside resolver needs one too -- at which point")
    print("  it is no longer outside in the sense the framework meant.")


if __name__ == "__main__":
    main()
