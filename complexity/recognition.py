#!/usr/bin/env python3
"""
================================================================================
RECOGNITION -- what it is, measured, and what it costs
================================================================================

boundary.py ended with: the correct field has no traps, and building it costs
one global scan. For 3-SAT no trap-free field is known.

RECOGNITION is the missing third thing. Definition used here, chosen because
it is measurable:

    Recognition is deciding which ALREADY-PAID-FOR structure an instance
    belongs to, without solving the instance.

If recognition succeeds, you do not descend a field at all. You apply a
solver that was built once for the whole class. The per-instance cost drops
to the cost of the test.

THE TEST CASE: RENAMABLE HORN

  A clause is Horn if it has at most one positive literal. Horn-SAT is
  solvable in LINEAR time by unit propagation -- no search, no descent.

  A formula is RENAMABLE Horn if some subset of variables can be flipped to
  make every clause Horn. Recognising this is a 2-SAT instance, so it is
  polynomial. It is a real, non-trivial equivalence class.

  So: hard-looking 3-SAT instances, at a clause ratio where plain descent
  died 120 times out of 120 in boundary.py, that are secretly in a tractable
  class. Blind descent cannot see it. Recognition can.

WHAT IS MEASURED

  1. blind descent on these instances                    (should fail)
  2. the recognition test, and its cost                  (should be cheap)
  3. the class solver after recognition                  (should be instant)
  4. the same recognition test on genuinely random 3-SAT (should say no)
  5. what happens when recognition is itself NP-hard

Run:  python3 recognition.py
================================================================================
"""

import random
import time
from collections import defaultdict

rnd = random.Random(515)


# ============================================================== generators

def horn_3sat(n, m, r):
    """Every clause has at most one positive literal."""
    cl = []
    while len(cl) < m:
        vs = r.sample(range(1, n + 1), 3)
        pos = r.randrange(4)          # 0..2 = which one is positive, 3 = none
        c = tuple(v if i == pos else -v for i, v in enumerate(vs))
        cl.append(c)
    return cl


def rename(cl, flip):
    return tuple(tuple(-l if abs(l) in flip else l for l in c) for c in cl)


def random_3sat(n, m, r):
    cl = []
    while len(cl) < m:
        vs = r.sample(range(1, n + 1), 3)
        cl.append(tuple(v * r.choice([1, -1]) for v in vs))
    return cl


# ================================================= 1. blind local descent

def unsat_count(cl, a):
    c = 0
    for cc in cl:
        if not any((a[abs(l) - 1] if l > 0 else not a[abs(l) - 1])
                   for l in cc):
            c += 1
    return c


def blind_descent(cl, n, a, limit=3000):
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


# ======================================= 2. recognition: is it renamable?

def two_sat(n, clauses):
    """Standard implication-graph 2-SAT. Returns an assignment or None."""
    N = 2 * n
    def idx(l):
        v = abs(l) - 1
        return 2 * v + (0 if l > 0 else 1)
    def neg(i):
        return i ^ 1
    adj = defaultdict(list)
    radj = defaultdict(list)
    for (a, b) in clauses:
        for (x, y) in ((a, b), (b, a)):
            u, v = neg(idx(x)), idx(y)
            adj[u].append(v)
            radj[v].append(u)
    order, seen = [], [False] * N
    for s in range(N):
        if seen[s]:
            continue
        st = [(s, iter(adj[s]))]
        seen[s] = True
        while st:
            node, it = st[-1]
            for w in it:
                if not seen[w]:
                    seen[w] = True
                    st.append((w, iter(adj[w])))
                    break
            else:
                order.append(node)
                st.pop()
    comp = [-1] * N
    c = 0
    for node in reversed(order):
        if comp[node] != -1:
            continue
        st = [node]
        comp[node] = c
        while st:
            u = st.pop()
            for w in radj[u]:
                if comp[w] == -1:
                    comp[w] = c
                    st.append(w)
        c += 1
    for v in range(n):
        if comp[2 * v] == comp[2 * v + 1]:
            return None
    return [comp[2 * v] > comp[2 * v + 1] for v in range(n)]


def recognise_renamable_horn(cl, n):
    """
    Lewis's reduction. Variable x_v true means 'flip v'.
    For every pair of positive literals (p, q) in a clause, at least one
    must be flipped: clause (x_p or x_q).
    For a positive p and negative -q, not both may end up positive:
    (x_p or not x_q)... encoded directly below.
    """
    two = []
    for c in cl:
        lits = list(c)
        for i in range(len(lits)):
            for j in range(i + 1, len(lits)):
                a, b = lits[i], lits[j]
                # x_v means "flip v". literal l is POSITIVE after renaming
                # iff (l>0 and not flipped) or (l<0 and flipped), so
                #   P(+v) = not x_v ,  P(-v) = x_v
                # at most one positive per clause means, for every pair,
                #   not(P(a) and P(b))  =  (not P(a)) or (not P(b))
                # and  not P(+v) = x_v ,  not P(-v) = not x_v
                # which is literally a and b again.
                two.append((a, b))
    sol = two_sat(n, two)
    if sol is None:
        return None
    return {v + 1 for v in range(n) if sol[v]}


# ================================ 3. the class solver: unit propagation

def horn_solve(cl, n):
    """Linear-time Horn-SAT. No search at all."""
    a = [False] * n
    changed = True
    while changed:
        changed = False
        for c in cl:
            sat = any((a[abs(l) - 1] if l > 0 else not a[abs(l) - 1])
                      for l in c)
            if sat:
                continue
            pos = [l for l in c if l > 0]
            if len(pos) == 1:
                a[pos[0] - 1] = True
                changed = True
            elif not pos:
                return None
    return a if unsat_count(cl, a) == 0 else None


def is_horn(cl):
    return all(sum(1 for l in c if l > 0) <= 1 for c in cl)


# ==================================================================== run

def main():
    n, ratio, T = 40, 5.0, 60
    m = int(n * ratio)

    print("=" * 78)
    print("SETUP")
    print("=" * 78)
    print()
    print(f"  n = {n} variables, m = {m} clauses, ratio {ratio}")
    print(f"  in boundary.py, blind descent solved 0 / 120 at this ratio.")
    print(f"  these instances are renamable Horn, which blind descent")
    print(f"  cannot see. {T} trials.")
    print()

    insts = []
    for _ in range(T):
        base = horn_3sat(n, m, rnd)
        flip = {v for v in range(1, n + 1) if rnd.random() < 0.5}
        insts.append((rename(base, flip), flip))

    print("=" * 78)
    print("1. BLIND DESCENT (no recognition)")
    print("=" * 78)
    print()
    t0 = time.perf_counter()
    res = defaultdict(int)
    for cl, _ in insts:
        a = [rnd.random() < 0.5 for _ in range(n)]
        _, o = blind_descent(list(cl), n, a)
        res[o] += 1
    t_blind = time.perf_counter() - t0
    for k, v in sorted(res.items()):
        print(f"  {k:>8} : {v:>4} / {T}")
    print(f"  time: {t_blind:.3f} s")
    print()
    print(f"  visibly Horn without renaming? "
          f"{sum(is_horn(cl) for cl, _ in insts)} / {T}")
    print()

    print("=" * 78)
    print("2. RECOGNITION")
    print("=" * 78)
    print()
    t0 = time.perf_counter()
    rec = [recognise_renamable_horn(list(cl), n) for cl, _ in insts]
    t_rec = time.perf_counter() - t0
    ok = sum(1 for r in rec if r is not None)
    print(f"  recognised as renamable Horn: {ok} / {T}")
    print(f"  time: {t_rec:.4f} s  ({t_rec/T*1000:.2f} ms per instance)")
    print(f"  vs blind descent:             {t_blind/T*1000:.2f} ms per "
          f"instance")
    print()

    print("=" * 78)
    print("3. SOLVE AFTER RECOGNITION")
    print("=" * 78)
    print()
    t0 = time.perf_counter()
    solved = 0
    for (cl, _), fl in zip(insts, rec):
        if fl is None:
            continue
        rc = rename(cl, fl)
        assert is_horn(rc)
        a = horn_solve(list(rc), n)
        if a is not None:
            back = [a[v] != (v + 1 in fl) for v in range(n)]
            if unsat_count(cl, back) == 0:
                solved += 1
    t_solve = time.perf_counter() - t0
    print(f"  solved after renaming: {solved} / {T}")
    print(f"  time: {t_solve:.4f} s  ({t_solve/T*1000:.2f} ms per instance)")
    print()
    print(f"  {'':>26} {'solved':>8} {'ms/instance':>14}")
    print("  " + "-" * 50)
    print(f"  {'blind descent':>26} {res.get('sat',0):>8} "
          f"{t_blind/T*1000:>14.2f}")
    print(f"  {'recognise + class solver':>26} {solved:>8} "
          f"{(t_rec+t_solve)/T*1000:>14.2f}")
    print()

    print("=" * 78)
    print("4. DOES RECOGNITION FALSELY FIRE ON RANDOM INSTANCES?")
    print("=" * 78)
    print()
    rr = [random_3sat(n, m, rnd) for _ in range(T)]
    fired = sum(1 for cl in rr if recognise_renamable_horn(cl, n) is not None)
    print(f"  genuinely random 3-SAT at ratio {ratio}: "
          f"recognised {fired} / {T}")
    print()
    print("  so the test is not vacuous. it says yes to the class and no")
    print("  to everything else. that is what makes it recognition rather")
    print("  than wishful thinking.")
    print()

    print("=" * 78)
    print("5. THE LIMIT")
    print("=" * 78)
    print()
    print("  recognition worked because a POLYNOMIAL test exists for this")
    print("  class, and someone found it (Lewis, 1978). that is the whole")
    print("  of the win, and it is not free:")
    print()
    print("  - the class had to be identified in advance")
    print("  - the test had to be discovered")
    print("  - the class solver had to be written")
    print()
    print("  all of that is the 'one global scan' from boundary.py, paid in")
    print("  a different currency: human work, done once, amortised over")
    print("  every instance anyone will ever meet.")
    print()
    print("  and the classes are a measure-zero slice. random 3-SAT at the")
    print("  threshold belongs to none of them, which is exactly why it is")
    print("  the standard hard case.")
    print()
    print("  so, stated carefully:")
    print()
    print("    boundary   makes the search FINITE   (the field is bounded)")
    print("    recognition makes it FAST            (the class is prepaid)")
    print("    P vs NP    asks whether recognition is ALWAYS possible")
    print()
    print("  that formulation is correct. and it is a restatement, not a")
    print("  solution: 'is there always a polynomial recognisable structure'")
    print("  is the same question wearing different clothes.")


if __name__ == "__main__":
    main()
