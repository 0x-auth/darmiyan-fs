#!/usr/bin/env python3
"""
================================================================================
MIRROR -- the two-resolver framework, built on the case where every answer
          is already known
================================================================================

WHAT THIS IS

Thread 9 of OPEN_THREADS.md, built. The specification was:

  1. an artifact: a relation laid down as structure, naming no domain
  2. resolver I (inside): hop count, local name, own accumulated error.
     clock is tau = sum|err|. hits ELOOP. reports undefined at fixed points.
  3. resolver O (outside): readlink, the whole link table, never walks,
     never fails, has no proper time.
  4. a bridge invariant both compute INDEPENDENTLY and must agree on.
     load-bearing: without it the construction is decorative.
  5. the payload is the two disagreements, not the agreements.

Built on Mobius maps because there the answer is known in advance, so the
bridge can be checked rather than asserted. That was the whole point of not
starting with an application.

THE BRIDGE INVARIANT

  D = tr^2 / det

Scale-free (multiplying the matrix by k leaves D fixed), unlike Delta
itself. Both resolvers must produce it, from disjoint information.

  OUTSIDE  reads node values off the link table and solves for (a,b,c,d)
           exactly over the rationals, then computes tr^2/det.
           It never walks and never follows a link to its end.

  INSIDE   never sees a matrix. It measures the SIGNED ratio of consecutive
           differences, r = lim (x_(n+2)-x_(n+1)) / (x_(n+1)-x_n), which is
           the multiplier at the attracting fixed point, and computes

               D = r + 2 + 1/r

           from that alone. It has no global view and no access to the law.

If those two disagree, the mirror is broken, not interesting.

Run:  python3 mirror.py
================================================================================
"""

import math
import os
import shutil
from fractions import Fraction

ROOT = "/tmp/mirror"


# =============================================================== THE ARTIFACT

def nm(x):
    if x is None:
        return "inf"
    return f"{x.numerator}_{x.denominator}"


def step(a, b, c, d, x):
    if x is None:                     # the point at infinity
        return None if c == 0 else Fraction(a, c)
    den = c * x + d
    if den == 0:
        return None
    return Fraction(a * x + b, den)


def build(name, a, b, c, d, x0, steps=28):
    """
    One directory per visited value; a symlink `to` pointing at the next
    one's directory. Nothing on disk records a, b, c, d, the sector, or
    any invariant. The writer lays down links and leaves.
    """
    base = os.path.join(ROOT, name)
    os.makedirs(base, exist_ok=True)
    x = Fraction(x0)
    seen = {}
    order = []
    for i in range(steps):
        key = nm(x)
        if key in seen:
            # close the loop and stop
            link = os.path.join(base, key, "to")
            break
        seen[key] = i
        order.append(x)
        os.makedirs(os.path.join(base, key), exist_ok=True)
        nxt = step(a, b, c, d, x)
        nkey = nm(nxt)
        os.makedirs(os.path.join(base, nkey), exist_ok=True)
        link = os.path.join(base, key, "to")
        if not os.path.lexists(link):
            os.symlink(os.path.join("..", nkey), link)
        if nxt == x:                       # fixed point: self-link
            break
        x = nxt
    return base, order


# ============================================================ RESOLVER: INSIDE

class Inside:
    """
    Knows: how many hops it has taken, and the name of the directory it is
    standing in. Nothing else. No map, no wall clock, no link table.
    """

    def __init__(self, base, start):
        self.base = base
        self.start = start

    def walk(self, limit=60):
        cur = os.path.join(self.base, self.start)
        vals, tau, hops = [], Fraction(0), 0
        seen = {}
        ending = "open"
        while hops < limit:
            here = os.path.basename(os.path.realpath(cur))
            if here in seen:
                ending = f"cycle of {hops - seen[here]}"
                break
            seen[here] = hops
            try:
                n, d = here.split("_")
                vals.append(Fraction(int(n), int(d)))
            except ValueError:
                ending = "undefined name"
                break
            link = os.path.join(cur, "to")
            if not os.path.lexists(link):
                ending = "dangling"
                break
            tgt = os.readlink(link)
            if os.path.basename(tgt) == here:
                ending = "self-link"
                break
            cur = os.path.join(self.base, os.path.basename(tgt))
            hops += 1
        for i in range(1, len(vals)):
            tau += abs(vals[i] - vals[i - 1])
        return vals, tau, ending

    def probe_eloop(self):
        """What the OS says when asked to resolve, rather than to read."""
        p = os.path.join(self.base, self.start, "to")
        try:
            os.stat(p)
            return "resolves"
        except OSError as e:
            return f"errno {e.errno}"

    def invariant(self, vals):
        """
        D = r + 2 + 1/r, where r is the signed limit of the ratio of
        consecutive differences. Measured, not looked up.
        """
        d = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        d = [x for x in d if x != 0]
        if len(d) < 6:
            return None, None
        ratios = [float(d[i + 1] / d[i]) for i in range(len(d) - 1)]
        r = ratios[-1]
        if r == 0:
            return None, ratios
        # NO SNAPPING. An earlier version forced r = 1 whenever it came close,
        # which manufactured an exact match on the parabolic cases. The raw
        # limit is reported and the parabolic error is left visible: r -> 1
        # only polynomially there (like 1 - 2/n), so a finite walk always
        # undershoots, and D = r + 2 + 1/r is quadratically insensitive near
        # r = 1, which is why the undershoot still lands close to 4.
        return r + 2 + 1.0 / r, ratios


# =========================================================== RESOLVER: OUTSIDE

class Outside:
    """
    Reads the link table. Never walks, never follows a link to its end,
    has no proper time, and cannot fail.
    """

    def __init__(self, base):
        self.base = base

    def table(self):
        pairs = []
        for e in sorted(os.listdir(self.base)):
            link = os.path.join(self.base, e, "to")
            if os.path.islink(link):
                pairs.append((e, os.path.basename(os.readlink(link))))
        return pairs

    @staticmethod
    def _val(s):
        if s == "inf":
            return None
        n, d = s.split("_")
        return Fraction(int(n), int(d))

    def recover(self):
        """
        Solve  a x + b - c x y - d y = 0  over the rationals for three
        distinct finite pairs. Exact Gaussian elimination, no floats.
        Returns (a, b, c, d) up to scale, or None.
        """
        pts = []
        for s, t in self.table():
            x, y = self._val(s), self._val(t)
            if x is not None and y is not None and x != y:
                pts.append((x, y))
            if len(pts) == 3:
                break
        if len(pts) < 3:
            return None
        M = [[x, Fraction(1), -x * y, -y] for x, y in pts]
        # nullspace of a 3x4 rational matrix
        piv, row = [], 0
        for col in range(4):
            sel = next((r for r in range(row, 3) if M[r][col] != 0), None)
            if sel is None:
                continue
            M[row], M[sel] = M[sel], M[row]
            pv = M[row][col]
            M[row] = [v / pv for v in M[row]]
            for r in range(3):
                if r != row and M[r][col] != 0:
                    f = M[r][col]
                    M[r] = [M[r][k] - f * M[row][k] for k in range(4)]
            piv.append(col)
            row += 1
            if row == 3:
                break
        free = [c for c in range(4) if c not in piv]
        if not free:
            return None
        f = free[0]
        sol = [Fraction(0)] * 4
        sol[f] = Fraction(1)
        for i, c in enumerate(piv):
            sol[c] = -M[i][f]
        den = 1
        for v in sol:
            den = den * v.denominator // math.gcd(den, v.denominator)
        return tuple(int(v * den) for v in sol)

    def invariant(self):
        m = self.recover()
        if m is None:
            return None, None
        a, b, c, d = m
        det = a * d - b * c
        if det == 0:
            return None, m
        return (a + d) ** 2 / det, m

    def fixed_points(self):
        """Where does the relation send a point to itself? Algebra, no walk."""
        m = self.recover()
        if m is None:
            return []
        a, b, c, d = m
        if c == 0:
            return ["infinity"] + ([] if a == d else
                                   [str(Fraction(b, d - a))])
        disc = (a - d) ** 2 + 4 * b * c
        if disc < 0:
            return ["none on the real line (complex pair)"]
        s = math.sqrt(disc)
        return [f"{(a - d + s) / (2 * c):.10f}", f"{(a - d - s) / (2 * c):.10f}"]


# ========================================================================= RUN

CASES = [
    # name        a   b   c   d   x0            what it secretly is
    ("boost",     1,  1,  1,  0, 1),          # det -1, Delta 5
    ("boost2",    2,  1,  1,  1, 1),          # det  1, Delta 5
    ("boost3",    3,  1,  1,  0, 1),          # det -1, Delta 13
    ("parabolic", 1,  1,  0,  1, 0),          # Delta 0, fixed pt at infinity
    ("parabolic2", 2, -1,  1,  0, 2),         # Delta 0, fixed pt at 1
    ("order2",    0, -1,  1,  0, 2),          # rotation, order 2
    ("order3",    0, -1,  1, -1, 2),          # rotation, order 3
    ("atfixed",   2, -1,  1,  0, 1),          # started ON the fixed point
    ("hitsinf",   0,  1,  1, -1, 2),          # 2 -> 1 -> infinity
]


def main():
    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    os.makedirs(ROOT)
    built = {}
    for name, a, b, c, d, x0 in CASES:
        base, order = build(name, a, b, c, d, x0)
        built[name] = (base, order, (a, b, c, d))

    W = 78
    print("=" * W)
    print("1. WHAT IS ON DISK")
    print("=" * W)
    print()
    base, order, _ = built["boost"]
    for e in sorted(os.listdir(base))[:5]:
        l = os.path.join(base, e, "to")
        if os.path.islink(l):
            print(f"    {e}/to -> {os.readlink(l)}")
    print(f"    ... {len(os.listdir(base))-5} more")
    print()
    print("  directories and symlinks. no a, b, c, d anywhere, no sector,")
    print("  no invariant, no clock.")
    print()

    print("=" * W)
    print("2. THE BRIDGE: TWO RESOLVERS, ONE INVARIANT, DISJOINT INPUTS")
    print("=" * W)
    print()
    print("  outside: solves for the map from three node values, exactly")
    print("           over the rationals. never walks.")
    print("  inside:  measures r = lim (dx_(n+1)/dx_n) from its own steps")
    print("           and returns r + 2 + 1/r. never sees a matrix.")
    print()
    print(f"  {'case':>12} {'D outside':>12} {'D inside':>12} {'|diff|':>11} "
          f"{'agree':>7} {'(truth)':>10}")
    print("  " + "-" * 70)
    agree_all = True
    for name, a, b, c, d, x0 in CASES:
        base, order, _ = built[name]
        out = Outside(base)
        d_out, m = out.invariant()
        start = nm(Fraction(x0))
        ins = Inside(base, start)
        vals, tau, ending = ins.walk()
        d_in, ratios = ins.invariant(vals)
        truth = (a + d) ** 2 / (a * d - b * c) if (a * d - b * c) else None
        if d_out is None or d_in is None:
            ok = "n/a"
            diff = float("nan")
        else:
            diff = abs(float(d_out) - d_in)
            ok = "yes" if diff < 1e-6 else ("close" if diff < 1e-2 else "NO")
            if ok == "NO":
                agree_all = False
        do = f"{float(d_out):.6f}" if d_out is not None else "--"
        di = f"{d_in:.6f}" if d_in is not None else "--"
        tr = f"{float(truth):.4f}" if truth is not None else "--"
        print(f"  {name:>12} {do:>12} {di:>12} {diff:>11.2e} {ok:>7} "
              f"{tr:>10}")
    print()
    print(f"  bridge holds on every case: {agree_all}")
    print()
    print("  the rotations return no inside value. a finite orbit gives no")
    print("  limit of difference ratios, so the inside resolver has nothing")
    print("  to extrapolate. that is a real limit of the inside chart and")
    print("  is reported as one, not patched over.")
    print()

    print("=" * W)
    print("3. THE PAYLOAD: WHERE THE TWO CHARTS DISAGREE")
    print("=" * W)
    print()
    print(f"  {'case':>12} {'inside says':>22} {'outside says':>34}")
    print("  " + "-" * 72)
    for name, a, b, c, d, x0 in CASES:
        base, order, _ = built[name]
        ins = Inside(base, nm(Fraction(x0)))
        vals, tau, ending = ins.walk()
        fp = Outside(base).fixed_points()
        errno = ins.probe_eloop()
        if ending == "dangling":
            ending = "ran out (step limit)"
        inside_says = ending if errno == "resolves" else f"{ending} / {errno}"
        outside_says = "fixed points: " + ", ".join(fp)[:44]
        print(f"  {name:>12} {inside_says:>22} {outside_says:>34}")
    print()
    print("  DISAGREEMENT CLASS 1 -- inside reports a terminating failure")
    print("  where outside reports an ordinary object.")
    print("    atfixed   inside: self-link      outside: a fixed point")
    print("    order2/3  inside: cycle of k     outside: a finite orbit")
    print("  in a simulation this is the deadlock, the stall, the control")
    print("  lock. from the ground track it is a normal attractor.")
    print()
    print("  DISAGREEMENT CLASS 2 -- inside reaches a name it cannot parse")
    print("  where outside reports an ordinary point in another chart.")
    print("    hitsinf   inside: undefined name")
    print("              outside: fixed points 1.618, -0.618, both finite")
    print("  the walk died at infinity; the relation did not. in a")
    print("  simulation this is gimbal lock: the coordinate failed, the")
    print("  system was fine.")
    print()
    print("  telling those two apart is the thing a single-chart simulator")
    print("  cannot do, and it is the only reason to build the pair.")
    print()
    print("  AND ONE CASE WHERE BOTH CHARTS LOSE. `atfixed` starts on the")
    print("  fixed point, so the orbit is one point: the inside resolver")
    print("  gets a self-link and no differences, and the OUTSIDE resolver")
    print("  cannot solve for the map either, because three distinct pairs")
    print("  do not exist. both columns are blank in section 2.")
    print()
    print("  that is not a bug in either resolver. it is the same fact")
    print("  chain/verify.py found from the other direction: at a fixed")
    print("  point the relation carries no information, so there is nothing")
    print("  for any chart to read. the pair does not rescue it, because")
    print("  there is no pair there -- x_(n+1) = x_n is one state wearing")
    print("  two labels.")
    print()

    print("=" * W)
    print("4. WHAT EACH RESOLVER HAS THAT THE OTHER DOES NOT")
    print("=" * W)
    print()
    base, order, _ = built["boost"]
    ins = Inside(base, nm(Fraction(1)))
    vals, tau, ending = ins.walk()
    out = Outside(base)
    print(f"  {'':>26} {'inside':>16} {'outside':>22}")
    print("  " + "-" * 66)
    print(f"  {'proper time tau':>26} {float(tau):>16.12f} "
          f"{'none -- does not move':>22}")
    print(f"  {'hops taken':>26} {len(vals):>16} "
          f"{'0':>22}")
    print(f"  {'can fail':>26} {'yes (ELOOP)':>16} {'no':>22}")
    print(f"  {'sees the whole relation':>26} {'no':>16} {'yes':>22}")
    print(f"  {'recovers D':>26} {'yes, from error':>16} "
          f"{'yes, from algebra':>22}")
    print()
    print("  tau belongs to the walker and to nothing else. the outside")
    print("  resolver is not slow, it is untimed: it never takes a step, so")
    print("  it accumulates no error, so it has no clock. that is the same")
    print("  statement as 'readlink never fails', read from the other side.")
    print()

    print("=" * W)
    print("5. WHAT IS STILL MISSING")
    print("=" * W)
    print()
    print("  the bridge holds and the disagreements are legible, so the")
    print("  framework works on the case where the answer was known. the")
    print("  two things it does not have:")
    print()
    print("  THE UNIT. D is a ratio. it says which conjugacy class the")
    print("  relation belongs to and never which member, and it says")
    print("  nothing about rate: the square of a map has the same orbit at")
    print("  half the tick count and the inside resolver cannot tell.")
    print("  supplying that needs something outside the structure.")
    print()
    print("  THE ROTATIONS. the inside chart has no handle on a finite")
    print("  orbit beyond its length. recovering D there needs the winding")
    print("  number, which is combinatorial rather than metric, and is a")
    print("  separate piece of work.")


if __name__ == "__main__":
    main()
