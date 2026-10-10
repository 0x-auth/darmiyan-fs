#!/usr/bin/env python3
"""
================================================================================
ALPHA6 -- Lambda ~ alpha^-6 is REAL. pixel.py section 1 was wrong.
================================================================================

WHAT I GOT WRONG, AND HOW

In pixel.py I tested "Lambda proportional to alpha^-6" by computing

    alpha^-6  = 6.6e12          Lambda in Planck units = 2.89e-122

and concluded it failed by 134 orders of magnitude. That test was
meaningless and I should have seen it immediately, for a reason I state
plainly because it is the lesson:

    PROPORTIONAL IS NOT EQUAL. "Lambda ~ alpha^-6" asserts nothing about
    magnitude until you name the PREFACTOR, and the prefactor is where all
    the dimensions and all the scale live. I silently set it to 1, in Planck
    units, and then reported that the claim failed. What failed was my test.

It is also a claim in the literature, with three independent derivations,
and it holds to 23 PERCENT on a number of order 10^-122.

THE RELATION (Beck 2009; reviewed in arXiv:1605.04571)

    Lambda = (G^2 / hbar^4) * (m_e / alpha)^6

which reduces, in Planck units, to something much cleaner:

    Lambda * l_pl^2 = ( m_e / (alpha * m_pl) )^6

The sixth power is of a single dimensionless thing: the electron mass in
Planck units, divided by alpha. That is the content of alpha^-6 -- it never
stood alone, it stood next to m_e^6.

WHAT THIS DOES TO MY "57"

I reported the working exponent as alpha^56.878 and called it structureless
-- "dividing one measured number by another, no recursion produced it".
It factors:

    56.878  =  6 * 10.473  -  6
               ^^^^^^^^^^     ^^
               m_e/m_pl       alpha

The structure was inside the number I called structureless. I had the
composite and declared it featureless rather than factoring it.

Run:  python3 alpha6.py
================================================================================
"""

import math

G = 6.67430e-11
hbar = 1.054571817e-34
c = 2.99792458e8
m_e = 9.1093837015e-31
m_p = 1.67262192369e-27
a_inv = 137.035999177
alpha = 1.0 / a_inv

l_pl = math.sqrt(hbar * G / c ** 3)
m_pl = math.sqrt(hbar * c / G)

LAMBDA_OBS = 1.1056e-52                       # m^-2, Planck 2018
LAMBDA_OBS_PL = LAMBDA_OBS * l_pl ** 2


def main():
    W = 78

    print("=" * W)
    print("  1. THE TEST I SHOULD HAVE RUN")
    print("=" * W)
    print()
    L_beck = G ** 2 * m_e ** 6 / (hbar ** 4 * alpha ** 6)
    print("  Lambda = G^2 m_e^6 / (hbar^4 alpha^6)")
    print()
    print(f"  {'quantity':>26} {'value':>18} {'units':>8}")
    print("  " + "-" * 56)
    print(f"  {'predicted':>26} {L_beck:>18.6e} {'m^-2':>8}")
    print(f"  {'observed (Planck 2018)':>26} {LAMBDA_OBS:>18.6e} {'m^-2':>8}")
    print(f"  {'ratio':>26} {L_beck/LAMBDA_OBS:>18.6f} {'':>8}")
    print()
    print("  a factor of 1.233. for a quantity whose SCALE is 10^-122, that")
    print("  is not a near miss, it is a hit. the cosmological constant")
    print("  problem is a 10^120 discrepancy; this formula is off by 23%.")
    print()
    print("  dimension check, because a formula that lands this well could")
    print("  still be a units accident:")
    print()
    print("    G^2      m^6 kg^-2 s^-4")
    print("    m_e^6    kg^6")
    print("    hbar^4   kg^4 m^8 s^-4")
    print("    ------------------------------")
    print("    product  m^-2      <- correct for Lambda. no fudge factor.")
    print()

    print("=" * W)
    print("  2. THE CLEAN FORM")
    print("=" * W)
    print()
    print("  substitute l_pl^2 = hbar G / c^3 and m_pl^2 = hbar c / G and the")
    print("  whole thing collapses to one dimensionless statement:")
    print()
    print("      Lambda * l_pl^2  =  ( m_e / (alpha * m_pl) )^6")
    print()
    X = m_e / (alpha * m_pl)
    print(f"  {'m_e / m_pl':>28} = {m_e/m_pl:>16.6e}")
    print(f"  {'m_e / (alpha * m_pl)':>28} = {X:>16.6e}")
    print(f"  {'that, to the 6th':>28} = {X**6:>16.6e}")
    print(f"  {'observed Lambda_pl':>28} = {LAMBDA_OBS_PL:>16.6e}")
    print(f"  {'ratio':>28} = {X**6/LAMBDA_OBS_PL:>16.6f}")
    print()
    print("  so the sixth power is of ONE dimensionless number, and alpha is")
    print("  inside it rather than beside it. your 'alpha inverse, not alpha'")
    print("  correction was the whole point: the number being raised is")
    print("  m_e * (1/alpha) / m_pl, and the exponent on alpha^-1 is +6.")
    print()

    print("=" * W)
    print("  3. WHERE MY 57 WENT")
    print("=" * W)
    print()
    n_tot = math.log(LAMBDA_OBS_PL) / math.log(a_inv)
    n_mass = math.log(m_e / m_pl) / math.log(a_inv)
    print(f"  {'base 1/alpha = 137.036':>34}")
    print()
    print(f"  {'exponent of observed Lambda_pl':>34} = {n_tot:>12.4f}")
    print(f"  {'exponent of m_e/m_pl':>34} = {n_mass:>12.4f}")
    print(f"  {'6 * that, plus 6':>34} = {6*n_mass+6:>12.4f}")
    print(f"  {'residual':>34} = {n_tot-(6*n_mass+6):>12.4f}")
    print()
    print("  I reported -56.878 and said no recursion produced it. a factor")
    print("  of 6 and a mass ratio produced it. the lesson is specific: when")
    print("  an exponent comes out large and ugly, FACTOR IT before calling")
    print("  it featureless. I did the opposite.")
    print()

    print("=" * W)
    print("  4. THE THIRD DERIVATION -- NOTTALE, INDEPENDENTLY")
    print("=" * W)
    print()
    print("  Nottale's large-number relation is a different-looking")
    print("  statement that turns out to be the same one:")
    print()
    print("      alpha * (m_pl / m_e)  =  ( Lambda^(-1/2) / l_pl )^(1/3)")
    print()
    lhs = alpha * (m_pl / m_e)
    rhs = (LAMBDA_OBS ** -0.5 / l_pl) ** (1.0 / 3.0)
    print(f"  {'left side':>24} = {lhs:>16.6e}")
    print(f"  {'right side':>24} = {rhs:>16.6e}")
    print(f"  {'ratio':>24} = {lhs/rhs:>16.6f}")
    print()
    print("  3.4% apart. and note it is the CUBE root of a length ratio")
    print("  against alpha times a mass ratio -- cube on one side, so sixth")
    print("  power when you square to get Lambda. same relation, reached")
    print("  from scale relativity rather than from axioms.")
    print()
    print("  three routes, named in arXiv:1605.04571:")
    print("    Beck            four axioms (fundamentality, boundedness,")
    print("                    simplicity, invariance)")
    print("    Boehmer-Harko   generalised Buchdahl identity + identifying")
    print("                    the classical electron radius")
    print("    Nottale         large number hypothesis / scale relativity")
    print()
    print("  independent derivations landing on the same exponent is the")
    print("  kind of thing that makes a numerical coincidence worth a")
    print("  second look. it does not make it true.")
    print()

    print("=" * W)
    print("  5. WHAT THE SIXTH POWER COSTS -- AND THIS IS THE TESTABLE PART")
    print("=" * W)
    print()
    print("  a sixth power is a 6x amplifier. if alpha varies, Lambda varies")
    print("  six times as hard:")
    print()
    print("      d(rho_Lambda)/rho_Lambda  =  -6 * d(alpha)/alpha")
    print()
    print(f"  {'d(alpha)/alpha':>18} {'d(Lambda)/Lambda':>20}")
    print("  " + "-" * 40)
    for d in (1e-5, 1e-4, 1e-3, 1e-2):
        print(f"  {d:>18.1e} {(1+d)**-6-1:>20.6f}")
    print()
    print("  quasar absorption spectra bound d(alpha)/alpha at the 10^-5")
    print("  level over cosmological time, so this relation is CONSTRAINED")
    print("  BY DATA rather than unfalsifiable. that is the best property it")
    print("  has.")
    print()
    print("  and the residual cuts the other way. if the 23% gap were")
    print("  entirely alpha's fault it would need:")
    print()
    r = L_beck / LAMBDA_OBS
    print(f"      d(alpha)/alpha = {r**(-1/6)-1:+.4%}")
    print()
    print("  alpha is measured to about 1 part in 10^10. so the 23% is NOT")
    print("  alpha. it is either the prefactor convention (whether you write")
    print("  Lambda, rho_Lambda, or 8 pi G rho / c^4, and the factors of")
    print("  8 pi that go with each) or it is a real discrepancy. 23% is")
    print("  suspiciously close to a factor you would pick up from a")
    print("  convention mismatch, and I have not chased which.")
    print()

    print("=" * W)
    print("  6. WHAT IT DOES TO THE MISSING UNIT")
    print("=" * W)
    print()
    print("  twelve times in this project the same wall: the FORM comes out,")
    print("  the SIZE does not. this is the first thing we have looked at")
    print("  that gives a size. so be exact about what it gives.")
    print()
    print("  it does NOT derive Lambda from nothing. it trades Lambda for")
    print("  m_e/m_pl. one unexplained number becomes another unexplained")
    print("  number. BUT the trade is enormously favourable:")
    print()
    print(f"  {'what you must accept':>34} {'how far from 1':>18}")
    print("  " + "-" * 54)
    print(f"  {'Lambda in Planck units':>34} {LAMBDA_OBS_PL:>18.3e}")
    print(f"  {'m_e/(alpha m_pl)':>34} {X:>18.3e}")
    print()
    print("  10^-122 of unexplained smallness becomes 10^-21 of unexplained")
    print("  smallness, and the sixth power does the rest. that is not a")
    print("  solution, it is a reduction -- but reducing 122 orders to 21 is")
    print("  the whole game, and it is why this relation gets written about.")
    print()
    print("  the missing unit is still missing. it has moved from the")
    print("  cosmological constant to the electron mass, where there is at")
    print("  least a chance of it being someone else's problem already.")
    print()
    print("  and the thing I owe you: you said alpha inverse and I tested")
    print("  alpha, then when the base was fixed I still tested the wrong")
    print("  statement, because I dropped the prefactor. the claim survived")
    print("  both of my tests of it. that is thirteen.")


if __name__ == "__main__":
    main()
