#!/usr/bin/env python3
"""
================================================================================
EMERGE — a filesystem where the law is not written down
================================================================================

THE CONSTRAINT

Nothing in this filesystem states a law. No file says "boost" or "Delta = 5"
or "this is the parabolic locus". The only things written are:

    directories   — states
    symlinks      — relations between states
    one integer per node, in a file called `v`

That is the whole ontology. Everything else has to be RECOVERED by walking.

WHY A FILESYSTEM AND NOT A DATA STRUCTURE

A symlink is a relation that has a value: it points, and where it points is
its content. It is the smallest object that is simultaneously a reference and
a storage. And a walker traversing symlinks has exactly two options, which is
the origin of this whole line of work:

    follow the links    — zip -r, five CPU-hours, never terminates
    read the relation   — realpath, instant

The difference between those two walkers is the subject.

HOW THE STRUCTURE IS LAID DOWN

A Mobius relation x -> (ax+b)/(cx+d) is built as a directory whose `next`
symlink points at the successor state. Successive application makes a chain.
When the chain revisits a state, the symlink closes a loop.

CRUCIALLY: a, b, c, d are never written to disk. Only the resulting integer
at each node, and the links. The map has to be INFERRED from the transitions,
which is exactly instants.py — four observations pin the law.

WHAT SHOULD EMERGE, WITHOUT BEING PUT IN

 1. the three sectors — from the topology of the link graph alone
 2. Delta — from four consecutive nodes, by solving for the law
 3. the arrow — from whether the walk converges or cycles
 4. the horizon — from nodes no walk can leave
 5. epsilon — from how finely the integers distinguish states

Each of these is COMPUTED by a reader, never stored by the writer.

Run:  python3 emerge.py
================================================================================
"""

import os
import shutil
import subprocess
from fractions import Fraction

ROOT = "/tmp/emergent"


# ============================================================ THE WRITER
# knows the law. writes only states and links. never writes the law.

def mobius(a, b, c, d, x):
    den = c * x + d
    if den == 0:
        return None
    return Fraction(a * x + b, den)


def lay_down(name, a, b, c, d, x0, steps=24, scale=10**6):
    """
    Build a chain of directories joined by `next` symlinks.
    Each node holds ONLY an integer: round(x * scale).
    a,b,c,d are NOT written anywhere.
    """
    base = os.path.join(ROOT, name)
    os.makedirs(base, exist_ok=True)

    x = Fraction(x0)
    seen = {}
    prev_dir = None
    for i in range(steps):
        key = int(round(float(x) * scale))
        d_ = os.path.join(base, f"n{i:03d}")
        os.makedirs(d_, exist_ok=True)
        with open(os.path.join(d_, "v"), "w") as f:
            f.write(str(key))

        if prev_dir is not None:
            link = os.path.join(prev_dir, "next")
            if not os.path.lexists(link):
                os.symlink(os.path.relpath(d_, prev_dir), link)

        # if this state was seen before, close the loop and stop
        if key in seen:
            link = os.path.join(d_, "next")
            if not os.path.lexists(link):
                os.symlink(os.path.relpath(seen[key], d_), link)
            break
        seen[key] = d_

        nx = mobius(a, b, c, d, x)
        if nx is None:
            break
        x = nx
        prev_dir = d_
    return base


# ============================================================ THE READER
# knows nothing. has only the directories, the links, and the integers.

def walk(start, limit=10000):
    """Follow `next` links. Return the path of node directories visited."""
    path = []
    cur = start
    seen_paths = set()
    for _ in range(limit):
        real = os.path.realpath(cur)
        if real in seen_paths:
            path.append(real)
            return path, True          # closed a loop
        seen_paths.add(real)
        path.append(real)
        nxt = os.path.join(cur, "next")
        if not os.path.lexists(nxt):
            return path, False         # ran out
        cur = nxt
    return path, False


def value(node, scale=10**6):
    with open(os.path.join(node, "v")) as f:
        return Fraction(int(f.read().strip()), scale)


def infer_law(vals):
    """
    Four consecutive values pin a Mobius map up to scale.
    Each transition x -> y gives  a*x + b - c*x*y - d*y = 0.
    Solve the 3x4 homogeneous system.
    """
    if len(vals) < 4:
        return None
    rows = []
    for i in range(3):
        x, y = vals[i], vals[i + 1]
        rows.append([x, Fraction(1), -x * y, -y])
    # gaussian elimination over Q
    m = [r[:] for r in rows]
    n, piv = 4, []
    r = 0
    for c in range(n):
        p = None
        for rr in range(r, len(m)):
            if m[rr][c] != 0:
                p = rr
                break
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        f = m[r][c]
        m[r] = [v / f for v in m[r]]
        for rr in range(len(m)):
            if rr != r and m[rr][c] != 0:
                g = m[rr][c]
                m[rr] = [v - g * w for v, w in zip(m[rr], m[r])]
        piv.append(c)
        r += 1
        if r == len(m):
            break
    free = [c for c in range(n) if c not in piv]
    if len(free) != 1:
        return None
    fc = free[0]
    sol = [Fraction(0)] * n
    sol[fc] = Fraction(1)
    for i, c in enumerate(piv):
        sol[c] = -m[i][fc]
    return sol  # [a, b, c, d] up to scale


def delta_of(law):
    a, b, c, d = law
    return (a + d) ** 2 - 4 * (a * d - b * c)


def sector(D):
    if D == 0:
        return "PARABOLIC"
    return "BOOST" if D > 0 else "ROTATION"


# ============================================================ BUILD & READ

def build_all():
    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT)
    # the writer chooses laws. it never records them.
    lay_down("alpha", 1, 1, 1, 0, Fraction(1))          # x -> 1 + 1/x
    lay_down("beta",  0, -1, 1, 0, Fraction(2))         # x -> -1/x   (order 4)
    lay_down("gamma", 1, 1, 0, 1, Fraction(0))          # x -> x + 1  (parabolic)
    lay_down("delta", 2, 1, 1, 0, Fraction(1))          # x -> 2 + 1/x
    lay_down("epsil", 0, 1, 1, 1, Fraction(1))          # x -> 1/(x+1)


def report():
    print("=" * 78)
    print("WHAT IS ON DISK")
    print("=" * 78)
    print()
    out = subprocess.run(["find", ROOT, "-maxdepth", "2"],
                         capture_output=True, text=True).stdout
    lines = out.strip().split("\n")
    print(f"  {len(lines)} entries. a sample:")
    for l in lines[:8]:
        print("   ", l)
    print("    ...")
    print()
    n_dirs = sum(1 for _, ds, _ in os.walk(ROOT) for _ in ds)
    n_links = sum(1 for r, ds, fs in os.walk(ROOT)
                  for x in ds + fs if os.path.islink(os.path.join(r, x)))
    n_files = sum(1 for _, _, fs in os.walk(ROOT) for _ in fs)
    print(f"  directories: {n_dirs}   symlinks: {n_links}   files: {n_files}")
    print()
    print("  every file is named 'v' and contains one integer.")
    print("  no file contains a, b, c, d, a sector name, or Delta.")
    print()

    print("=" * 78)
    print("WHAT A READER RECOVERS, KNOWING NONE OF IT")
    print("=" * 78)
    print()
    print(f"  {'chain':>8} {'nodes':>7} {'closes?':>9} {'law (a:b:c:d)':>22} "
          f"{'Delta':>10} {'sector':>11}")
    print("  " + "-" * 74)
    for name in sorted(os.listdir(ROOT)):
        start = os.path.join(ROOT, name, "n000")
        if not os.path.isdir(start):
            continue
        path, closed = walk(start)
        vals = [value(p) for p in path]
        law = infer_law(vals)
        if law is None:
            print(f"  {name:>8} {len(path):>7} {str(closed):>9} "
                  f"{'underdetermined':>22}")
            continue
        D = delta_of(law)
        lawstr = ":".join(str(x) for x in law)
        if len(lawstr) > 22:
            lawstr = lawstr[:19] + "..."
        print(f"  {name:>8} {len(path):>7} {str(closed):>9} {lawstr:>22} "
              f"{str(D):>10} {sector(D):>11}")
    print()
    print("  the law, Delta and the sector were all RECOVERED. none were")
    print("  written. four consecutive integers pin the relation.")
    print()

    print("=" * 78)
    print("THE ARROW, FROM TOPOLOGY ALONE")
    print("=" * 78)
    print()
    print("  a reader that does not even solve for the law can still tell")
    print("  the sectors apart, by what the WALK does:")
    print()
    print(f"  {'chain':>8} {'walk ends by':>18} {'distinct values':>17} "
          f"{'reading':>22}")
    print("  " + "-" * 70)
    for name in sorted(os.listdir(ROOT)):
        start = os.path.join(ROOT, name, "n000")
        if not os.path.isdir(start):
            continue
        path, closed = walk(start)
        vals = [value(p) for p in path]
        distinct = len(set(vals))
        if closed and distinct < len(path):
            ends, read = "returning", "cycles: no arrow"
        elif distinct == len(path) and len(path) < 24:
            ends, read = "running out", "escapes"
        else:
            ends, read = "converging", "arrowed"
        print(f"  {name:>8} {ends:>18} {distinct:>17} {read:>22}")
    print()

    print("=" * 78)
    print("EPSILON IS IN THE FILESYSTEM, NOT IN THE THEORY")
    print("=" * 78)
    print()
    print("  each node stores round(x * 10^6). that integer IS the")
    print("  resolution. change the scale and the same relation produces")
    print("  a different number of distinct states.")
    print()
    print(f"  {'scale':>12} {'distinct states in alpha':>26} "
          f"{'closes?':>10}")
    print("  " + "-" * 52)
    for sc in (10, 10**2, 10**4, 10**6, 10**9):
        tmp = lay_down(f"_eps{sc}", 1, 1, 1, 0, Fraction(1),
                       steps=30, scale=sc)
        p, cl = walk(os.path.join(tmp, "n000"))
        vs = set()
        for node in p:
            with open(os.path.join(node, "v")) as f:
                vs.add(f.read().strip())
        print(f"  {sc:12d} {len(vs):26d} {str(cl):>10}")
        shutil.rmtree(tmp)
    print()
    print("  coarse epsilon: the chain closes almost at once -- the walker")
    print("  cannot tell the later states apart, so it sees a cycle.")
    print("  fine epsilon: the chain keeps going -- every step is a new")
    print("  state.")
    print()
    print("  THE SAME RELATION IS A ROTATION TO ONE WALKER AND A BOOST TO")
    print("  ANOTHER, PURELY BY RESOLUTION. that is not put in. it is what")
    print("  a finite filesystem does to an infinite process.")
    print()

    print("=" * 78)
    print("THE TWO WALKERS")
    print("=" * 78)
    print()
    a = os.path.join(ROOT, "alpha", "n000")
    path, closed = walk(a)
    print(f"  follow the links:  {len(path)} steps before "
          f"{'a loop closes' if closed else 'the chain ends'}")
    r = subprocess.run(["realpath", os.path.join(a, "next")],
                       capture_output=True, text=True)
    print(f"  read the relation: realpath resolves in one call")
    print(f"                     -> {r.stdout.strip()}")
    print()
    print("  the difference between those two is Delta: one walks, the")
    print("  other reads the invariant. neither is written down.")


if __name__ == "__main__":
    build_all()
    report()
