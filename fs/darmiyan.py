#!/usr/bin/env python3
"""
================================================================================
DARMIYAN — three sectors, told apart by how a walk fails
================================================================================

THE OBSERVATION THIS IS BUILT ON

    meaning -> meaning

A symlink whose target is its own name. The link is well formed, the entry
exists, and `ls` shows it. But:

    $ realpath meaning
    realpath: meaning: Too many levels of symbolic links      (ELOOP, errno 40)

The filesystem reports UNDEFINED. Nothing is broken. What fails is the
attempt to terminate a walk on a fixed point.

And a two-cycle does the same thing:

    a -> b
    b -> a
    $ realpath a          ->  ELOOP

So the OS gives the same error for a fixed point and for a cycle. From the
walker's side, order 1 and order 2 are indistinguishable: both are
"undefined".

THE THREE SECTORS, AS FILESYSTEM BEHAVIOUR

A Mobius relation x -> (ax+b)/(cx+d) has three kinds, set by
Delta = tr^2 - 4det. Built as symlinks, each kind fails differently:

    PARABOLIC   the two fixed points merge     -> a SELF-LINK   -> ELOOP
    ROTATION    finite orbit, returns          -> a CYCLE       -> ELOOP
    BOOST       converges, never arrives       -> an OPEN CHAIN -> no error,
                                                                   no end

That is the whole classification, and nothing in the filesystem states it.
The writer lays down links. The reader finds out by walking, and by reading.

WHAT EMERGES, NOT PUT IN
 1. which sector, from the shape of the failure
 2. that ELOOP conflates order 1 with order 2 -- a resolution limit, not a
    property of the relation
 3. that readlink never fails: the information was always present
 4. that "undefined" is a coordinate artifact -- the same way the
    Schwarzschild horizon is a coordinate singularity and r=0 is not

Run:  python3 darmiyan.py
================================================================================
"""

import os
import shutil
import errno
import subprocess
from fractions import Fraction

ROOT = "/tmp/darmiyan"


# ================================================================== WRITER

def mob(a, b, c, d, x):
    den = c * x + d
    return None if den == 0 else Fraction(a * x + b, den)


def nm(x):
    return "inf" if x is None else str(x).replace("/", "_over_")


def build(name, a, b, c, d, x0, steps=16):
    """
    One directory per visited value. Each holds a symlink `to` whose TARGET
    IS THE NEXT VALUE'S NAME, in the same directory. So:
        a fixed point   -> `to` points at its own directory name
        a cycle         -> `to` links chase each other round
        a chain         -> `to` walks forward and never closes
    All three are ordinary symlinks. None is labelled.
    """
    base = os.path.join(ROOT, name)
    os.makedirs(base, exist_ok=True)
    x = Fraction(x0)
    for _ in range(steps):
        here = nm(x)
        os.makedirs(os.path.join(base, here), exist_ok=True)
        nxt = mob(a, b, c, d, x)
        link = os.path.join(base, here + ".to")
        if not os.path.lexists(link):
            os.symlink(nm(nxt) + ".to" if nxt is not None else "inf.to", link)
        if nxt is None or nxt == x:
            break
        x = nxt
    return base


# ================================================================== READER

def probe(path):
    """What happens when the OS is asked to resolve this link."""
    try:
        os.path.realpath(path, strict=True)
        return "resolves"
    except OSError as e:
        if e.errno == errno.ELOOP:
            return "ELOOP (undefined)"
        if e.errno == errno.ENOENT:
            return "dangling"
        return f"errno {e.errno}"


def hop_count(base, start, limit=200):
    """Follow one hop at a time by READING links. Returns (hops, ending)."""
    seen = {}
    cur = start
    for i in range(limit):
        p = os.path.join(base, cur)
        if not os.path.lexists(p):
            return i, "dangling"
        tgt = os.readlink(p)
        if tgt == cur:
            return i, "self-link"
        if tgt in seen:
            return i, f"cycle of {i - seen[tgt]}"
        seen[cur] = i
        cur = tgt
    return limit, "open (no end found)"


# ==================================================================== RUN

CASES = [
    # name       a  b  c  d   x0            (secret) Delta
    ("identity", 1, 0, 0, 1, Fraction(7)),      # 0  parabolic
    ("shift",    1, 1, 0, 1, Fraction(0)),      # 0  parabolic
    ("negrecip", 0, -1, 1, 0, Fraction(2)),     # <0 rotation, order 2
    ("order3",   0, -1, 1, -1, Fraction(2)),    # <0 rotation, order 3
    ("golden",   1, 1, 1, 0, Fraction(1)),      # >0 boost
    ("silver",   2, 1, 1, 0, Fraction(1)),      # >0 boost
]


def delta(a, b, c, d):
    return (a + d) ** 2 - 4 * (a * d - b * c)


def main():
    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT)
    for name, a, b, c, d, x0 in CASES:
        build(name, a, b, c, d, x0)

    print("=" * 78)
    print("ON DISK: symlinks and nothing else")
    print("=" * 78)
    print()
    for name, *_ in CASES:
        base = os.path.join(ROOT, name)
        links = sorted(x for x in os.listdir(base) if x.endswith(".to"))
        print(f"  {name}/   ({len(links)} links)")
        for l in links[:4]:
            t = os.readlink(os.path.join(base, l))
            mark = "   <-- SELF" if t == l else ""
            print(f"      {l:>22} -> {t}{mark}")
        if len(links) > 4:
            print(f"      ... {len(links)-4} more")
        print()

    print("=" * 78)
    print("WHAT THE OS SAYS WHEN ASKED TO RESOLVE")
    print("=" * 78)
    print()
    print(f"  {'case':>10} {'first link':>22} {'OS verdict':>20}")
    print("  " + "-" * 56)
    for name, *_ in CASES:
        base = os.path.join(ROOT, name)
        links = sorted(x for x in os.listdir(base) if x.endswith(".to"))
        if links:
            print(f"  {name:>10} {links[0]:>22} "
                  f"{probe(os.path.join(base, links[0])):>20}")
    print()
    print("  ELOOP is the filesystem's word for undefined. note that it")
    print("  appears for BOTH a self-link and a cycle -- the OS cannot")
    print("  tell order 1 from order 2. that is a resolution limit.")
    print()

    print("=" * 78)
    print("WHAT A READER FINDS BY HOPPING, ONE LINK AT A TIME")
    print("=" * 78)
    print()
    print(f"  {'case':>10} {'hops':>6} {'ending':>22} {'sector recovered':>20} "
          f"{'(secret Delta)':>16}")
    print("  " + "-" * 78)
    for name, a, b, c, d, x0 in CASES:
        base = os.path.join(ROOT, name)
        links = sorted(x for x in os.listdir(base) if x.endswith(".to"))
        h, end = hop_count(base, links[0] if links else "")
        if end == "self-link":
            sec = "PARABOLIC"
        elif end.startswith("cycle"):
            sec = "ROTATION"
        elif end.startswith("open") or end == "dangling":
            sec = "BOOST"
        else:
            sec = "?"
        D = delta(a, b, c, d)
        print(f"  {name:>10} {h:>6} {end:>22} {sec:>20} {str(D):>16}")
    print()
    print("  the sector was recovered from HOW THE WALK ENDS. the writer")
    print("  wrote no sector, no Delta, no a b c d. the last column is")
    print("  printed here only to check the answer.")
    print()

    print("=" * 78)
    print("READLINK NEVER FAILS")
    print("=" * 78)
    print()
    print(f"  {'case':>10} {'link':>22} {'realpath':>20} {'readlink':>22}")
    print("  " + "-" * 78)
    for name, *_ in CASES:
        base = os.path.join(ROOT, name)
        links = sorted(x for x in os.listdir(base) if x.endswith(".to"))
        if not links:
            continue
        l = links[0]
        p = os.path.join(base, l)
        print(f"  {name:>10} {l:>22} {probe(p):>20} "
              f"{os.readlink(p):>22}")
    print()
    print("  the information was always there. what the OS could not do")
    print("  was FOLLOW it to a terminating answer. the undefined is in")
    print("  the walk, not in the structure.")
    print()

    print("=" * 78)
    print("THE COORDINATE ARTIFACT")
    print("=" * 78)
    print()
    print("  x -> (ax+b)/(cx+d) is 'undefined' where cx + d = 0. that is")
    print("  not a hole. it is the point sent to infinity, and on the")
    print("  Riemann sphere infinity is an ordinary point -- the map is")
    print("  perfectly defined there in another chart.")
    print()
    print("  same structure as Schwarzschild: g_tt blows up at r = r_s,")
    print("  but the Kretschmann scalar stays finite. the horizon is a")
    print("  coordinate singularity. r = 0 is the real one.")
    print()
    print("  and same structure here: ELOOP is the walker's chart failing.")
    print("  readlink is the other chart, and it resolves instantly.")
    print()
    print("  meaning -> meaning is not broken. it is the one node whose")
    print("  value is its own reference: storage and reference coincide.")
    print("  that is the between, and it is exactly where a walker")
    print("  reports undefined while a reader reports a fixed point.")


if __name__ == "__main__":
    main()
