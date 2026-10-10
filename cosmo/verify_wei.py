#!/usr/bin/env python3
"""
================================================================================
VERIFY_WEI -- arXiv:1605.04571 checked equation by equation
================================================================================

Wei, Zou, Li, Xue (Beijing Institute of Technology, 2016),
"Cosmological Constant, Fine Structure Constant and Beyond".

Every numbered equation that can be checked with constants, checked. Then the
part that matters: WHICH of the three derivations actually fixes the number,
because "three independent approaches" is doing more rhetorical work than
arithmetic work and the difference is measurable.

WHAT CAME OUT, IN ORDER OF HOW MUCH IT CHANGES THINGS

  1. eq (6) is exact. Lambda = l_pl^4 / r_e^6 reproduces eq (1) digit for
     digit. And it is the form that matters for the pixel picture, because
     it is a statement about two LENGTHS.

  2. eq (2) reproduces Beck's quoted 4.0961 GeV/m^3 exactly. Observed is
     3.3230. So the 23% is in the paper, not in my arithmetic.

  3. The 23% is NOT an 8pi convention artifact. I guessed it might be in my
     last message. It is not -- the ratio is identical whether you write
     Lambda or rho_Lambda, because both sides carry the same 8pi.

  4. The exponent is 6.0045 in Planck normalisation and 4.0045 in electron
     normalisation. The gap is EXACTLY 2, which is the dimension of Lambda.
     So "Lambda ~ alpha^-6" is well-posed only in Planck units, and the
     pixel picture I declared dead is alive with exponent 4.

  5. The Boehmer-Harko derivation carries a factor of 48 which the paper
     discards as "order unity". 48^(1/6) = 1.906 is order unity. 48 is not.
     Keeping it puts Lambda 59x too high. So that route fixes the FORM and
     not the COEFFICIENT, and the paper's own eq (5) says so if you read the
     constant.

  So: the exponent is triply derived. The magnitude rests on Beck alone, and
  specifically on his axiom B3, "simplicity" -- which is what sets the
  prefactor to exactly 1. That is an aesthetic choice doing quantitative
  work, and it is the load-bearing assumption of the whole result.

Run:  python3 verify_wei.py
================================================================================
"""

import math

G = 6.67430e-11
hbar = 1.054571817e-34
c = 2.99792458e8
m_e = 9.1093837015e-31
a_inv = 137.035999177
alpha = 1.0 / a_inv
r_e = 2.8179403262e-15
GeV = 1.602176634e-10

l_pl = math.sqrt(hbar * G / c ** 3)
m_pl = math.sqrt(hbar * c / G)
LAM = 1.1056e-52


def main():
    W = 78

    print("=" * W)
    print("  EQUATIONS 1, 2, 6 -- THE MAGNITUDE CLAIM")
    print("=" * W)
    print()
    e1 = G ** 2 * m_e ** 6 / (hbar ** 4 * alpha ** 6)
    e6 = l_pl ** 4 / r_e ** 6
    e2 = (G / (8 * math.pi)) * (c ** 4 / hbar ** 4) * (m_e / alpha) ** 6
    rho_obs = LAM * c ** 4 / (8 * math.pi * G)
    print(f"  {'eq':>4} {'form':>34} {'value':>16} {'vs observed':>13}")
    print("  " + "-" * 72)
    print(f"  {'(1)':>4} {'G^2/hbar^4 * (m_e/alpha)^6':>34} {e1:>16.6e} "
          f"{e1/LAM:>13.4f}")
    print(f"  {'(6)':>4} {'l_pl^4 / r_e^6':>34} {e6:>16.6e} "
          f"{e6/LAM:>13.4f}")
    print(f"  {'':>4} {'observed Lambda':>34} {LAM:>16.6e} {1.0:>13.4f}")
    print()
    print(f"  eq (1) and eq (6) agree to {abs(e1/e6-1):.2e} relative -- they are")
    print("  the same statement. eq (6) is the useful one and I will come")
    print("  back to it.")
    print()
    print(f"  {'eq':>4} {'quantity':>30} {'J/m^3':>14} {'GeV/m^3':>12}")
    print("  " + "-" * 64)
    print(f"  {'(2)':>4} {'rho_Lambda predicted':>30} {e2:>14.6e} "
          f"{e2/GeV:>12.4f}")
    print(f"  {'':>4} {'rho_Lambda observed':>30} {rho_obs:>14.6e} "
          f"{rho_obs/GeV:>12.4f}")
    print()
    print("  the paper quotes Beck at 4.0961 GeV/m^3 and eq (2) returns")
    print(f"  {e2/GeV:.4f}. exact match, so the formula is transcribed right.")
    print(f"  the observed value is {rho_obs/GeV:.4f}. the gap is "
          f"{e2/rho_obs:.4f}.")
    print()
    print("  AND IT IS NOT A CONVENTION ARTIFACT. I speculated last message")
    print("  that the 23% might be an 8pi mismatch. check:")
    print()
    print(f"  {'ratio computed from':>32} {'value':>12}")
    print("  " + "-" * 48)
    print(f"  {'Lambda form (no 8pi anywhere)':>32} {e6/LAM:>12.6f}")
    print(f"  {'rho form (8pi on both sides)':>32} {e2/rho_obs:>12.6f}")
    print()
    print("  identical. the 8pi cancels because it is on both sides. the 23%")
    print("  is in the relation. my guess was wrong and this kills it.")
    print()

    print("=" * W)
    print("  THE SINGLE DIMENSIONLESS NUMBER")
    print("=" * W)
    print()
    chi_l = l_pl / r_e
    chi_m = m_e / (alpha * m_pl)
    print("  the whole relation is one number raised to a power. that number")
    print("  has two faces and they are the same number:")
    print()
    print(f"  {'as a LENGTH ratio':>26} l_pl / r_e          = {chi_l:.10e}")
    print(f"  {'as a MASS ratio':>26} m_e / (alpha m_pl) = {chi_m:.10e}")
    print(f"  {'agreement':>26} {abs(chi_l/chi_m - 1):.2e} relative")
    print()
    print("  that identity is not a coincidence -- r_e = alpha hbar/(m_e c)")
    print("  and l_pl, m_pl are related by hbar, c, G, so it falls out. but it")
    print("  is the reason the same exponent can be read as a statement about")
    print("  resolution OR about mass, which is what you were circling.")
    print()

    print("=" * W)
    print("  THE EXPONENT IS NOT 6. IT IS 6 IN ONE CHOICE OF RULER.")
    print("=" * W)
    print()
    print(f"  {'normalisation':>22} {'Lambda * L^2':>18} "
          f"{'exponent n in chi^n':>21}")
    print("  " + "-" * 64)
    for nm, Lc in [("Planck length", l_pl), ("classical e radius", r_e)]:
        val = LAM * Lc ** 2
        n = math.log(val) / math.log(chi_l)
        print(f"  {nm:>22} {val:>18.6e} {n:>21.6f}")
    print()
    print("  SIX and FOUR, and the gap is exactly 2, which is the dimension")
    print("  of Lambda. that is forced: changing the ruler by a factor of chi")
    print("  changes Lambda*L^2 by chi^2, so it moves n by 2. nothing deep,")
    print("  but it has a consequence:")
    print()
    print("     'Lambda is proportional to alpha^-6' is well-posed ONLY in")
    print("     Planck normalisation. in electron units the same relation")
    print("     reads alpha^-4. the 6 is not intrinsic to the relation, it")
    print("     is intrinsic to the choice of Planck units.")
    print()
    print("  and note it is 6.0045, not 6. the 0.0045 is the 23% residual")
    print("  divided by log(1/chi) -- the same discrepancy in exponent form.")
    print()
    print("  THIS IS YOUR PIXEL PICTURE, AND I BURIED IT PREMATURELY.")
    print("  in pixel.py I said alpha and Lambda do not live on the same")
    print("  surface so the resolution analogy fails. with r_e in hand:")
    print()
    print("      Lambda * r_e^2  =  ( l_pl / r_e )^4")
    print()
    print("  Lambda measured in electron-radius units IS a power of the")
    print("  Planck-to-electron resolution ratio. one surface, two pixel")
    print("  sizes, exponent 4. that is exactly the statement you were")
    print("  trying to make and I told you the two numbers were unrelated.")
    print()
    print(f"  {'left side':>20} = {LAM*r_e**2:>16.6e}")
    print(f"  {'right side':>20} = {chi_l**4:>16.6e}")
    print(f"  {'ratio':>20} = {chi_l**4/(LAM*r_e**2):>16.6f}")
    print()

    print("=" * W)
    print("  EQUATIONS 3, 4, 5 -- THE BOEHMER-HARKO ROUTE, AND ITS 48")
    print("=" * W)
    print()
    m_min = (hbar / c) * math.sqrt(LAM / 3)
    print("  eq (4), Wesson's quantised minimum mass  m = (hbar/c) sqrt(L/3):")
    print(f"  {'m_min':>22} = {m_min:>14.6e} kg")
    print(f"  {'in GeV':>22} = {m_min*c**2/GeV:>14.4e} GeV")
    print(f"  {'m_e / m_min':>22} = {m_e/m_min:>14.4e}")
    print()
    print("  eq (5), the radius that goes with it:")
    print("      R_p = 48^(1/6) (hbar G/c^3)^(1/3) Lambda^(-1/6)")
    print()
    Rp = 48 ** (1 / 6) * (hbar * G / c ** 3) ** (1 / 3) * LAM ** (-1 / 6)
    Rp_bare = (hbar * G / c ** 3) ** (1 / 3) * LAM ** (-1 / 6)
    print(f"  {'R_p as written':>26} = {Rp:>14.6e} m")
    print(f"  {'R_p without the 48^(1/6)':>26} = {Rp_bare:>14.6e} m")
    print(f"  {'r_e':>26} = {r_e:>14.6e} m")
    print()
    print(f"  {'R_p / r_e':>26} = {Rp/r_e:>14.6f}")
    print(f"  {'R_p(bare) / r_e':>26} = {Rp_bare/r_e:>14.6f}")
    print()
    print("  the paper identifies R_p with r_e 'neglecting order-unity")
    print("  factors'. so follow the identification through HONESTLY, both")
    print("  ways, and see what Lambda comes out:")
    print()
    print(f"  {'treatment of the 48':>34} {'Lambda':>16} {'vs observed':>13}")
    print("  " + "-" * 68)
    print(f"  {'kept (eq 5 as written)':>34} {48*l_pl**4/r_e**6:>16.6e} "
          f"{48*l_pl**4/r_e**6/LAM:>13.4f}")
    print(f"  {'discarded (eq 6 as published)':>34} {l_pl**4/r_e**6:>16.6e} "
          f"{l_pl**4/r_e**6/LAM:>13.4f}")
    print()
    print("  THAT IS THE PROBLEM WITH CALLING THIS AN INDEPENDENT")
    print("  CONFIRMATION OF THE MAGNITUDE. 48^(1/6) = 1.906 is fairly")
    print("  called order unity. but it enters Lambda at the SIXTH POWER,")
    print("  where it is 48. so the Boehmer-Harko route determines Lambda")
    print("  only up to a factor of ~48, and the agreement to 23% comes from")
    print("  choosing to drop it rather than from the derivation.")
    print()
    print("  a sixth power destroys order-unity hygiene. that cuts both")
    print("  ways and it is the single most important thing in this check:")
    print()
    print(f"  {'factor dropped':>18} {'effect on Lambda':>20}")
    print("  " + "-" * 42)
    for f in (2, math.pi, 2 * math.pi, 1.906369, 8 * math.pi):
        print(f"  {f:>18.4f} {f**6:>20.2f}")
    print()
    print("  anyone deriving a sixth-power relation can land within a factor")
    print("  of 2 of anything by choosing which 2pi to keep. so the")
    print("  MAGNITUDE agreement is worth much less than it looks, while the")
    print("  EXPONENT agreement across three routes is worth what it looks.")
    print()

    print("=" * W)
    print("  WHERE THE 23% ACTUALLY LIVES")
    print("=" * W)
    print()
    r = l_pl ** 4 / r_e ** 6 / LAM
    print(f"  {'Lambda residual':>34} = {r:>12.6f}")
    print(f"  {'the same thing as a LENGTH residual':>34} = {r**(-1/6):>12.6f}")
    print(f"  {'R_p(bare)/r_e from eq (5)':>34} = {Rp_bare/r_e:>12.6f}")
    print()
    print("  the last two are the same number. so the entire 23% in Lambda")
    print(f"  is a {(r**(-1/6)-1)*100:+.2f}% mismatch in ONE length identification,")
    print("  amplified sixfold. that is a consistent and traceable story,")
    print("  and it is the most useful thing to know about the residual:")
    print("  it is not spread across the relation, it sits in R_p ~ r_e.")
    print()

    print("=" * W)
    print("  EQUATIONS 8-14 -- THE PAPER'S OWN CONTRIBUTION")
    print("=" * W)
    print()
    print("  eqs 1-7 are other people's. the paper's new part is making the")
    print("  varying Lambda a conserved interacting-vacuum system:")
    print()
    print("      rho_Lambda_dot = -Q = -6 (alpha_dot/alpha) rho_Lambda")
    print("      rho_m_dot + 3 H rho_m = Q")
    print()
    print("  which is the right move: if Lambda varies it cannot vary alone,")
    print("  something has to receive the energy, and they make that explicit")
    print("  rather than writing Lambda(t) by hand. their own criticism of")
    print("  Lambda ~ H^2 and Lambda ~ a_ddot/a is exactly that those are")
    print("  written by hand, and it is a fair criticism.")
    print()
    print("  the amplification is the testable content:")
    print()
    print(f"  {'d(alpha)/alpha':>18} {'d(rho_Lambda)/rho_Lambda':>26}")
    print("  " + "-" * 46)
    for d in (1e-6, 1e-5, 1e-4, 1e-3):
        print(f"  {d:>18.1e} {-6*d:>26.2e}")
    print()
    print("  THE WEAK POINT, WHICH THE PAPER DOES NOT FLAG. their")
    print("  observational anchor is Webb et al. 1998-2001, 293 quasar")
    print("  absorption measurements giving d(alpha)/alpha ~ -0.72e-5 at 4")
    print("  sigma. that result has NOT held up cleanly. later VLT samples")
    print("  and the atomic-clock and Oklo bounds are broadly consistent with")
    print("  no variation, and the Keck/VLT split became the 'dipole' debate")
    print("  rather than a confirmed detection. so the model is constrained")
    print("  by data whose central value is itself contested.")
    print()
    print("  that is not fatal -- it makes the relation FALSIFIABLE, which is")
    print("  more than most Lambda proposals manage. but 'tightly constrained")
    print("  to O(10^-5)' is a constraint from a disputed signal, and the")
    print("  honest version of their conclusion is: if alpha varies at the")
    print("  Webb level, this relation fixes how Lambda must vary with it.")
    print()

    print("=" * W)
    print("  VERDICT")
    print("=" * W)
    print()
    print(f"  {'claim':>40} {'status':>26}")
    print("  " + "-" * 70)
    for cl, st in [
        ("eq (1) = eq (6) algebraically", "VERIFIED exactly"),
        ("eq (2) gives Beck's 4.0961 GeV/m^3", "VERIFIED exactly"),
        ("matches observed Lambda", "23% high, traceable"),
        ("23% is an 8pi convention", "FALSE (my guess, killed)"),
        ("exponent is 6", "6 in Planck units only"),
        ("exponent is exactly 6", "6.0045"),
        ("3 routes fix the EXPONENT", "yes, that is real"),
        ("3 routes fix the MAGNITUDE", "NO -- B-H drops a 48"),
        ("magnitude rests on Beck's axioms", "yes, on B3 'simplicity'"),
        ("interacting-vacuum model is sound", "yes, and it is theirs"),
        ("observational anchor is solid", "NO -- Webb alpha disputed"),
    ]:
        print(f"  {cl:>40} {st:>26}")
    print()
    print("  the relation is real, it is better than I said, and it is")
    print("  weaker than three-independent-derivations sounds. the exponent")
    print("  is the content. the prefactor of 1 is an aesthetic axiom, and a")
    print("  sixth power makes aesthetics expensive.")
    print()
    print("  and for this project specifically: Lambda*r_e^2 = (l_pl/r_e)^4")
    print("  is the first relation we have met that gives a MAGNITUDE from")
    print("  a ratio of two scales. the missing unit has not been found, but")
    print("  for the first time it has been MOVED -- out of Lambda and into")
    print("  m_e, where 10^-122 becomes 10^-21.")


if __name__ == "__main__":
    main()
