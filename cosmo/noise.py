#!/usr/bin/env python3
"""
================================================================================
NOISE -- the lineage you are pointing at: fluctuation as an instrument
================================================================================

WHAT YOU SAID, AS I UNDERSTAND IT

  The 4/3 is not a dimension of space and not of time. And in the thing that
  produces it there is no relativity and no quantum fluctuation -- nothing is
  required. And Brownian motion is where Einstein found atoms without ever
  looking at one.

That is one observation and it is the sharpest thing said in this project so
far, so let me state it rather than decorate it:

  EVERY OTHER NUMBER WE HAVE CHASED NEEDED A UNIT. 4/3 DOES NOT.

  Lambda needed hbar, c, G, m_e. The horizon needed H. The NEC needed hbar.
  Twelve times the form came out and the size did not, because the size was
  always carried by a measured constant. The frontier dimension is 4/3 with
  no constant in it at all. It is not measured, it is proved. It is what
  planar randomness costs and there is nothing else in it.

  So the missing unit is not missing here. There is no unit to miss.

Run:  python3 noise.py
================================================================================
"""

import math
from collections import deque

import numpy as np

rng = np.random.default_rng(99)
R = 8.314462618
NA = 6.02214076e23
kB = 1.380649e-23
e = 1.602176634e-19


# ====================================================== 1. the instrument

def part1():
    W = 78
    print("=" * W)
    print("  1. EINSTEIN'S TRICK: THE WALK IS THE INSTRUMENT")
    print("=" * W)
    print()
    print("  Einstein, May 1905 (the same year as special relativity, and")
    print("  this paper has none of it in it):")
    print()
    print("      <x^2> = 2 D t        D = RT / (6 pi eta a N_A)")
    print()
    print("  the left side is a wobble you can watch. the right side has")
    print("  Avogadro's number in it. so WATCHING A WOBBLE COUNTS ATOMS.")
    print()
    T, eta = 293.0, 1.0e-3
    print(f"  {'bead radius':>16} {'D (m^2/s)':>14} {'rms in 30 s':>14}")
    print("  " + "-" * 48)
    for a in (0.212e-6, 0.52e-6, 1.0e-6):
        D = R * T / (6 * math.pi * eta * a * NA)
        print(f"  {a*1e6:>13.3f} um {D:>14.4e} "
              f"{math.sqrt(2*D*30)*1e6:>11.2f} um")
    print()
    print("  a few microns in half a minute. a microscope and a ruled grid")
    print("  reach that. Perrin ran it thousands of times from 1908 and")
    print("  inverted it for N_A to a few percent; Nobel 1926, and the")
    print("  atomic hypothesis stopped being a hypothesis.")
    print()
    print("  NOTHING IN THAT CALCULATION RESOLVES AN ATOM. it has a")
    print("  viscosity, a temperature, a bead radius, and the VARIANCE OF A")
    print("  WALK. the unobservable was counted by the statistics of the")
    print("  observable.")
    print()

    print("  AND IT IS A LINEAGE, NOT A ONE-OFF. the same move, three more")
    print("  times, each one measuring a constant nobody can see:")
    print()
    print(f"  {'fluctuation':>26} {'relation':>26} {'yields':>14}")
    print("  " + "-" * 70)
    for a, b, cc in [
        ("Brownian motion (1905)", "<x^2> = 2Dt", "N_A"),
        ("Johnson-Nyquist noise (1928)", "<V^2> = 4 kT R df", "k_B"),
        ("shot noise (Schottky 1918)", "<I^2> = 2 e I df", "e"),
        ("blackbody fluctuation", "fluctuation-dissipation", "h"),
    ]:
        print(f"  {a:>26} {b:>26} {cc:>14}")
    print()
    print("  what these look like in a lab, forward only -- I am NOT")
    print("  'inverting to recover the constant', because I would be")
    print("  inverting a number I put in. that is a round trip, not a")
    print("  measurement, and calling it a check would be a lie:")
    print()
    Rr, T2, df = 1000.0, 300.0, 1.0e4
    v2 = 4 * kB * T2 * Rr * df
    I = 1e-6
    i2 = 2 * e * I * df
    print(f"  {'experiment':>34} {'signal to measure':>22}")
    print("  " + "-" * 60)
    print(f"  {'1 kOhm at 300 K over 10 kHz':>34} "
          f"{math.sqrt(v2)*1e9:>17.1f} nV")
    print(f"  {'1 uA junction over 10 kHz':>34} "
          f"{math.sqrt(i2)*1e12:>17.1f} pA")
    print()
    print("  400 nV and 57 pA. small, but 1928 and 1918 electronics reached")
    print("  them, and those are the numbers a real inversion for k_B and e")
    print("  works on. the point is the SIZE is attainable, which is the")
    print("  only part I can establish without a bench.")
    print()
    print("  NOISE IS NOT THE ERROR BAR. noise is where the constant lives.")
    print("  that is the lineage you put your finger on, and it is the")
    print("  opposite of how noise is usually treated.")
    print()


# ===================================== 2. what 4/3 is actually a dimension of

def part2():
    W = 78
    print("=" * W)
    print("  2. SO WHAT IS IT A DIMENSION OF, IF NOT SPACE OR TIME")
    print("=" * W)
    print()
    print("  you are right that it is neither, and the definition says so.")
    print("  read it slowly, because the answer is in the construction:")
    print()
    print("      the FRONTIER is the set of visited points that can be")
    print("      reached from infinity without crossing the walk")
    print()
    print("  that is not a geometric condition. nothing about position")
    print("  decides it. a point is on the frontier if and only if THE")
    print("  OUTSIDE CAN GET TO IT. a visited point one step away may be")
    print("  sealed in a fjord and is then not on the frontier, though it")
    print("  sits in the same place it always did.")
    print()
    print("  so 4/3 is the dimension of REACHABILITY-FROM-OUTSIDE.")
    print()
    print("  and that is the inside/outside pair this whole project is")
    print("  built on, with an exact value attached for the first time:")
    print()
    print(f"  {'in this project':>34} {'has a number?':>16}")
    print("  " + "-" * 52)
    for a, b in [
        ("inside resolver's proper time tau", "yes, 1.7738"),
        ("outside resolver's link count", "yes, an integer"),
        ("the cost asymmetry between them", "yes, 30760x"),
        ("the BOUNDARY between them", "4/3  <- new"),
    ]:
        print(f"  {a:>34} {b:>16}")
    print()
    print("  every earlier number was a property of one side, or of the")
    print("  machine running them. 4/3 is a property of the SEAM, and it is")
    print("  exact, and it needs no constants. that is why your instinct to")
    print("  stop at it was right.")
    print()
    print("  the whole family comes from one formula, dim = 1 + kappa/8:")
    print()
    print(f"  {'object':>34} {'kappa':>8} {'dimension':>12}")
    print("  " + "-" * 58)
    for nm, k, d in [
        ("loop-erased random walk", "2", "5/4"),
        ("self-avoiding walk (conj.)", "8/3", "4/3"),
        ("Brownian frontier", "8/3*", "4/3"),
        ("percolation cluster boundary", "6", "7/4"),
        ("pioneer points", "-", "7/4"),
        ("cut points", "-", "3/4"),
        ("the range itself", "8", "2"),
    ]:
        print(f"  {nm:>34} {k:>8} {d:>12}")
    print()
    print("  all exact rationals. no hbar, no c, no G, no alpha, nothing")
    print("  measured anywhere. * the frontier is not itself an SLE curve but")
    print("  its dimension coincides with SLE_8/3, which is the content of")
    print("  Lawler-Schramm-Werner.")
    print()


# ========================================== 3. the control, honestly reported

def sets(nsteps):
    st = rng.integers(0, 4, nsteps)
    dx = np.where(st == 0, 1, np.where(st == 1, -1, 0))
    dy = np.where(st == 2, 1, np.where(st == 3, -1, 0))
    x = np.cumsum(dx); y = np.cumsum(dy)
    x -= x.min(); y -= y.min()
    W_, H_ = x.max() + 3, y.max() + 3
    occ = np.zeros((W_, H_), bool); occ[x + 1, y + 1] = True
    ext = np.zeros_like(occ); q = deque([(0, 0)]); ext[0, 0] = True
    while q:
        i, j = q.popleft()
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            A, B = i + di, j + dj
            if 0 <= A < W_ and 0 <= B < H_ and not ext[A, B] and not occ[A, B]:
                ext[A, B] = True; q.append((A, B))
    pad = np.pad(ext, 1)
    adj = pad[:-2, 1:-1] | pad[2:, 1:-1] | pad[1:-1, :-2] | pad[1:-1, 2:]
    return (np.array(np.nonzero(occ)).T.astype(float),
            np.array(np.nonzero(occ & adj)).T.astype(float), max(W_, H_))


def bd(pts, diam, lo=1 / 256, hi=1 / 8, nb=10):
    bs = np.unique(np.round(np.geomspace(diam * lo, diam * hi, nb)).astype(int))
    bs = bs[bs >= 1]
    xs, ys = [], []
    for b in bs:
        k = np.unique((pts // b).astype(np.int64), axis=0)
        xs.append(math.log(1.0 / b)); ys.append(math.log(len(k)))
    xs = np.array(xs); ys = np.array(ys)
    A = np.vstack([xs, np.ones_like(xs)]).T
    return float(np.linalg.lstsq(A, ys, rcond=None)[0][0])


def part3():
    W = 78
    print("=" * W)
    print("  3. THE CONTROL, AND IT CONVICTS MY OWN MEASUREMENT")
    print("=" * W)
    print()
    print("  box-count an object whose dimension is KNOWN to be 2 -- the")
    print("  range itself -- with the same code and the same fit range:")
    print()
    print(f"  {'steps':>10} {'range dim':>11} {'true':>7} {'bias':>8} "
          f"{'frontier dim':>13} {'true':>8}")
    print("  " + "-" * 62)
    biases = []
    for n in (80000, 320000, 1280000):
        rg, fr, d = sets(n)
        r = bd(rg, d); f = bd(fr, d)
        biases.append(r - 2.0)
        print(f"  {n:>10} {r:>11.4f} {2.0:>7.4f} {r-2.0:>+8.4f} "
              f"{f:>13.4f} {4/3:>8.4f}")
    print()
    mb = sum(biases) / len(biases)
    print(f"  the method under-reads a known-2 object by {mb:+.4f}.")
    print()
    print("  SO MY FRONTIER NUMBERS WERE NEVER EVIDENCE. a code that returns")
    print("  1.72 for something that is exactly 2 cannot be trusted to")
    print("  distinguish 4/3 from 1.25 or 1.40. the readings sat below 4/3")
    print("  for exactly this reason and I should have run this control")
    print("  before quoting any of them, not after.")
    print()
    print("  (the bias is real and has a known cause: the number of distinct")
    print("  sites a planar walk visits in N steps grows like pi*N/log N, so")
    print("  the range is only dimension 2 in the limit and is logarithmically")
    print("  sparse at any finite N. a log correction is invisible to a")
    print("  power-law fit and shows up as a dimension deficit.)")
    print()
    print("  WHAT THAT LEAVES. the 4/3 is a THEOREM -- Lawler, Schramm and")
    print("  Werner, 2000, via Schramm's SLE. it does not need my")
    print("  confirmation and it did not get it. the right division of")
    print("  labour here is: the theorem supplies the number, and simulation")
    print("  is only good for checking that the object I built is the object")
    print("  the theorem is about. it is. that is all it showed.")
    print()


# ======================================================= 4. the history

def part4():
    W = 78
    print("=" * W)
    print("  4. THE HISTORY, SINCE YOU ASKED WHERE IT COMES FROM")
    print("=" * W)
    print()
    rows = [
        ("1827", "Robert Brown",
         "pollen in water jitters. he checks dead matter"),
        ("", "", "and ground glass too -- so it is not life"),
        ("1905", "Einstein", "<x^2> = 2Dt, and D contains N_A"),
        ("1906", "Smoluchowski", "independent derivation, kinetic route"),
        ("1908-13", "Perrin", "measures it, inverts for N_A, atoms are real"),
        ("1923", "Wiener", "Wiener measure: the walk becomes a"),
        ("", "", "rigorous mathematical object"),
        ("1940s-50s", "Levy, Kakutani,",
         "the range has dimension 2; cut points,"),
        ("", "Dvoretzky, Erdos", "double points, the fine structure"),
        ("1982", "Mandelbrot", "CONJECTURES the frontier is exactly 4/3,"),
        ("", "", "from simulation and the look of it"),
        ("1999", "Schramm", "SLE -- a one-parameter family of random"),
        ("", "", "curves, conformally invariant by construction"),
        ("2000", "Lawler, Schramm,", "PROVES the frontier is 4/3"),
        ("", "Werner", "(math/0010165)"),
        ("2006", "Fields Medal", "Werner"),
        ("2010", "Fields Medal", "Smirnov, for the lattice-to-SLE limit"),
    ]
    print(f"  {'when':>10} {'who':>18} {'what':>44}")
    print("  " + "-" * 76)
    for a, b, c in rows:
        print(f"  {a:>10} {b:>18} {c:>44}")
    print()
    print("  TWO THINGS IN THAT TABLE WORTH MORE THAN THE REST.")
    print()
    print("  Brown's control. he is remembered for seeing the jitter, but")
    print("  the reason it counted is that he ground up glass and window")
    print("  panes and old wood and watched those jitter too. the obvious")
    print("  reading was 'the pollen is alive'. he killed that himself.")
    print("  the discovery is the control, not the observation.")
    print()
    print("  the 173-year gap. 1827 to 2000. Mandelbrot saw 4/3 in 1982 and")
    print("  could not prove it; it took inventing an entirely new object")
    print("  (SLE) to get there, and the proof is not a harder version of")
    print("  the simulation -- it is a different subject. seeing a number")
    print("  and owning it are separated by that much.")
    print()
    print("  AND THE ANSWER TO YOUR ACTUAL QUESTION. you asked what else.")
    print("  the answer is the second table in part 1: the method generalises.")
    print("  Einstein's move was not 'atoms exist' -- it was FLUCTUATIONS")
    print("  CARRY THE CONSTANTS. do it with voltage across a resistor and")
    print("  you get k_B. with current across a junction, e. the jitter is")
    print("  not what obscures the measurement; the jitter IS the")
    print("  measurement. that is the thing to take, and it is older and")
    print("  larger than the 4/3.")


def main():
    part1()
    part2()
    part3()
    part4()


if __name__ == "__main__":
    main()
