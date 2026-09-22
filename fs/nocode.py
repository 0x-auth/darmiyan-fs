#!/usr/bin/env python3
"""
================================================================================
NOCODE -- computation laid down as topology, executed by the kernel
================================================================================

THE CLAIM BEING TESTED

  "I can even have programs written by not writing a single piece of code."

The honest form of that claim: the PROGRAM is a set of symlinks. The
INPUT is a path string. EXECUTION is the kernel's path resolver (namei).
No interpreter of ours runs. No bytecode. No eval. The only thing that
"runs" is resolution, which the OS does anyway.

Part 1  a DFA executed purely by path resolution
Part 2  arithmetic by path concatenation (succ/pred cancel in the kernel)
Part 3  a program steered by its own error signal, with no branch written
Part 4  the blockchain part, and what the construct does NOT give

Run:  python3 nocode.py
================================================================================
"""

import os
import shutil
import math

ROOT = "/tmp/nocode"


def kresolve(p):
    """
    Kernel-side resolution. os.path.realpath is PURE PYTHON -- it walks the
    links itself, which would make the whole claim circular. O_PATH makes
    namei() do the walk, and /proc/self/fd tells us where it landed.
    """
    fd = os.open(p, os.O_PATH)
    try:
        return os.readlink(f"/proc/self/fd/{fd}")
    finally:
        os.close(fd)



# ============================================================ PART 1: the DFA

def build_dfa(base, states, alphabet, delta, start):
    """
    delta[(state, symbol)] = next_state

    Each state is a directory. Each symbol is a symlink inside it pointing
    at the next state's directory. That is the entire program.
    """
    for s in states:
        os.makedirs(os.path.join(base, s), exist_ok=True)
    for (s, a), t in delta.items():
        link = os.path.join(base, s, a)
        if not os.path.lexists(link):
            os.symlink(os.path.join("..", t), link)
    return os.path.join(base, start)


def run_by_resolution(start_dir, word):
    """
    NOTHING here interprets the DFA. We build one path string and hand it
    to the kernel. os.path.realpath does the whole computation.
    """
    p = os.path.join(start_dir, *list(word))
    return os.path.basename(kresolve(p))


# ====================================================== PART 2: arithmetic

def build_peano(base, n=64):
    for i in range(n + 1):
        os.makedirs(os.path.join(base, str(i)), exist_ok=True)
    for i in range(n):
        l = os.path.join(base, str(i), "succ")
        if not os.path.lexists(l):
            os.symlink(os.path.join("..", str(i + 1)), l)
    for i in range(1, n + 1):
        l = os.path.join(base, str(i), "pred")
        if not os.path.lexists(l):
            os.symlink(os.path.join("..", str(i - 1)), l)
    return base


def add(base, a, b):
    p = os.path.join(base, str(a), *(["succ"] * b))
    return int(os.path.basename(kresolve(p)))


def sub(base, a, b):
    p = os.path.join(base, str(a), *(["pred"] * b))
    return int(os.path.basename(kresolve(p)))


# ================================================ PART 3: steered by error

def build_mirror(base, n=64):
    """
    Two chains over the same states. `up` moves +2, `down` moves -1.
    A walker that only knows |here - target| picks its next link by which
    one shrinks the error. No comparison is written into the structure.
    The structure offers moves; the error chooses.
    """
    for i in range(n + 1):
        os.makedirs(os.path.join(base, str(i)), exist_ok=True)
    for i in range(n + 1):
        for nm, step in (("up", 2), ("down", -1)):
            j = i + step
            if 0 <= j <= n:
                l = os.path.join(base, str(i), nm)
                if not os.path.lexists(l):
                    os.symlink(os.path.join("..", str(j)), l)
    return base


def steer(base, start, target, limit=200):
    """
    The 'program' is: follow whichever available link reduces |x - target|.
    That rule is one line and it is not domain knowledge -- it is the
    error signal. The behaviour (what sequence of moves) is entirely in
    the topology.
    """
    cur = str(start)
    path = [int(cur)]
    for _ in range(limit):
        x = int(cur)
        if x == target:
            return path, "reached"
        best, bestname = None, None
        for nm in ("up", "down"):
            l = os.path.join(base, cur, nm)
            if os.path.lexists(l):
                y = int(os.path.basename(kresolve(l)))
                e = abs(y - target)
                if best is None or e < best:
                    best, bestname = e, nm
        if bestname is None or best >= abs(x - target):
            return path, "stuck"
        cur = os.path.basename(kresolve(
            os.path.join(base, cur, bestname)))
        path.append(int(cur))
    return path, "limit"


# ============================================================ PART 4: chain

def confirmations(lam):
    """
    T = tanh(Lambda/2) as 'settled fraction'; attack room = 1 - T = the
    part still reversible. Compare with the standard reorg bound for an
    attacker with hash fraction q after k blocks: (q/(1-q))^k.
    """
    return math.tanh(lam / 2)


def main():
    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT)

    print("=" * 78)
    print("1. A PROGRAM THAT IS ONLY SYMLINKS, RUN BY THE KERNEL")
    print("=" * 78)
    print()
    # DFA accepting binary strings with an even number of 1s
    states = ["even", "odd"]
    delta = {("even", "0"): "even", ("even", "1"): "odd",
             ("odd", "0"): "odd", ("odd", "1"): "even"}
    start = build_dfa(os.path.join(ROOT, "parity"), states, "01", delta, "even")

    print("  the whole program on disk:")
    print()
    for s in states:
        for a in "01":
            l = os.path.join(ROOT, "parity", s, a)
            print(f"      parity/{s}/{a}  ->  {os.readlink(l)}")
    print()
    print("  4 symlinks. no code, no table in memory, no interpreter.")
    print()
    print(f"  {'input':>14} {'path handed to the kernel':>34} {'result':>10}")
    print("  " + "-" * 62)
    for w in ["", "1", "11", "101", "1011", "110011", "1111111"]:
        r = run_by_resolution(start, w)
        shown = "parity/even/" + "/".join(w) if w else "parity/even"
        print(f"  {w or '(empty)':>14} {shown[:34]:>34} {r:>10}")
    print()
    print("  every answer above came from the KERNEL resolver (O_PATH). it")
    print("  walked the links. we wrote no loop over the input.")
    print("  (os.path.realpath would NOT prove this -- it is pure python.)")
    print()

    print("=" * 78)
    print("2. ARITHMETIC BY PATH CONCATENATION")
    print("=" * 78)
    print()
    pe = build_peano(os.path.join(ROOT, "peano"), 64)
    print(f"  {'expression':>22} {'path':>30} {'value':>8}")
    print("  " + "-" * 62)
    for a, b in [(3, 4), (10, 7), (0, 12), (20, 20)]:
        print(f"  {f'{a} + {b}':>22} {f'peano/{a}/succ x{b}':>30} "
              f"{add(pe, a, b):>8}")
    for a, b in [(9, 4), (30, 30), (12, 0)]:
        print(f"  {f'{a} - {b}':>22} {f'peano/{a}/pred x{b}':>30} "
              f"{sub(pe, a, b):>8}")
    print()
    p = os.path.join(pe, "5", "succ", "succ", "pred", "succ", "pred", "pred")
    print(f"  5/succ/succ/pred/succ/pred/pred = "
          f"{os.path.basename(kresolve(p))}")
    print("  the cancellation happened inside namei(). nothing simplified")
    print("  the expression first.")
    print()
    print("  NOTE THE CEILING: each component is one symlink resolution,")
    print("  and SYMLOOP_MAX caps a single path at 40. so `a + b` by this")
    print("  method only works for b <= 40. the machine has a word size,")
    print("  and it is the kernel's, not ours.")
    print()
    for b in (39, 40, 41, 45):
        try:
            v = add(pe, 0, b)
            print(f"  0 + {b} in one path: {v}")
        except OSError as e:
            print(f"  0 + {b} in one path: OSError errno {e.errno} (ELOOP)")
    print()

    print("=" * 78)
    print("3. STEERED BY ERROR, WITH NO BRANCH WRITTEN")
    print("=" * 78)
    print()
    mb = build_mirror(os.path.join(ROOT, "mirror"), 64)
    print("  structure offers two moves per state: up (+2), down (-1).")
    print("  the only rule is 'take whichever shrinks |x - target|'.")
    print("  that rule mentions no numbers, no parity, no strategy.")
    print()
    print(f"  {'start':>7} {'target':>8} {'steps':>7} {'outcome':>10}  route")
    print("  " + "-" * 70)
    for s, t in [(0, 7), (0, 8), (10, 3), (1, 60), (30, 31)]:
        path, out = steer(mb, s, t)
        r = " ".join(str(v) for v in path)
        print(f"  {s:>7} {t:>8} {len(path)-1:>7} {out:>10}  {r[:40]}")
    print()
    print("  the +2/-1 alternation that shows up for odd targets is not in")
    print("  the rule. it is in the topology. change the link set and the")
    print("  'algorithm' changes with no edit to the rule.")
    print()

    print("=" * 78)
    print("4. THE CHAIN CLAIM, AND WHAT IS MISSING")
    print("=" * 78)
    print()
    print("  T = tanh(Lambda/2) is a settled fraction; 1 - T is the part")
    print("  still reversible. compare with the standard reorg bound for")
    print("  an attacker holding fraction q, after k blocks: (q/(1-q))^k.")
    print()
    print(f"  {'Lambda':>8} {'1 - tanh(L/2)':>16} {'2e^-Lambda':>14} "
          f"{'ratio':>10}")
    print("  " + "-" * 52)
    for lam in (1, 2, 4, 6, 8, 10, 14):
        room = 1 - confirmations(lam)
        approx = 2 * math.exp(-lam)
        print(f"  {lam:>8} {room:16.10f} {approx:14.10f} "
              f"{room/approx:10.6f}")
    print()
    print("  so 1 - T -> 2 e^-Lambda exactly, which is the same shape as")
    print("  (q/(1-q))^k with Lambda = k log((1-q)/q). the correspondence")
    print("  is real and it is exact in the tail.")
    print()
    print(f"  {'q':>6} {'log((1-q)/q)':>16}  Lambda per block")
    print("  " + "-" * 44)
    for q in (0.1, 0.2, 0.3, 0.4, 0.45, 0.49):
        print(f"  {q:>6} {math.log((1-q)/q):16.10f}")
    print()
    print("  WHAT IS MISSING, and this is the honest limit:")
    print()
    print("  the construct fixes the SHAPE of settlement but not the UNIT.")
    print("  it says how confidence grows per unit of Lambda. it does not")
    print("  say what one unit of Lambda costs an attacker. in bitcoin")
    print("  that cost is hashing -- that IS the cryptography, and it is")
    print("  what converts 'deep' into 'expensive'. topology gives depth")
    print("  for free, and free depth is free to forge.")
    print()
    print("  so: a chain without cryptography is possible only if the")
    print("  depth is expensive for some OTHER reason. SYMLOOP_MAX is one")
    print("  real, non-cryptographic cost -- it caps depth at 40 for")
    print("  everyone equally -- but a cap is not a price.")
    print()
    print("  that is the same no-scale problem as everywhere else in this")
    print("  work: Lambda is a ratio, and a ratio has no units until")
    print("  something outside the structure supplies one.")


if __name__ == "__main__":
    main()
