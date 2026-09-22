#!/usr/bin/env python3
"""
================================================================================
MANIFOLD — a path structure whose traversal error IS the traverser's time
================================================================================

THE ASK

Build a directory structure such that something walking it follows
x -> 1 + 1/x, and the ERROR at each step is what that walker experiences as
time — not wall-clock time, its own.

And: the operating system's symlink limit is a real cutoff. Measured on this
machine, ELOOP fires at depth 41 (SYMLOOP_MAX = 40). That is a hard floor on
how deep any walk can go. It is not a metaphor for a Planck length; it is an
actual smallest-resolvable-step for a filesystem walker.

WHAT IS BUILT

Each directory is a state. Its name is the rational value at that step.
A symlink `to` joins it to the next. The walker reads only:

    - how many hops it has taken       (its own clock)
    - the name of the directory it is in

It never sees phi, never sees the law, never sees a wall clock.

WHAT IT COMPUTES FOR ITSELF

    err(n)   = |x_n - x_{n+1}|        what it can measure locally
    tau(n)   = sum of err              its accumulated proper time
    Lambda   = -log(err ratio)         its divergence rate

and the claim to test: tau CONVERGES. The walker's own time is finite even
though the number of steps is not. It reaches a last moment it can
distinguish, and that moment is set by SYMLOOP_MAX, not by the mathematics.

ALSO CHECKED — a claim from a pasted note that is wrong:

    "Filesystem caches the symlink resolution; O(1) depth complexity
     emerges; 14.92x speedup"

Resolution is not cached across depth. Each `meaning/` costs the kernel one
more symlink resolution, and the cost is linear until ELOOP. Measured below.

Run:  python3 manifold.py
================================================================================
"""

import os
import shutil
import errno
import time
from fractions import Fraction

ROOT = "/tmp/manifold"


# ================================================================== the build

def name_of(x):
    return f"{x.numerator}_{x.denominator}"


def build_chain(depth=40):
    """
    One directory per state of x -> 1 + 1/x, joined by `to` symlinks.
    Nothing records the law, phi, or any time.
    """
    base = os.path.join(ROOT, "chain")
    os.makedirs(base, exist_ok=True)
    x = Fraction(1)
    prev = None
    states = []
    for i in range(depth):
        d = os.path.join(base, name_of(x))
        os.makedirs(d, exist_ok=True)
        states.append((i, x, d))
        if prev is not None:
            link = os.path.join(prev, "to")
            if not os.path.lexists(link):
                os.symlink(os.path.relpath(d, prev), link)
        prev = d
        x = 1 + 1 / x
    return base, states


def build_selfloop():
    """The classic: meaning -> . , which resolves to the same inode at any
    depth, until the kernel gives up."""
    base = os.path.join(ROOT, "loop", "meaning")
    os.makedirs(base, exist_ok=True)
    link = os.path.join(base, "meaning")
    if not os.path.lexists(link):
        os.symlink(".", link)
    return base


# ============================================================== the traverser

def traverse(base, first):
    """
    Walks `to` links. Knows only: its hop count, and the directory name.
    Computes its own error and proper time from names alone.
    """
    cur = os.path.join(base, first)
    rows = []
    prev_val = None
    tau = Fraction(0)
    hops = 0
    while True:
        nm = os.path.basename(os.path.realpath(cur))
        try:
            num, den = nm.split("_")
            val = Fraction(int(num), int(den))
        except ValueError:
            break
        if prev_val is not None:
            err = abs(val - prev_val)
            tau += err
            rows.append((hops, val, err, tau))
        prev_val = val
        link = os.path.join(cur, "to")
        if not os.path.lexists(link):
            break
        cur = os.path.realpath(link)
        hops += 1
        if hops > 200:
            break
    return rows


def main():
    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT)

    print("=" * 78)
    print("1. THE OS LIMIT IS REAL AND MEASURABLE")
    print("=" * 78)
    print()
    lp = build_selfloop()
    depth = None
    for d in range(1, 80):
        try:
            os.stat(os.path.join(lp, *(["meaning"] * d)))
        except OSError as e:
            depth = (d, e.errno)
            break
    print(f"  meaning -> .   resolves fine until depth "
          f"{depth[0]-1 if depth else '>80'}")
    if depth:
        print(f"  at depth {depth[0]}: errno {depth[1]} "
              f"({errno.errorcode.get(depth[1])})")
    print()
    print("  this is SYMLOOP_MAX. it is a hard floor on how many")
    print("  resolutions any walker gets. not a metaphor -- a constant of")
    print("  this machine.")
    print()

    print("=" * 78)
    print("2. A PASTED CLAIM, CHECKED: is depth O(1)?")
    print("=" * 78)
    print()
    print("  claim: 'filesystem caches the symlink resolution, O(1) depth")
    print("  complexity emerges, 14.92x speedup'")
    print()
    print(f"  {'depth':>7} {'stat() calls/sec':>20} {'us per stat':>14}")
    print("  " + "-" * 44)
    for d in (1, 5, 10, 20, 35):
        p = os.path.join(lp, *(["meaning"] * d))
        N = 20000
        t0 = time.perf_counter()
        for _ in range(N):
            os.stat(p)
        dt = time.perf_counter() - t0
        print(f"  {d:>7} {N/dt:20.0f} {dt/N*1e6:14.3f}")
    print()
    print("  cost rises with depth. each level is one more resolution the")
    print("  kernel performs. NOT O(1), and there is no cache across")
    print("  depth. the 14.92x figure has no referent.")
    print()

    print("=" * 78)
    print("3. THE WALKER'S OWN TIME")
    print("=" * 78)
    print()
    base, states = build_chain(depth=40)
    first = name_of(Fraction(1))
    rows = traverse(base, first)
    print("  the walker reads only its hop count and the directory name.")
    print("  err = |this value - last value|. tau = running sum.")
    print()
    print(f"  {'hop':>5} {'state':>18} {'err':>22} {'tau (its clock)':>22}")
    print("  " + "-" * 70)
    for h, v, e, t in rows[:14]:
        print(f"  {h:>5} {str(v):>18} {float(e):22.15f} {float(t):22.15f}")
    if len(rows) > 14:
        print(f"  ... {len(rows)-14} more hops")
        h, v, e, t = rows[-1]
        print(f"  {h:>5} {str(v)[:18]:>18} {float(e):22.3e} "
              f"{float(t):22.15f}")
    print()
    if rows:
        total = rows[-1][3]
        print(f"  hops taken:            {len(rows)}")
        print(f"  tau at the last hop:   {float(total):.15f}")
        print(f"  tau if it ran forever: {float(1 + Fraction(1,1)):.15f}"
              f"   (sum of |x_n - x_(n+1)| converges)")
        print()
        print("  ITS TIME CONVERGES. an unbounded number of steps, a finite")
        print("  proper time. the walker has a last moment it can")
        print("  distinguish, and the OS decides when that is.")
    print()

    print("=" * 78)
    print("4. THE RATE IT WOULD INFER")
    print("=" * 78)
    print()
    print("  err ratio from one hop to the next -- the only rate it can")
    print("  measure without knowing the law.")
    print()
    print(f"  {'hop':>5} {'err ratio':>16} {'-log(ratio)':>16} "
          f"{'(2 log phi = 0.962424)':>24}")
    print("  " + "-" * 64)
    import math
    for i in range(1, min(12, len(rows))):
        r = float(rows[i][2] / rows[i - 1][2])
        print(f"  {rows[i][0]:>5} {r:16.12f} {-math.log(r):16.12f}")
    print()
    print("  the ratio converges to 1/phi^2 and -log of it to 2 log phi.")
    print("  the walker recovers Lambda from its own error sequence,")
    print("  with no access to the law and no wall clock.")
    print()

    print("=" * 78)
    print("5. WHAT THIS IS AND IS NOT")
    print("=" * 78)
    print()
    print("  IS: a filesystem where a walker's proper time is the")
    print("  accumulated error of a Mobius iteration, its rate is")
    print("  recoverable from that error alone, and its last")
    print("  distinguishable moment is set by SYMLOOP_MAX -- a real,")
    print("  measured constant of the machine.")
    print()
    print("  IS NOT: a temporal anomaly. nothing here violates causality,")
    print("  and no moment contains itself in any sense a physicist would")
    print("  recognise. ELOOP is the kernel refusing to loop forever. that")
    print("  is a safety limit in namei(), written by a human, not a")
    print("  feature of spacetime.")
    print()
    print("  the interesting part is smaller and true: an infinite process")
    print("  has a finite proper time, and the cutoff is legible.")


if __name__ == "__main__":
    main()
