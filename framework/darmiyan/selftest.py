"""
The framework's own test, runnable from the image: `darmiyan verify`.

It checks three things, in order of how much they matter:

  1. the bridge AGREES where it should     (known relations)
  2. the bridge REFUSES where it must      (a deliberately corrupted artifact)
  3. the invariant is independent of scale (k*M gives the same D)

Test 2 is the one that matters. A contract that never fires is decoration.
"""

from __future__ import annotations

import os

from .bridge import BridgeViolation, read
from .inside import Inside
from .outside import Outside
from .relation import Relation
from . import substrate as sub_mod


def verify() -> int:
    W = 78
    fails = 0
    print("\n" + "=" * W)
    print("  1. THE BRIDGE AGREES WHERE IT SHOULD")
    print("=" * W + "\n")
    print(f"  {'relation':>12} {'D in':>12} {'D out':>12} {'truth':>12} {'ok':>5}")
    print("  " + "-" * 60)
    for nm, (a, b, c, d, s) in {
        "golden":  (1, 1, 1, 0, 1),
        "boost":   (2, 1, 1, 1, 1),
        "boost3":  (3, 1, 1, 0, 1),
        "shift":   (1, 1, 0, 1, 0),
    }.items():
        rel = Relation(name=nm, a=a, b=b, c=c, d=d, seed=s)
        r = read(rel)
        t = rel.truth()
        ok = r.agreement in ("exact", "close")
        fails += 0 if ok else 1
        print(f"  {nm:>12} {r.d_inside:>12.6f} {r.d_outside:>12.6f} "
              f"{t:>12.4f} {str(ok):>5}")

    print("\n" + "=" * W)
    print("  2. THE BRIDGE REFUSES WHERE IT MUST")
    print("=" * W + "\n")
    print("  splice a second law onto the tail of an artifact, so the")
    print("  structure no longer encodes ONE Mobius relation. each resolver")
    print("  then sees a different law -- which one lands where depends on")
    print("  directory ordering and does not matter. what matters is that")
    print("  they disagree, and that the framework returns nothing.\n")
    # build law A, then splice law B onto its tail. Outside solves from the
    # first three nodes and sees A. Inside walks to the end and measures B.
    A = Relation(name="corrupt", a=1, b=1, c=1, d=0, seed=1, steps=10)
    path = A.materialise()
    x = list(A.orbit())[-1]
    B = Relation(name="corrupt", a=3, b=1, c=1, d=0, seed=x, steps=20,
                 root=A.root)
    B.materialise(clean=False)          # same directory, different tail law
    print(f"    spliced law (3x+1)/x onto the tail of (x+1)/x at {x}")
    try:
        read(A, materialise=False)
        print("\n    NO REFUSAL. the contract did not fire.")
        print("    this is a FAILURE of the framework, not of the artifact.")
        fails += 1
    except BridgeViolation as e:
        print(f"\n    refused: {e}\n")
        print("    correct. no number was returned.")

    print("\n" + "=" * W)
    print("  3. THE INVARIANT IS SCALE-FREE")
    print("=" * W + "\n")
    print("  D = tr^2/det must not change when the matrix is multiplied by")
    print("  a constant. Delta = tr^2 - 4det would.\n")
    print(f"  {'k':>4} {'D outside':>14} {'Delta':>14}")
    print("  " + "-" * 36)
    base = None
    for k in (1, 2, 3, 5):
        rel = Relation(name=f"scale{k}", a=2 * k, b=1 * k, c=1 * k, d=1 * k,
                       seed=1)
        rel.materialise()
        d = Outside(rel.path).invariant()
        a_, b_, c_, d_ = 2 * k, k, k, k
        delta = (a_ + d_) ** 2 - 4 * (a_ * d_ - b_ * c_)
        print(f"  {k:>4} {d:>14.9f} {delta:>14}")
        if base is None:
            base = d
        elif abs(d - base) > 1e-9:
            fails += 1

    print("\n" + "=" * W)
    print("  4. THE MOVING SUBSTRATE (1.1.0)")
    print("=" * W + "\n")
    print("  the floor D* = h^(1/(p-1)) must be where the walk actually")
    print("  settles, and the stability criterion D* > (p-1)/2 must predict")
    print("  whether it settles at all.\n")
    print(f"  {'p':>6} {'h':>9} {'D* predicted':>14} {'D measured':>14} "
          f"{'pred':>8} {'obs':>8} {'ok':>4}")
    print("  " + "-" * 68)
    for p_, h_ in ((2.0, 10.0), (3.0, 10.0), (6.0, 1e4), (6.0, 10.0),
                   (4.0 / 3.0, 2.0)):
        ds = sub_mod.floor_of(p=p_, h=h_)
        stable = sub_mod.floor_is_stable(p=p_, h=h_)
        relax = sub_mod.relaxation(p=p_, h=h_)
        tk = int(min(3e6, max(6e4, 80 * relax))) if stable else 60000
        o = sub_mod.walk(1000.0, h_, p_, ticks=tk)
        settled = abs(o.final_D - ds) < 1e-6
        ok = (settled == bool(stable))
        if not ok:
            fails += 1
        print(f"  {p_:>6.3f} {h_:>9.1f} {ds:>14.6f} {o.final_D:>14.6f} "
              f"{str(bool(stable)):>8} {str(settled):>8} "
              f"{('ok' if ok else 'FAIL'):>4}")
    print()
    print("  and the p = 0 horizon must land on 1/h exactly:\n")
    print(f"  {'h':>8} {'1/h':>9} {'first escapes':>15} {'ok':>5}")
    print("  " + "-" * 42)
    for h_ in (0.2, 0.1, 0.05):
        firstbad = None
        for D0 in range(1, int(4 / h_)):
            if sub_mod.walk(D0, h_, 0.0, ticks=20000).outcome != "arrives":
                firstbad = D0
                break
        ok = firstbad is not None and abs(firstbad - round(1 / h_)) <= 1
        if not ok:
            fails += 1
        print(f"  {h_:>8.3f} {1/h_:>9.2f} {str(firstbad):>15} "
              f"{('ok' if ok else 'FAIL'):>5}")


    print()
    print("=" * W)
    print(f"  failures: {fails}")
    print("=" * W + "\n")
    return 1 if fails else 0
