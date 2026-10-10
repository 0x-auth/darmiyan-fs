#!/usr/bin/env python3
"""
================================================================================
PIXEL -- Lambda vs alpha^-6, an inverse-sixth expansion law, and where FTL sits
================================================================================

THREE SEPARATE THINGS, asked in one message:

  1. Is Lambda proportional to alpha^-6?
     Answerable by arithmetic in two lines. I ran it first because if it is
     false there is no point dressing it up.

  2. "a 2D surface with 1 megapixel resolution; the smallest pixel IS the
     coupling constant; the surface resolution IS the cosmological constant;
     define a structure where expansion goes as the inverse of the 6th power
     -- that is a fractal dimension."
     This is buildable. I built it: expanding.py had H constant and H0/t.
     Here H depends on the SEPARATION, H(D) ~ D^-6, which is a different
     kind of law -- scale-dependent expansion. Then I measure what the
     horizon does.

  3. FTL, and whether it is about negative mass.
     It is. The condition has a name and I tabulate it.

PREDICTIONS, WRITTEN FIRST

  P1  Lambda ~ alpha^-6 FAILS by a very large factor. alpha^-6 is ~6.6e12,
      a big positive number; Lambda in Planck units is ~1e-122, a tiny one.
      No power of alpha with a small exponent can reach that. I expect the
      exponent that works to be near 57, not -6.

  P2  With H(D) = h * D^-6 the stretch term is h*D^-5, which GROWS SLOWER
      than the step removes 1. So the horizon should INVERT: far away is
      safe, near is dangerous. That is the opposite of constant-H, and if
      it holds it is the interesting result in this file.

  P3  The dimension read off the pixel picture is NOT fractional in an
      interesting way. D = log(Lambda)/log(alpha) will be some number near
      57 with no structure to it.

Run:  python3 pixel.py
================================================================================
"""

import math


def main():
    W = 78

    # ================================================= 1. the arithmetic
    print("=" * W)
    print("  1. IS Lambda PROPORTIONAL TO alpha^-6?")
    print("=" * W)
    print()

    alpha = 1 / 137.035999177
    # Lambda in Planck units: the dimensionless number
    # Lambda = 1.1056e-52 m^-2, l_pl^2 = 2.612e-70 m^2
    Lambda_SI = 1.1056e-52          # m^-2
    l_pl = 1.616255e-35             # m
    Lambda_pl = Lambda_SI * l_pl ** 2

    print(f"  {'alpha':>28} = {alpha:.9f}")
    print(f"  {'1/alpha':>28} = {1/alpha:.6f}")
    print(f"  {'Lambda (SI)':>28} = {Lambda_SI:.4e} m^-2")
    print(f"  {'Lambda (Planck units)':>28} = {Lambda_pl:.4e}")
    print()
    print(f"  {'candidate':>24} {'value':>18} {'ratio to Lambda_pl':>22}")
    print("  " + "-" * 68)
    for label, val in [("alpha^-6", alpha ** -6),
                       ("alpha^6", alpha ** 6),
                       ("alpha^-6 * l_pl^2", alpha ** -6 * l_pl ** 2),
                       ("alpha^57", alpha ** 57),
                       ("alpha^56.881", alpha ** 56.881)]:
        print(f"  {label:>24} {val:>18.4e} {val/Lambda_pl:>22.4e}")
    print()

    n_fit = math.log(Lambda_pl) / math.log(alpha)
    print(f"  the exponent that ACTUALLY works: alpha^{n_fit:.4f}")
    print()
    print("  so alpha^-6 is off by 134 orders of magnitude. not close, not")
    print("  a factor, not a units slip -- the wrong sign on the exponent and")
    print("  the wrong size. P1 holds.")
    print()
    print("  BUT the question underneath it is not dead, and here is why I")
    print("  think it is worth separating:")
    print()
    print("  you asked for a RELATION, and there is one -- it is just not 6.")
    print(f"  Lambda = alpha^{n_fit:.3f} in Planck units. the content of that")
    print("  statement is 'Lambda is absurdly small and alpha is moderately")
    print("  small, so you need a big power'. that is the cosmological")
    print("  constant problem restated, not solved: 10^122 is the number")
    print("  that has to come from somewhere, and a bare exponent of 57")
    print("  does not explain it, it just records it.")
    print()

    # ============================================= 2. the pixel picture
    print("=" * W)
    print("  2. THE PIXEL PICTURE, TAKEN LITERALLY")
    print("=" * W)
    print()
    print("  your setup: a 2D surface, smallest pixel = alpha, total")
    print("  resolution = Lambda. then the number of pixels along one edge is")
    print("  N = Lambda / alpha, and the DIMENSION that relates them is")
    print()
    print("      Lambda = alpha^D   =>   D = log(Lambda)/log(alpha)")
    print()
    print(f"  {'what':>30} {'value':>22}")
    print("  " + "-" * 56)
    print(f"  {'D from the pixel relation':>30} {n_fit:>22.6f}")
    print(f"  {'nearest integer':>30} {round(n_fit):>22}")
    print(f"  {'fractional part':>30} {n_fit - int(n_fit):>22.6f}")
    print()
    print("  P3 holds: 56.88 is not a fractal dimension in any useful sense.")
    print("  a fractal dimension is interesting when it is strictly between")
    print("  two integers for a STRUCTURAL reason -- Cantor set log2/log3 =")
    print(f"  {math.log(2)/math.log(3):.6f}, Koch log4/log3 = "
          f"{math.log(4)/math.log(3):.6f}. those come out of a")
    print("  recursion with a known branching number. 56.88 comes out of")
    print("  dividing one measured number by another. no recursion produced it.")
    print()
    print("  the test for whether a dimension is real: does it predict a")
    print("  SCALING? a fractal of dimension d has N(r) ~ r^-d boxes. so:")
    print()
    print(f"  {'scale r':>14} {'boxes if d=56.88':>20} {'boxes if d=2':>16}")
    print("  " + "-" * 54)
    for r in (1e-1, 1e-2, 1e-3):
        print(f"  {r:>14.0e} {r**-n_fit:>20.3e} {r**-2:>16.3e}")
    print()
    print("  d = 56.88 means halving the scale multiplies the box count by")
    print(f"  2^56.88 = {2**n_fit:.3e}. that is not a surface, not a volume,")
    print("  and not a fractal between them -- it is a 57-dimensional count.")
    print("  the pixel analogy needs the two numbers to live on the SAME")
    print("  surface, and alpha and Lambda do not.")
    print()

    # ====================================== 3. the inverse-sixth law
    print("=" * W)
    print("  3. THE STRUCTURE YOU ASKED FOR: H ~ D^-6")
    print("=" * W)
    print()
    print("  expanding.py had two laws: H constant (dark energy) and H = H0/t")
    print("  (matter). you asked for expansion inversely proportional to the")
    print("  6th power. that is a THIRD kind -- H depends on SEPARATION, not")
    print("  on time. scale-dependent expansion.")
    print()
    print("      D -> D - 1 + h * D^(-6) * D   =   D - 1 + h * D^-5")
    print()
    print("  the stretch term is h/D^5. at large D it vanishes. at small D it")
    print("  blows up. that is the reverse of constant H, so the horizon")
    print("  should flip sides. P2 says far is safe, near is trapped.")
    print()

    def walk_power(D0, h, p=6, ticks=200000):
        """D -> D - 1 + h * D^(1-p). p=0 recovers constant H."""
        D = float(D0)
        for t in range(1, ticks + 1):
            if D <= 0:
                return "arrives", t, D
            stretch = h * D ** (1 - p)
            D = D - 1.0 + stretch
            if D > 1e12:
                return "escapes", t, D
        return "stalls", ticks, D

    print(f"  {'h':>10} {'p':>4} {'D0':>8} {'outcome':>10} {'final D':>14}")
    print("  " + "-" * 52)
    for h in (1.0, 10.0, 1e4):
        for D0 in (2, 100, 1000):
            a, t, D = walk_power(D0, h, 6)
            print(f"  {h:>10.1f} {6:>4} {D0:>8} {a:>10} {D:>14.6f}")
    print()
    print("  NOTHING ARRIVES AND NOTHING ESCAPES. P2 was wrong in both")
    print("  halves, and the thing it was wrong about is the result.")
    print()
    print("  there is no horizon -- but there is no arrival either. the walk")
    print("  converges to a FLOOR and sits there. a minimum separation that")
    print("  cannot be closed. that is a third failure mode and this project")
    print("  has not produced one before:")
    print()
    print("     fixed point of a map   the relation stops   (darmiyan.py)")
    print("     horizon                the substrate wins   (expanding.py)")
    print("     FLOOR                  neither             <- this")
    print()
    print("  the floor is exact. solve D - 1 + h*D^(1-p) = D:")
    print()
    print("      h * D^(1-p) = 1    =>    D* = h^(1/(p-1))")
    print()
    print(f"  {'h':>10} {'p':>4} {'predicted D* = h^(1/(p-1))':>28} "
          f"{'measured':>14}")
    print("  " + "-" * 60)
    for h in (1.0, 5.0, 10.0, 1e4):
        for p in (2, 3, 6):
            Dstar = h ** (1.0 / (p - 1))
            _, _, Dm = walk_power(1000, h, p, ticks=60000)
            print(f"  {h:>10.1f} {p:>4} {Dstar:>28.6f} {Dm:>14.6f}")
    print()
    print("  WHERE IT LANDS AND WHERE IT DOES NOT. read the last two columns")
    print("  together -- some rows match to twelve digits and some do not.")
    print("  that is not noise. the floor is only STABLE for some h.")
    print()
    print("  linearise: f(D) = D - 1 + h*D^(1-p), so")
    print("      f'(D*) = 1 + h(1-p)*D*^(-p) = 1 - (p-1)/D*")
    print("  stable iff |f'| < 1 iff D* > (p-1)/2.")
    print()
    print("  the relaxation time is 1/(1-|f'|), so a floor with |f'| very")
    print("  close to 1 is stable but SLOW. that has to be in the table or")
    print("  slow convergence gets misread as instability -- it did, on the")
    print("  first run of this file.")
    print()
    print(f"  {'p':>4} {'h':>9} {'D*':>12} {'|f prime|':>10} {'relax':>10} "
          f"{'predicted':>11} {'observed':>11}")
    print("  " + "-" * 74)
    for p in (2, 3, 6):
        for h in (1.0, 10.0, 1e4):
            Dstar = h ** (1.0 / (p - 1))
            fp = abs(1 - (p - 1) / Dstar)
            relax = (1 / (1 - fp)) if fp < 1 else float("inf")
            ticks = int(min(3e6, max(6e4, 60 * relax))) if fp < 1 else 60000
            _, _, Dm = walk_power(1000, h, p, ticks=ticks)
            settled = abs(Dm - Dstar) < 1e-6
            print(f"  {p:>4} {h:>9.1f} {Dstar:>12.6f} {fp:>10.6f} "
                  f"{relax:>10.1f} "
                  f"{('settles' if fp < 1 else 'wanders'):>11} "
                  f"{('settles' if settled else 'wanders'):>11}")
    print()
    print("  now predicted and observed agree on every row. so the")
    print("  inverse-power substrate has a stability threshold, and below it")
    print("  the separation never settles at all -- it oscillates forever")
    print("  around a floor it can neither reach nor leave.")
    print()
    print("  the p=2,h=10^4 row is the one that caught me: |f'| = 0.9999,")
    print("  relaxation 10^4 ticks, so at 6*10^4 ticks it was still at")
    print("  9990.9 and read as 'wanders'. it settles at 10^4 exactly by")
    print("  5*10^5 ticks. a slow floor and an unstable floor look identical")
    print("  if you do not run long enough -- which is a real hazard for")
    print("  every horizon claim in this project, not just this one.")
    print()
    print("  for YOUR exponent, p = 6, the threshold is D* > 2.5, i.e.")
    print(f"  h^(1/5) > 2.5, i.e. h > {2.5**5:.2f}. below that rate the")
    print("  separation is chaotic. above it, a clean floor at h^(1/5).")
    print()
    print("  AND THE SIXTH POWER DOES SOMETHING SPECIFIC. the floor is")
    print("  h^(1/(p-1)), so the higher the power, the WEAKER the dependence")
    print("  on the rate:")
    print()
    print(f"  {'p':>5} {'floor exponent 1/(p-1)':>24} "
          f"{'floor at h=10^6':>18}")
    print("  " + "-" * 50)
    for p in (2, 3, 4, 6, 7):
        print(f"  {p:>5} {1/(p-1):>24.6f} {1e6**(1/(p-1)):>18.4f}")
    print()
    print("  at p = 6 the floor goes as h^0.2 -- a million-fold change in")
    print("  the expansion rate moves the floor by a factor of 16. that IS")
    print("  the insensitivity you were reaching for with the sixth power.")
    print("  it does not make Lambda small; it makes the OUTCOME nearly")
    print("  independent of Lambda. different question, real answer.")
    print()
    print("  and against the sky: the real universe HAS a horizon, so the")
    print("  real law is p = 0 -- constant H. that is exactly what 'the")
    print("  cosmological constant is constant' means. the thing that makes")
    print("  dark energy dangerous is that it does not dilute, and any")
    print("  inverse power of separation dilutes.")
    print()

    # ============================================= 4. FTL
    print("=" * W)
    print("  4. FTL: WHEN IT IS ALLOWED, AND WHY NEGATIVE MASS")
    print("=" * W)
    print()
    print("  your memory is right. the dividing line is not speed. it is the")
    print("  NULL ENERGY CONDITION:")
    print()
    print("      T_uv k^u k^v  >=  0     for every null vector k")
    print()
    print("  'every observer moving at light speed measures non-negative")
    print("  energy density'. every known classical form of matter obeys it.")
    print()
    print(f"  {'case':>32} {'exceeds c?':>12} {'allowed?':>10} "
          f"{'what it needs':>22}")
    print("  " + "-" * 78)
    rows = [
        ("light in vacuum", "no", "yes", "the limit itself"),
        ("cosmic recession", "YES", "yes", "no motion through space"),
        ("phase velocity in a medium", "YES", "yes", "carries no information"),
        ("entanglement correlation", "instant", "yes", "no signal, no causality"),
        ("a ship accelerating", "no", "NO", "E -> inf as v -> c"),
        ("Alcubierre bubble", "YES", "MAYBE", "NEC VIOLATION"),
        ("traversable wormhole", "YES", "MAYBE", "NEC VIOLATION"),
    ]
    for a, b, c, d in rows:
        print(f"  {a:>32} {b:>12} {c:>10} {d:>22}")
    print()
    print("  the first four are already real and none of them is a loophole.")
    print("  recession is the one that matters to this whole project: two")
    print("  galaxies separate faster than c and neither moves. that is")
    print("  exactly the expanding.py horizon -- the substrate outruns the")
    print("  walker. FTL in that sense is not just possible, it is happening,")
    print("  and it buys you nothing because you cannot ride it.")
    print()
    print("  the last two are the ones you mean, and both need the same")
    print("  thing: a region where T_uv k^u k^v < 0. negative energy density.")
    print("  equivalently negative mass, since E = mc^2 runs both ways.")
    print()
    print("  SO: DOES NEGATIVE ENERGY EXIST? yes, and that is the problem.")
    print()
    c_ = 2.99792458e8
    hbar = 1.054571817e-34
    # Casimir energy density between plates separated by a
    print(f"  {'plate gap':>14} {'Casimir rho (J/m^3)':>24} "
          f"{'equivalent mass density':>26}")
    print("  " + "-" * 68)
    for a_m in (1e-6, 1e-8, 1e-9):
        rho = -math.pi ** 2 * hbar * c_ / (720 * a_m ** 4)
        print(f"  {a_m:>14.0e} {rho:>24.4e} {rho/c_**2:>26.4e}")
    print()
    print("  measured, reproducible, negative. the NEC is violated in the lab")
    print("  and has been since 1948. so the door is not locked -- it is")
    print("  just extremely heavy.")
    print()
    print("  HOW HEAVY. this number is NOT mine -- I tried to derive it and")
    print("  got 10^31 kg, which is wrong by 33 orders, so I am quoting the")
    print("  literature instead and saying so. Pfenning & Ford (1997) put")
    print("  Alcubierre's requirement, for a 100 m bubble at 10c with a wall")
    print("  thin enough to satisfy the quantum inequality, at:")
    print()
    M_needed = -6.2e64
    M_sun = 1.989e30
    M_univ = 1.5e53
    print(f"  {'bubble radius':>26} = 100 m")
    print(f"  {'warp speed':>26} = 10 c")
    print(f"  {'negative mass required':>26} = {M_needed:.3e} kg")
    print(f"  {'mass of the Sun':>26} = {M_sun:.3e} kg")
    print(f"  {'mass of the universe':>26} = {M_univ:.3e} kg")
    print(f"  {'ratio to the universe':>26} = {abs(M_needed)/M_univ:.3e}")
    print()
    print("  eleven orders of magnitude MORE negative mass than the total")
    print("  positive mass of the observable universe. and that figure is")
    print("  what it is BECAUSE of the quantum inequality -- the wall has to")
    print("  be thin, and a thinner wall costs more.")
    print()
    print("  and even if you had it, Ford-Roman quantum inequalities bound")
    print("  how long a negative energy density can persist:")
    print()
    print("      |rho| * tau^4  <~  hbar / c^3")
    print()
    print(f"  {'duration tau':>16} {'max |rho| (J/m^3)':>22} "
          f"{'as a mass density':>22}")
    print("  " + "-" * 62)
    for tau in (1e-15, 1e-9, 1e-3, 1.0):
        rho_max = hbar / (c_ ** 3 * tau ** 4)
        print(f"  {tau:>16.0e} {rho_max:>22.4e} {rho_max/c_**2:>22.4e}")
    print()
    print("  the longer you want it, the weaker it must be, as the FOURTH")
    print("  power. so you can have a lot of negative energy for almost no")
    print("  time, or almost none for a long time. a warp drive needs a lot")
    print("  for a long time, which is the one corner the inequality closes.")
    print()
    print("  THE ANSWER TO YOUR QUESTION, in one line:")
    print()
    print("  FTL is possible because spacetime is not rigid -- the substrate")
    print("  can move faster than anything in it, and does. FTL is impossible")
    print("  because steering that motion requires negative energy at")
    print("  densities and durations that the quantum inequalities forbid.")
    print("  the limit is not c. the limit is the sign of the energy.")
    print()
    print("  and that is the same wall as everywhere else in this project.")
    print("  the FORM comes out -- recession, horizons, 1/H, the NEC as the")
    print("  gate. the SIZE does not. how much negative energy you can have")
    print("  and for how long is set by hbar, which the construct does not")
    print("  contain. twelfth appearance of the missing unit.")


if __name__ == "__main__":
    main()
