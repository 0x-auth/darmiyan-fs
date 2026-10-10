#!/usr/bin/env python3
"""
================================================================================
EXPANDING -- when the substrate stretches while the walker walks
================================================================================

EVERYTHING BUILT SO FAR HAD A STATIC ARTIFACT

darmiyan.py, manifold.py, mirror.py: the structure is written once, then
walked. Only the walker moves. That is the whole construct's blind spot, and
it is exactly the thing cosmology is about -- space stretches between things
rather than things moving through space.

So: let the chain grow while the walk is in progress, and see what happens.

THE THREE REAL LIMITS, MEASURED

  NAME_MAX     bytes in one path component
  PATH_MAX     bytes in a whole path
  SYMLOOP_MAX  symlink resolutions in one lookup

Three independent ceilings on how far a single lookup can reach. Only the
third has been used in this work; the other two bound a different axis.

THE PREDICTION, BEFORE RUNNING

  Metric expansion inserts new nodes in proportion to the separation, so
  the distance D to the target obeys

        dD/dt = H*D - 1          (stretch adds H*D, the step removes 1)

  which has a fixed point at D = 1/H. Start closer and the walker arrives.
  Start further and D grows without bound and it never arrives.

  If that comes out, the construct has produced a HUBBLE RADIUS from
  nothing but insertion rate -- an event horizon that is not a fixed point
  of a map, which is the first horizon in this work that is not.

  And with decelerating expansion H(t) = H0/t, the integral of H converges
  differently and there should be NO permanent horizon: everything arrives
  eventually. That is the matter-dominated case, and it is the control.

Run:  python3 expanding.py
================================================================================
"""

import math
import os
import shutil
import subprocess

ROOT = "/tmp/expanding"


# ======================================================= the three ceilings

def measure_limits():
    out = {}
    for nm in ("NAME_MAX", "PATH_MAX", "SYMLOOP_MAX"):
        try:
            out[nm] = os.pathconf("/tmp", "PC_" + nm)
        except (OSError, ValueError, KeyError):
            out[nm] = None
    # measure SYMLOOP directly, since pathconf often lies about it
    base = os.path.join(ROOT, "loop")
    os.makedirs(base, exist_ok=True)
    link = os.path.join(base, "s")
    if not os.path.lexists(link):
        os.symlink(".", link)
    depth = None
    for d in range(1, 80):
        try:
            os.stat(os.path.join(base, *(["s"] * d)))
        except OSError:
            depth = d - 1
            break
    out["SYMLOOP measured"] = depth
    # measure NAME_MAX directly
    n = 1
    while n < 600:
        try:
            p = os.path.join(ROOT, "x" * n)
            os.mkdir(p)
            os.rmdir(p)
            n += 1
        except OSError:
            break
    out["NAME_MAX measured"] = n - 1
    return out


# ================================================= the expanding substrate

def walk_expanding(D0, H, ticks=4000, decelerating=False):
    """
    D = number of nodes between the walker and the target.

    Each tick:
      - the walker advances one node          D -= 1
      - the substrate stretches               D += H(t) * D

    Nodes are inserted IN PROPORTION to the current separation. That is what
    metric expansion means: not motion, insertion between.

    Returns (arrived, ticks_taken, D_history).
    """
    D = float(D0)
    hist = [D]
    for t in range(1, ticks + 1):
        Ht = (H / t) if decelerating else H
        D = D - 1.0 + Ht * D
        hist.append(D)
        if D <= 0:
            return True, t, hist
        if D > 1e9:
            return False, t, hist
    return False, ticks, hist


def main():
    W = 78
    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT)

    print("=" * W)
    print("  1. THE THREE CEILINGS, MEASURED ON THIS MACHINE")
    print("=" * W)
    print()
    lim = measure_limits()
    for k, v in lim.items():
        print(f"  {k:>22} = {v}")
    print()
    nm = lim.get("NAME_MAX measured") or 255
    pm = lim.get("PATH_MAX") or 4096
    sl = lim.get("SYMLOOP measured") or 40
    print(f"  so one lookup is bounded three separate ways:")
    print(f"    at most {nm} bytes in a component")
    print(f"    at most {pm} bytes in the whole path")
    print(f"    at most {sl} symlink resolutions")
    print()
    print(f"  the path bound alone allows ~{pm // 2} components of one byte.")
    print(f"  the symlink bound allows {sl}. so which ceiling you hit depends")
    print(f"  on whether your structure is made of names or of references --")
    print(f"  {pm // 2 // sl}x apart. only the symlink one has been used so far.")
    print()

    print("=" * W)
    print("  2. STATIC SUBSTRATE: the walker always arrives")
    print("=" * W)
    print()
    print(f"  {'D0':>8} {'H':>8} {'arrived':>9} {'ticks':>8}")
    print("  " + "-" * 36)
    for D0 in (10, 100, 1000):
        a, t, _ = walk_expanding(D0, 0.0)
        print(f"  {D0:>8} {0.0:>8.4f} {str(a):>9} {t:>8}")
    print()
    print("  with no expansion, distance falls by exactly 1 per tick. this is")
    print("  every artifact built in this project until now.")
    print()

    print("=" * W)
    print("  3. EXPANDING SUBSTRATE: a horizon appears at D = 1/H")
    print("=" * W)
    print()
    print(f"  {'H':>10} {'predicted 1/H':>15} {'last D0 that':>14} "
          f"{'first D0 that':>15}")
    print(f"  {'':>10} {'':>15} {'arrives':>14} {'never does':>15}")
    print("  " + "-" * 60)
    for H in (0.2, 0.1, 0.05, 0.02, 0.01, 0.005):
        lastok, firstbad = None, None
        for D0 in range(1, int(4 / H)):
            a, _, _ = walk_expanding(D0, H, ticks=20000)
            if a:
                lastok = D0
            elif firstbad is None:
                firstbad = D0
                break
        print(f"  {H:>10.4f} {1/H:>15.2f} {str(lastok):>14} "
              f"{str(firstbad):>15}")
    print()
    print("  the boundary sits exactly at 1/H, every time. that is a HUBBLE")
    print("  RADIUS, produced by nothing but an insertion rate.")
    print()
    print("  and note what kind of horizon it is NOT. every previous horizon")
    print("  in this project was a fixed point of a map -- the walker stops")
    print("  because the relation stops. here the relation never stops and")
    print("  the walker never stops; the SUBSTRATE outruns it. that is a new")
    print("  failure mode and the construct could not express it before.")
    print()

    print("=" * W)
    print("  4. THE CONTROL: decelerating expansion has no permanent horizon")
    print("=" * W)
    print()
    print("  H(t) = H0/t -- expansion that slows. matter-dominated.")
    print()
    print(f"  {'H0':>8} {'D0':>8} {'constant H':>14} {'decelerating':>15}")
    print("  " + "-" * 50)
    for H0 in (0.1, 0.05):
        for D0 in (5, 20, 60, 200):
            a1, _, _ = walk_expanding(D0, H0, ticks=50000)
            a2, _, _ = walk_expanding(D0, H0, ticks=50000, decelerating=True)
            print(f"  {H0:>8.3f} {D0:>8} {str(a1):>14} {str(a2):>15}")
    print()
    print("  decelerating expansion lets everything arrive eventually. the")
    print("  horizon in part 3 needs expansion that does NOT slow down.")
    print("  that is the same statement as: an event horizon requires")
    print("  Lambda > 0. the control separates the two cases cleanly.")
    print()

    print("=" * W)
    print("  5. AGAINST THE REAL NUMBERS")
    print("=" * W)
    print()
    c = 2.99792458e8
    Mpc = 3.0857e22
    Gly = 9.4607e24
    H0 = 67.4 * 1000 / Mpc
    print(f"  in the model:   horizon at D = 1/H nodes, H in nodes per tick")
    print(f"  in the sky:     horizon at R = c/H0")
    print()
    print(f"  c/H0 = {c/H0/Gly:.2f} Gly   (Hubble radius)")
    print(f"  measured here: boundary at exactly 1/H, to the node")
    print()
    print("  same equation. in the model one tick moves one node, so c = 1")
    print("  by construction and the horizon is 1/H. in the sky c is the")
    print("  local step rate and the horizon is c/H. the construct did not")
    print("  need to be told about light cones to produce one.")
    print()
    print("  WHAT THIS DOES NOT DO: it gives the horizon's FORM and not its")
    print("  SIZE. H is an input here. in the sky H0 is measured. nothing")
    print("  internal fixes it -- the missing unit, eleventh appearance.")


if __name__ == "__main__":
    main()
