#!/usr/bin/env python3
"""
================================================================================
QUANTUM -- a statevector simulator, and the one operation representation lacks
================================================================================

WHAT THIS IS

  A classical simulator of a quantum computer. It is not a quantum computer
  and cannot be one: it stores 2^n complex amplitudes and pays for every
  branch. The speedup it demonstrates is real on hardware and entirely
  absent here.

WHY BUILD IT ANYWAY

  Because the thing base phi cannot do is visible in three lines of output.
  A change of base is a bijection: it permutes labels. Quantum branches
  carry AMPLITUDES, which are signed, and signed things CANCEL. That is the
  whole difference, and it is measurable.

CONTENTS

  1. the cancellation itself, digit by digit
  2. Deutsch-Jozsa: one query against 2^(n-1)+1 classical queries
  3. Grover on a 3-SAT instance at the clause ratio where local descent
     failed 120/120 in boundary.py
  4. the bill: what simulating it actually costs

Run:  python3 quantum.py
================================================================================
"""

import math
import random

import numpy as np

rng = random.Random(515)


# ============================================================ the machine

class Q:
    def __init__(self, n):
        self.n = n
        self.s = np.zeros(1 << n, dtype=complex)
        self.s[0] = 1.0
        self.ops = 0

    def h(self, q):
        """Hadamard on qubit q. The only gate that makes superposition."""
        n, s = self.n, self.s
        s = s.reshape([2] * n)
        s = np.moveaxis(s, q, 0)
        a, b = s[0].copy(), s[1].copy()
        s[0] = (a + b) / math.sqrt(2)
        s[1] = (a - b) / math.sqrt(2)     # <-- the minus sign. this is it.
        self.s = np.moveaxis(s, 0, q).reshape(-1)
        self.ops += 1

    def x(self, q):
        n, s = self.n, self.s.reshape([2] * self.n)
        s = np.moveaxis(s, q, 0)
        s[[0, 1]] = s[[1, 0]]
        self.s = np.moveaxis(s, 0, q).reshape(-1)
        self.ops += 1

    def phase_oracle(self, pred):
        """Flip the SIGN of every basis state the predicate accepts."""
        idx = np.fromiter(((-1.0 if pred(i) else 1.0)
                           for i in range(len(self.s))), float)
        self.s *= idx
        self.ops += 1

    def diffuse(self):
        """Inversion about the mean. 2|mean> - |s>."""
        m = self.s.mean()
        self.s = 2 * m - self.s
        self.ops += 1

    def probs(self):
        return np.abs(self.s) ** 2


def bits(i, n):
    return format(i, f"0{n}b")


# ==================================================================== run

def main():
    print("=" * 78)
    print("1. THE OPERATION A NUMBER BASE CANNOT PERFORM")
    print("=" * 78)
    print()
    print("  one qubit. H splits it, H again puts it back. watch the")
    print("  amplitude of |1> in the final state.")
    print()
    q = Q(1)
    print(f"  {'step':>28} {'amp |0>':>12} {'amp |1>':>12} "
          f"{'P(0)':>9} {'P(1)':>9}")
    print("  " + "-" * 74)
    print(f"  {'start |0>':>28} {q.s[0].real:>12.6f} {q.s[1].real:>12.6f} "
          f"{q.probs()[0]:>9.4f} {q.probs()[1]:>9.4f}")
    q.h(0)
    print(f"  {'after H  (split)':>28} {q.s[0].real:>12.6f} "
          f"{q.s[1].real:>12.6f} {q.probs()[0]:>9.4f} "
          f"{q.probs()[1]:>9.4f}")
    q.h(0)
    print(f"  {'after H again (recombine)':>28} {q.s[0].real:>12.6f} "
          f"{q.s[1].real:>12.6f} {q.probs()[0]:>9.4f} "
          f"{q.probs()[1]:>9.4f}")
    print()
    print("  the |1> amplitude is EXACTLY zero, and here is the arithmetic")
    print("  that made it zero:")
    print()
    r = 1 / math.sqrt(2)
    print(f"    path via |0>:  {r:+.6f} x {r:+.6f} = {r*r:+.6f}")
    print(f"    path via |1>:  {r:+.6f} x {-r:+.6f} = {-r*r:+.6f}")
    print(f"    sum         :                    "
          f"{r*r + (-r*r):+.6f}")
    print()
    print("  two routes to the same outcome, opposite signs, sum zero.")
    print()
    print("  now put a phase flip between the two H's -- flip the sign of")
    print("  the |1> branch only, and nothing else:")
    print()
    q = Q(1)
    q.h(0)
    q.phase_oracle(lambda i: i == 1)
    q.h(0)
    print(f"  {'H, phase flip on |1>, H':>28} {q.s[0].real:>12.6f} "
          f"{q.s[1].real:>12.6f} {q.probs()[0]:>9.4f} "
          f"{q.probs()[1]:>9.4f}")
    print()
    print("  the outcome INVERTED. |0> now has probability zero. a sign on")
    print("  a branch nobody measured changed which answer comes out with")
    print("  certainty.")
    print()
    print("  this is the operation nothing in the previous four scripts")
    print("  could do. a probability distribution cannot: probabilities")
    print("  are non-negative and only ever ADD. a change of base cannot:")
    print("  a base relabels, relabeling is a permutation, and a")
    print("  permutation moves things without ever annihilating one.")
    print()
    print("  the minus sign in the second row of H is the entire")
    print("  difference between this and base phi.")
    print()

    print("=" * 78)
    print("2. DEUTSCH-JOZSA: ONE QUERY AGAINST 2^(n-1) + 1")
    print("=" * 78)
    print()
    print("  promise: f is constant, or balanced (half 0, half 1).")
    print("  classically you may need 2^(n-1)+1 queries to be SURE.")
    print()
    print(f"  {'n':>4} {'classical worst case':>22} {'quantum queries':>17} "
          f"{'verdict':>12} {'correct':>9}")
    print("  " + "-" * 70)
    for n in (3, 5, 8, 12):
        for kind in ("constant", "balanced"):
            if kind == "constant":
                c = rng.randrange(2)
                f = (lambda c: (lambda x: c))(c)
            else:
                mask = rng.randrange(1, 1 << n)
                f = (lambda m: (lambda x: bin(x & m).count("1") & 1))(mask)
            q = Q(n)
            for i in range(n):
                q.h(i)
            q.phase_oracle(lambda i: f(i) == 1)
            for i in range(n):
                q.h(i)
            p0 = q.probs()[0]
            verdict = "constant" if p0 > 0.5 else "balanced"
            print(f"  {n:>4} {2**(n-1)+1:>22,} {1:>17} {verdict:>12} "
                  f"{str(verdict == kind):>9}")
    print()
    print("  one oracle call, every time, and the answer is exact. the")
    print("  interference put ALL the amplitude on |0...0> for constant")
    print("  and NONE there for balanced.")
    print()

    print("=" * 78)
    print("3. GROVER ON THE 3-SAT THAT BEAT LOCAL DESCENT")
    print("=" * 78)
    print()
    n, ratio = 14, 5.0
    m = int(n * ratio)

    def rand_3sat(n, m, r):
        cl = []
        while len(cl) < m:
            vs = r.sample(range(n), 3)
            cl.append(tuple((v, r.choice([True, False])) for v in vs))
        return cl

    def sat(cl, a):
        for c in cl:
            if not any(((a >> v) & 1 == 1) == pol for v, pol in c):
                return False
        return True

    # find an instance with a handful of solutions
    for _ in range(4000):
        cl = rand_3sat(n, m, rng)
        sols = [a for a in range(1 << n) if sat(cl, a)]
        if 1 <= len(sols) <= 6:
            break
    N = 1 << n
    M = len(sols)
    print(f"  n = {n} variables, m = {m} clauses, ratio {ratio}")
    print(f"  search space N = {N:,},  satisfying assignments M = {M}")
    print(f"  in boundary.py, strict local descent solved 0/120 at this")
    print(f"  ratio. it is not that the instances are unsolvable. it is")
    print(f"  that the landscape has traps.")
    print()
    q = Q(n)
    for i in range(n):
        q.h(i)
    iters = int(math.floor(math.pi / 4 * math.sqrt(N / M)))
    print(f"  Grover iterations = floor(pi/4 * sqrt(N/M)) = {iters}")
    print()
    print(f"  {'iteration':>11} {'P(a solution)':>16} {'P(any single wrong)':>21}")
    print("  " + "-" * 52)
    marks = set(sols)
    checkpoints = {0, 1, iters // 4, iters // 2, 3 * iters // 4, iters}
    p = q.probs()
    print(f"  {0:>11} {sum(p[s] for s in sols):>16.8f} "
          f"{p[(sols[0]+1) % N]:>21.8f}")
    for t in range(1, iters + 1):
        q.phase_oracle(lambda i: i in marks)
        q.diffuse()
        if t in checkpoints:
            p = q.probs()
            print(f"  {t:>11} {sum(p[s] for s in sols):>16.8f} "
                  f"{p[(sols[0]+1) % N]:>21.8f}")
    p = q.probs()
    best = int(np.argmax(p))
    print()
    print(f"  most likely measurement: {bits(best, n)}  "
          f"(satisfying: {sat(cl, best)})")
    print(f"  probability of landing on a solution: "
          f"{sum(p[s] for s in sols):.6f}")
    print()
    print(f"  {'method':>34} {'oracle calls':>16}")
    print("  " + "-" * 52)
    print(f"  {'exhaustive search (expected)':>34} {N//(M+1):>16,}")
    print(f"  {'Grover':>34} {iters:>16,}")
    print(f"  {'ratio':>34} {N//(M+1)/iters:>16.1f}x")
    print()
    print("  sqrt, not exponential. Grover is quadratic and that is a")
    print("  theorem about its optimality, not a limit of this code. no")
    print("  quantum algorithm searches an unstructured space faster.")
    print()

    print("=" * 78)
    print("4. THE BILL")
    print("=" * 78)
    print()
    print(f"  {'n':>5} {'amplitudes':>16} {'memory (complex128)':>22}")
    print("  " + "-" * 46)
    for k in (14, 20, 30, 40, 50, 60):
        b = (1 << k) * 16
        u = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
        i = 0
        v = float(b)
        while v >= 1024 and i < 6:
            v /= 1024; i += 1
        print(f"  {k:>5} {1 << k:>16,} {f'{v:.1f} {u[i]}':>22}")
    print()
    print("  this simulator pays for every branch. that is why it is a")
    print("  simulator. a real device holds the superposition in physical")
    print("  degrees of freedom and pays nothing per branch, which is the")
    print("  entire point and the entire engineering difficulty.")
    print()
    print("  so, to be exact about what was built here: a correct, slow,")
    print("  classical model of quantum interference. it demonstrates the")
    print("  mechanism and provides no speedup whatsoever.")
    print()
    print("  and the mechanism is the one thing a number system cannot")
    print("  supply, at any base, algebraic or transcendental, Pisot or")
    print("  not: a signed weight that can cancel another.")


if __name__ == "__main__":
    main()
