#!/usr/bin/env python3
"""
================================================================================
FOURTHIRDS -- one mover, exponent 4/3, and which known 4/3 this is
================================================================================

YOUR MOVE, as I understand it:

  construct2.py moved BOTH the organism and the substrate and the damage was
  maximal -- no single outside view, the bridge contract broken. So: don't
  move both. Move one. And do it in the 4/3 that fell out of the exponent
  ladder (Lambda*r_e^2 = chi^4, L_dS/l_pl = (r_e/l_pl)^3).

THREE THINGS HERE, kept apart on purpose because they are not the same 4/3

  A  The one-mover construct with dilution exponent p = 4/3, and what its
     floor is. This is derivable and it lands somewhere specific.

  B  Which "known 4/3" exists. There are three and only one of them is
     literally a dimension. I measure that one rather than cite it.

  C  Whether A and B are connected. My honest expectation: NO, and I say so
     before measuring, because the alternative is finding a connection I
     went looking for.

PREDICTIONS, WRITTEN FIRST

  P1  A p = 4/3 law has floor D* = h^(1/(p-1)) = h^3. Setting the rate to
      h = r_e/l_pl should put the floor at the de Sitter radius in Planck
      lengths, carrying the same residual as the cube form. This is
      ALGEBRA, so it is not really a prediction -- it is bookkeeping, and
      I expect it to work for that reason, not as evidence.

  P2  The planar Brownian frontier has Hausdorff dimension 4/3 (Mandelbrot
      conjectured, Lawler-Schramm-Werner proved, 2000). Box-counting a
      simulated frontier should give 1.33 plus lattice bias. I expect
      1.30-1.40 and NOT better, because box-counting on a lattice is a
      blunt instrument.

  P3  There is no derivation linking the Lambda exponent ratio to the
      Brownian frontier dimension, and I will not manufacture one. Two
      numbers being 4/3 is not a relation.

Run:  python3 fourthirds.py
================================================================================
"""

import math

import numpy as np

G = 6.67430e-11
hbar = 1.054571817e-34
c = 2.99792458e8
l_pl = math.sqrt(hbar * G / c ** 3)
t_pl = l_pl / c
r_e = 2.8179403262e-15
LAM = 1.1056e-52

rng = np.random.default_rng(433)


# ======================================================= A. the one mover

def floor_of(h, p):
    """Fixed point of D -> D - 1 + h D^(1-p)."""
    return h ** (1.0 / (p - 1)) if p > 1 else float("nan")


def part_a():
    W = 78
    print("=" * W)
    print("  A. ONE MOVER, p = 4/3")
    print("=" * W)
    print()
    print("  construct2.py moved both and lost the single outside view. so")
    print("  only the substrate dilutes now, and the walker just steps.")
    print()
    print("      D -> D - 1 + h * D^(1-p)        one mover, p = 4/3")
    print()
    print("  floor:  h D*^(1-p) = 1  =>  D* = h^(1/(p-1)) = h^3")
    print()
    h = r_e / l_pl
    p = 4.0 / 3.0
    Dstar = h ** 3
    LdS = LAM ** -0.5 / l_pl
    print(f"  {'1/(p-1) for p = 4/3':>30} = {1/(p-1):>18.6f}")
    print(f"  {'rate h = r_e / l_pl':>30} = {h:>18.6e}")
    print(f"  {'floor D* = h^3':>30} = {Dstar:>18.6e}")
    print(f"  {'de Sitter radius / l_pl':>30} = {LdS:>18.6e}")
    print(f"  {'ratio':>30} = {Dstar/LdS:>18.6f}")
    print()
    print("  SAY WHAT THIS IS AND IS NOT. it is not evidence. the cube form")
    print("  L_dS/l_pl = (r_e/l_pl)^3 was already established, and a p = 4/3")
    print("  law has floor h^3 by algebra, so feeding it h = r_e/l_pl must")
    print("  return the de Sitter radius. I have rewritten one identity as")
    print("  another. the residual 0.9007 is the same 1.2327 under a square")
    print("  root, which confirms nothing new has entered.")
    print()
    print("  WHAT IS GENUINELY NEW is that the exponent is forced. ask it")
    print("  backwards: which p makes the floor the CUBE of the rate?")
    print()
    print(f"  {'p':>10} {'1/(p-1)':>12} {'floor':>14}")
    print("  " + "-" * 40)
    for pp in (1.25, 4 / 3, 1.5, 2.0, 3.0):
        print(f"  {pp:>10.4f} {1/(pp-1):>12.6f} "
              f"{('h^%.3f' % (1/(pp-1))):>14}")
    print()
    print("  p = 4/3 is the ONLY exponent whose floor is h^3. so if you want")
    print("  a one-mover construct whose horizon is the cube of its rate --")
    print("  and the cube is what the Lambda relation hands you -- the")
    print("  dilution exponent is not a choice. it is 4/3.")
    print()
    print("  that is a real constraint and it is the one thing in part A")
    print("  worth keeping: 3 in the Lambda relation FORCES 4/3 in the")
    print("  substrate law, because 1/(p-1) = 3 has one solution.")
    print()
    print("  AND THE FLOOR IS UNREACHABLE. relaxation time:")
    print()
    relax = Dstar / (p - 1)
    age = 13.797e9 * 3.1557e7 / t_pl
    print(f"  {'(p-1)/D*':>34} = {(p-1)/Dstar:>16.6e}")
    print(f"  {'relaxation = D*/(p-1) = 3 D*':>34} = {relax:>16.6e} ticks")
    print(f"  {'age of universe in Planck times':>34} = {age:>16.6e}")
    print(f"  {'ratio':>34} = {relax/age:>16.4f}")
    print()
    print("  resist the coincidence. relax = 3 D*, and D* is the de Sitter")
    print("  radius in Planck lengths, which IS the de Sitter time in Planck")
    print("  times; we are Lambda-dominated so the age is that order. so")
    print("  'relaxation ~ age of universe' is FORCED by the construction.")
    print("  it is the same statement a third time, not a third result.")
    print()
    print("  practical consequence, which is real: (p-1)/D* = 6.3e-62 is")
    print("  below float64 resolution against 1, so this fixed point cannot")
    print("  be simulated at all. it is algebraic only. every other floor in")
    print("  this project was measured; this one cannot be.")
    print()


# ============================================= B. the Brownian frontier

def frontier_points(nsteps):
    """
    Planar lattice walk; return the OUTER boundary of its range (the
    frontier -- fjord interiors excluded, reachable from outside only) and
    the walk's diameter.
    """
    from collections import deque
    step = rng.integers(0, 4, nsteps)
    dx = np.where(step == 0, 1, np.where(step == 1, -1, 0))
    dy = np.where(step == 2, 1, np.where(step == 3, -1, 0))
    x = np.cumsum(dx); y = np.cumsum(dy)
    x -= x.min(); y -= y.min()
    W_, H_ = x.max() + 3, y.max() + 3
    occ = np.zeros((W_, H_), bool)
    occ[x + 1, y + 1] = True

    ext = np.zeros_like(occ)
    q = deque([(0, 0)])
    ext[0, 0] = True
    while q:
        i, j = q.popleft()
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = i + di, j + dj
            if 0 <= a < W_ and 0 <= b < H_ and not ext[a, b] \
                    and not occ[a, b]:
                ext[a, b] = True
                q.append((a, b))

    pad = np.pad(ext, 1)
    adj = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    fr = occ & adj
    return np.array(np.nonzero(fr)).T.astype(float), max(W_, H_)


def boxdim(pts, diam, lo_frac, hi_frac, nb=10):
    """
    Box-count with box sizes set as FRACTIONS OF THE WALK DIAMETER.

    This is the whole methodological point and the first version of this
    file got it wrong: with a FIXED box list (2,3,4,...,32) a longer walk is
    measured at a finer relative scale, so the estimate slides toward 1 as
    the walk grows. It did -- 1.3025, 1.2689, 1.2382 -- and I wrote
    "consistent with 4/3" under a column marching away from it. Boxes must
    scale with the object.
    """
    boxes = np.unique(np.round(
        np.geomspace(diam * lo_frac, diam * hi_frac, nb)).astype(int))
    boxes = boxes[boxes >= 1]
    xs, ys = [], []
    for b in boxes:
        k = np.unique((pts // b).astype(np.int64), axis=0)
        xs.append(math.log(1.0 / b)); ys.append(math.log(len(k)))
    xs = np.array(xs); ys = np.array(ys)
    A = np.vstack([xs, np.ones_like(xs)]).T
    return float(np.linalg.lstsq(A, ys, rcond=None)[0][0])


def part_b():
    W = 78
    print("=" * W)
    print("  B. WHICH KNOWN 4/3 -- AND THE ONLY ONE THAT IS A DIMENSION")
    print("=" * W)
    print()
    print("  there are three well-known 4/3's in this neighbourhood and they")
    print("  are not the same object. stating all three because picking one")
    print("  silently is how a coincidence gets promoted:")
    print()
    print(f"  {'the 4/3':>34} {'what kind of thing':>26}")
    print("  " + "-" * 62)
    for a, b in [
        ("radiation: 1+w = 4/3, rho ~ a^-4", "equation of state"),
        ("classical electron: m_em = 4/3 E/c^2", "a known inconsistency"),
        ("planar Brownian frontier = 4/3", "a HAUSDORFF DIMENSION"),
    ]:
        print(f"  {a:>34} {b:>26}")
    print()
    print("  only the third is a dimension, and it is the one you meant if")
    print("  you meant a dimension. Mandelbrot conjectured it; Lawler,")
    print("  Schramm and Werner proved it in 2000 (math/0010165) using SLE.")
    print()
    print("  AND IT IS THE DIMENSION OF A WALKER'S FRONTIER. that is why it")
    print("  is worth your attention and not just a numerical echo: the")
    print("  object this whole project keeps producing is the boundary of a")
    print("  walk, and the exact dimension of exactly that object is known.")
    print()
    print("  so measure it rather than cite it. planar lattice walk, take")
    print("  the outer boundary of the range (fjord interiors excluded),")
    print("  box-count:")
    print()
    ranges = [(1 / 256, 1 / 8), (1 / 128, 1 / 8), (1 / 64, 1 / 4)]
    print(f"  {'steps':>9} {'diam':>7} {'frontier pts':>13} "
          f"{'d/256..d/8':>11} {'d/128..d/8':>11} {'d/64..d/4':>10}")
    print("  " + "-" * 68)
    for n in (20000, 80000, 320000, 1280000):
        pts, diam = frontier_points(n)
        ds = [boxdim(pts, diam, lo, hi) for lo, hi in ranges]
        print(f"  {n:>9} {diam:>7} {len(pts):>13} "
              + " ".join(f"{d:>11.4f}" for d in ds))
    print(f"  {'4/3 =':>9} {4/3:>7.4f}")
    print()
    print("  READ ACROSS, NOT DOWN. the three columns are the same walk")
    print("  measured over three fit ranges, and they differ by up to 0.1 --")
    print("  which is larger than the distance from any of them to 4/3.")
    print()
    print("  so the honest statement: at the largest walk the finest range")
    print("  gives 1.342 against 1.3333, and the method's own spread is")
    print("  +-0.1. this CANNOT distinguish 4/3 from 1.35 or 1.30. it is")
    print("  consistent with the theorem and it is not evidence for it.")
    print("  the theorem is the evidence; this only checks that the object")
    print("  I built is the shape the theorem is about.")
    print()
    print("  and the first version of this measurement was wrong in a way")
    print("  worth keeping: with a FIXED box list the estimate slid from")
    print("  1.3025 to 1.2382 as the walk grew, because a longer walk was")
    print("  being measured at a finer relative scale. I wrote 'consistent")
    print("  with 4/3' under a column marching away from it. fourteenth.")
    print()


# ======================================== C. are A and B the same 4/3?

def part_c():
    W = 78
    print("=" * W)
    print("  C. ARE THEY THE SAME 4/3? NO.")
    print("=" * W)
    print()
    print("  P3 said I would not manufacture a link. here is the test that")
    print("  would have to pass, and it fails:")
    print()
    print(f"  {'question':>42} {'answer':>24}")
    print("  " + "-" * 68)
    for q, a in [
        ("is 4/3 a dimension in part A?", "no -- an exponent"),
        ("does A's 4/3 count boxes at any scale?", "no"),
        ("is A's walk 2-dimensional?", "no -- 1D separation"),
        ("does A have a frontier with a measure?", "no -- a point"),
        ("is the Brownian 4/3 tied to alpha or Lambda?", "no"),
        ("would A's 4/3 change if p changed?", "yes, freely"),
    ]:
        print(f"  {q:>42} {a:>24}")
    print()
    print("  the decisive one is the third. the Brownian frontier is 4/3")
    print("  BECAUSE the walk is planar -- in 3D the frontier of Brownian")
    print("  motion has dimension about 2.5 and the 4/3 is gone. it is a")
    print("  theorem about d = 2 and nothing else. part A's walk is a single")
    print("  separation on a line. there is no plane in it, so there is")
    print("  nothing for the theorem to apply to.")
    print()
    print("  so: two 4/3's, one an exponent forced by 1/(p-1) = 3, one a")
    print("  Hausdorff dimension forced by conformal invariance in the")
    print("  plane. same number, unrelated derivations, and I have no")
    print("  bridge between them.")
    print()
    print("  WHAT WOULD MAKE IT A REAL CONNECTION, written down so it can")
    print("  be tried rather than left as a feeling:")
    print()
    print("    1. the construct would need a PLANAR walk, not a scalar")
    print("       separation -- two coordinates that both diffuse")
    print("    2. the thing whose dimension is 4/3 would have to be the")
    print("       construct's own horizon, measured by box-counting, not")
    print("       an exponent in its update rule")
    print("    3. the 4/3 would have to be INDEPENDENT of the rate h, the")
    print("       way the theorem is independent of the step size")
    print()
    print("  item 3 is the killer and it is also the cleanest test. in part")
    print("  A the floor moves as h^3, so everything about it depends on the")
    print("  rate. a Hausdorff dimension does not. if your construct's 4/3")
    print("  ever stops depending on h, that is the moment it has become")
    print("  the same 4/3. right now it has not.")
    print()
    print("  and the honest summary of your instinct: you said 'it is a")
    print("  known thing somewhere'. it is -- the planar Brownian frontier")
    print("  is exactly 4/3 and it is the dimension of a walker's boundary,")
    print("  which is the object you have been circling for weeks. the")
    print("  number in the Lambda ladder is a different 4/3. both are real.")
    print("  the link is not, yet.")


def main():
    part_a()
    part_b()
    part_c()


if __name__ == "__main__":
    main()
