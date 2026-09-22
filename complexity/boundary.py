#!/usr/bin/env python3
"""
================================================================================
BOUNDARY -- when a search problem is not a search problem
================================================================================

THE CLAIM BEING TESTED

  "People in a burning theatre do not compute left/right every second. The
   exits are a boundary condition. What looks like a search problem may not
   be a search at all -- it may be guided by the boundary."

This is testable, so it is tested. Four parts.

  1. Build a room. Solve it BOTH ways: per-agent search, and one global
     field that every agent then descends for free. Count the cost.
  2. Show the field's decisive property: descent from ANY cell reaches an
     exit, with no search, because a BFS distance field has no spurious
     local minima. This is a theorem, not luck, and it is why the intuition
     is correct for this problem.
  3. Break it. Use a CHEAP field (straight-line distance to nearest exit)
     instead of the true one. Agents now get trapped. The boundary
     condition only works if the field is the right one, and building the
     right one costs a global scan.
  4. Go to an actual NP-hard problem (3-SAT) and do the same thing. The
     natural field (unsatisfied clause count) is cheap to evaluate and
     has traps. Measure how often descent gets stuck.

WHAT THE ANSWER TURNS OUT TO BE

  The boundary condition does not remove the search. It AMORTISES it:
  one global computation, then every local decision is free, for every
  agent, forever. That is a real and large win, and it is exactly what a
  potential field is in physics.

  It is not P = NP. The win requires a polynomial-size field with no
  spurious minima, and for NP-hard problems the existence of one is the
  open question itself.

Run:  python3 boundary.py
================================================================================
"""

import heapq
import math
import random
from collections import deque

random.seed(515)


# ================================================================ the room

def make_room(W=61, H=41):
    """
    Walls on the boundary, four exits, and interior obstacles including a
    concave pocket -- a seating block with an opening facing away from the
    nearest exit.
    """
    g = [["." for _ in range(W)] for _ in range(H)]
    for x in range(W):
        g[0][x] = g[H - 1][x] = "#"
    for y in range(H):
        g[y][0] = g[y][W - 1] = "#"

    exits = [(0, W // 2), (H - 1, W // 2), (H // 2, 0), (H // 2, W - 1)]
    for (y, x) in exits:
        g[y][x] = "E"

    # seating blocks
    for by in range(6, H - 6, 9):
        for bx in range(6, W - 6, 13):
            for dy in range(5):
                for dx in range(9):
                    if 0 < by + dy < H - 1 and 0 < bx + dx < W - 1:
                        g[by + dy][bx + dx] = "#"
            # an aisle through each block
            for dy in range(5):
                g[by + dy][bx + 4] = "."

    # one concave pocket that opens AWAY from the centre
    py, px = H - 10, 8
    for dx in range(12):
        g[py][px + dx] = "#"
        g[py + 6][px + dx] = "#"
    for dy in range(7):
        g[py + dy][px + 11] = "#"

    for (y, x) in exits:
        g[y][x] = "E"
    return g, exits


def free_cells(g):
    return [(y, x) for y, row in enumerate(g)
            for x, c in enumerate(row) if c != "#"]


NB = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# ======================================================= method A: search

def astar(g, start, exits):
    """Per-agent search. Counts cells expanded."""
    H, W = len(g), len(g[0])
    ex = set(exits)

    def h(p):
        return min(abs(p[0] - e[0]) + abs(p[1] - e[1]) for e in ex)

    openq = [(h(start), 0, start)]
    best = {start: 0}
    expanded = 0
    while openq:
        f, gc, cur = heapq.heappop(openq)
        if cur in ex:
            return gc, expanded
        if gc > best.get(cur, 1 << 30):
            continue
        expanded += 1
        for dy, dx in NB:
            n = (cur[0] + dy, cur[1] + dx)
            if not (0 <= n[0] < H and 0 <= n[1] < W):
                continue
            if g[n[0]][n[1]] == "#":
                continue
            ng = gc + 1
            if ng < best.get(n, 1 << 30):
                best[n] = ng
                heapq.heappush(openq, (ng + h(n), ng, n))
    return None, expanded


# ======================================================== method B: field

def true_field(g, exits):
    """One BFS from all exits at once. Cost = O(cells), paid once."""
    H, W = len(g), len(g[0])
    d = [[None] * W for _ in range(H)]
    q = deque()
    for (y, x) in exits:
        d[y][x] = 0
        q.append((y, x))
    visited = 0
    while q:
        y, x = q.popleft()
        visited += 1
        for dy, dx in NB:
            ny, nx = y + dy, x + dx
            if 0 <= ny < H and 0 <= nx < W and g[ny][nx] != "#" \
                    and d[ny][nx] is None:
                d[ny][nx] = d[y][x] + 1
                q.append((ny, nx))
    return d, visited


def cheap_field(g, exits):
    """Straight-line distance to the nearest exit. Ignores walls entirely.
    Costs nothing to build. This is the naive boundary condition."""
    H, W = len(g), len(g[0])
    d = [[None] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if g[y][x] != "#":
                d[y][x] = min(math.hypot(y - e[0], x - e[1]) for e in exits)
    return d


def descend(g, d, start, exits, limit=4000):
    """
    The agent's whole algorithm: look at the four neighbours, step to the
    lowest. No search, no memory, no map. Returns (steps, outcome).
    """
    ex = set(exits)
    H, W = len(g), len(g[0])
    cur = start
    seen = set()
    for i in range(limit):
        if cur in ex:
            return i, "out"
        if cur in seen:
            return i, "cycle"
        seen.add(cur)
        best, bn = d[cur[0]][cur[1]], None
        for dy, dx in NB:
            n = (cur[0] + dy, cur[1] + dx)
            if not (0 <= n[0] < H and 0 <= n[1] < W):
                continue
            if g[n[0]][n[1]] == "#" or d[n[0]][n[1]] is None:
                continue
            if d[n[0]][n[1]] < best:
                best, bn = d[n[0]][n[1]], n
        if bn is None:
            return i, "stuck"
        cur = bn
    return limit, "limit"


# ====================================================== part 4: 3-SAT

def random_3sat(n, m, rnd):
    cl = []
    while len(cl) < m:
        vs = rnd.sample(range(n), 3)
        cl.append(tuple((v + 1) * rnd.choice([1, -1]) for v in vs))
    return cl


def unsat_count(cl, a):
    c = 0
    for c1 in cl:
        if not any((a[abs(l) - 1] if l > 0 else not a[abs(l) - 1])
                   for l in c1):
            c += 1
    return c


def sat_descend(cl, n, a, limit=5000):
    """Same rule as the agents: flip whichever single variable most reduces
    the 'distance to an exit'. Strictly downhill, no sideways, no restarts."""
    cur = unsat_count(cl, a)
    for i in range(limit):
        if cur == 0:
            return i, "sat"
        bi, bv = None, cur
        for v in range(n):
            a[v] = not a[v]
            u = unsat_count(cl, a)
            a[v] = not a[v]
            if u < bv:
                bv, bi = u, v
        if bi is None:
            return i, "stuck"
        a[bi] = not a[bi]
        cur = bv
    return limit, "limit"


# ==================================================================== run

def main():
    g, exits = make_room()
    cells = free_cells(g)
    starts = random.sample(cells, 400)
    starts = [s for s in starts if s not in set(exits)]

    print("=" * 78)
    print("1. SAME PROBLEM, TWO WAYS. COUNT THE COST.")
    print("=" * 78)
    print()
    print(f"  room: {len(g[0])} x {len(g)}, {len(cells)} free cells, "
          f"{len(exits)} exits, {len(starts)} agents")
    print()

    tot_exp = 0
    lens_a = []
    for s in starts:
        L, e = astar(g, s, exits)
        tot_exp += e
        if L is not None:
            lens_a.append(L)

    d, visited = true_field(g, exits)
    lens_b, outs = [], {}
    for s in starts:
        L, o = descend(g, d, s, exits)
        outs[o] = outs.get(o, 0) + 1
        if o == "out":
            lens_b.append(L)

    print(f"  {'method':>34} {'cells touched':>16} {'mean path':>12}")
    print("  " + "-" * 64)
    print(f"  {'A*, once per agent':>34} {tot_exp:>16,} "
          f"{sum(lens_a)/len(lens_a):>12.2f}")
    print(f"  {'one BFS field + free descent':>34} "
          f"{visited + sum(lens_b):>16,} {sum(lens_b)/len(lens_b):>12.2f}")
    print()
    print(f"  field build alone: {visited:,} cells, paid ONCE, shared by all")
    print(f"  per-agent cost after that: 4 comparisons per step")
    print(f"  cost ratio: {tot_exp/(visited + sum(lens_b)):.1f}x")
    print(f"  paths identical in length: "
          f"{sum(lens_a) == sum(lens_b)}")
    print()
    print("  the search did not disappear. it was done ONCE, for everyone,")
    print("  and turned into a field. that is the whole of the insight and")
    print("  it is correct.")
    print()

    print("=" * 78)
    print("2. WHY IT WORKS HERE: NO TRAPS, AND THAT IS A THEOREM")
    print("=" * 78)
    print()
    print(f"  {'outcome':>12} {'agents':>8}")
    print("  " + "-" * 22)
    for k, v in sorted(outs.items()):
        print(f"  {k:>12} {v:>8}")
    print()
    # exhaustive check over every free cell
    traps = 0
    for (y, x) in cells:
        if (y, x) in set(exits) or d[y][x] is None:
            continue
        nbr = [d[y+dy][x+dx] for dy, dx in NB
               if 0 <= y+dy < len(g) and 0 <= x+dx < len(g[0])
               and g[y+dy][x+dx] != "#" and d[y+dy][x+dx] is not None]
        if nbr and min(nbr) >= d[y][x]:
            traps += 1
    print(f"  exhaustive check of all {len(cells)} cells:")
    print(f"  cells with no strictly-downhill neighbour: {traps}")
    print()
    print("  zero, and it cannot be otherwise: a BFS distance field has a")
    print("  strictly smaller neighbour at every non-exit cell, by")
    print("  construction. so greedy descent is GUARANTEED. the theatre")
    print("  intuition is not a heuristic here, it is exact.")
    print()

    print("=" * 78)
    print("3. NOW USE THE WRONG FIELD. THE CHEAP ONE.")
    print("=" * 78)
    print()
    cd = cheap_field(g, exits)
    outs2 = {}
    for s in starts:
        L, o = descend(g, cd, s, exits)
        outs2[o] = outs2.get(o, 0) + 1
    print("  field = straight-line distance to nearest exit. costs nothing")
    print("  to build. ignores walls, which is exactly what a boundary")
    print("  condition looks like if you do not pay for it.")
    print()
    print(f"  {'outcome':>12} {'true field':>12} {'cheap field':>13}")
    print("  " + "-" * 40)
    for k in sorted(set(outs) | set(outs2)):
        print(f"  {k:>12} {outs.get(k,0):>12} {outs2.get(k,0):>13}")
    print()
    traps2 = 0
    for (y, x) in cells:
        if (y, x) in set(exits) or cd[y][x] is None:
            continue
        nbr = [cd[y+dy][x+dx] for dy, dx in NB
               if 0 <= y+dy < len(g) and 0 <= x+dx < len(g[0])
               and g[y+dy][x+dx] != "#" and cd[y+dy][x+dx] is not None]
        if nbr and min(nbr) >= cd[y][x]:
            traps2 += 1
    print(f"  cells with no downhill neighbour: {traps2} "
          f"(true field: {traps})")
    print()
    print("  so the claim needs one more word. it is not 'the boundary")
    print("  condition guides you'. it is 'the CORRECT field guides you',")
    print("  and the correct field costs a global scan. the scan is the")
    print("  search, moved.")
    print()

    print("=" * 78)
    print("4. THE SAME EXPERIMENT ON AN NP-HARD PROBLEM")
    print("=" * 78)
    print()
    print("  3-SAT. field = number of unsatisfied clauses. cheap to")
    print("  evaluate at any point, exactly like the theatre. agents")
    print("  descend it by flipping one variable at a time.")
    print()
    print(f"  {'n':>5} {'m':>6} {'m/n':>6} {'trials':>8} {'reached 0':>11} "
          f"{'stuck in a trap':>17}")
    print("  " + "-" * 60)
    rnd = random.Random(515)
    for n, ratio in [(40, 2.0), (40, 3.0), (40, 4.0), (40, 4.26), (40, 5.0)]:
        m = int(n * ratio)
        sat = stuck = 0
        T = 120
        for _ in range(T):
            cl = random_3sat(n, m, rnd)
            a = [rnd.random() < 0.5 for _ in range(n)]
            _, o = sat_descend(cl, n, a)
            if o == "sat":
                sat += 1
            else:
                stuck += 1
        print(f"  {n:>5} {m:>6} {ratio:>6.2f} {T:>8} {sat:>11} {stuck:>17}")
    print()
    print("  the field exists, is cheap, and is a perfectly sensible")
    print("  boundary condition. and descent gets trapped, more and more")
    print("  often as the instance gets constrained.")
    print()
    print("  that is the difference, stated without hand-waving:")
    print()
    print("    shortest-path-to-exit  -> a polynomial field exists with NO")
    print("                              traps. guaranteed. build it once.")
    print("    3-SAT                  -> a cheap field exists but HAS traps.")
    print("                              a trap-free one would make local")
    print("                              descent solve SAT in polynomial")
    print("                              time, which is the open question.")
    print()

    print("=" * 78)
    print("5. THE PART THAT CONNECTS TO THE FILESYSTEM WORK")
    print("=" * 78)
    print()
    print("  verification is forward. checking a proposed escape route, or")
    print("  a proposed satisfying assignment, is local and cheap: walk it")
    print("  and confirm. same shape as readlink -- the answer is stored AT")
    print("  the thing.")
    print()
    print("  finding is reverse. it asks which configurations lead here,")
    print("  and that is not stored anywhere, so it is reconstructed by")
    print("  visiting. same shape as 'which names point at this file'.")
    print()
    print("  a field is a reverse lookup computed once and cached. that is")
    print("  literally what the BFS above is: for every cell, the answer to")
    print("  'how do I get out from here'. it costs one full scan of the")
    print("  world, and after that it is free forever.")
    print()
    print("  stated as an analogy, not a theorem. the forward/reverse")
    print("  asymmetry is measured in mirror_fs.py; whether P vs NP IS that")
    print("  asymmetry is not something this script shows.")


if __name__ == "__main__":
    main()
