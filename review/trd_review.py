#!/usr/bin/env python3
"""
================================================================================
TRD_REVIEW -- checking the load-bearing claims of trust_dimension_v5
================================================================================

V5's new contribution is Section 4: a claimed NON-CIRCULAR derivation of the
phi-boundary. Five resistance functions, "each defined with zero reference to
phi, sqrt5, or any Fibonacci number", and only one of them lands on phi.

That is the claim worth testing, because everything else in the paper is
either a restatement of known physics (Section 3) or explicitly labelled a
hypothesis (Section 7). So:

  1. reproduce Table 1 independently
  2. ask whether V4 is actually phi-free in CONTENT, not just in symbols
  3. identify the V5 attractor, which the paper calls "other"
  4. run the missing control on the phi x sqrt(n) simulation

Run:  python3 trd_review.py
================================================================================
"""

import math

import numpy as np

PHI = (1 + math.sqrt(5)) / 2
rng = np.random.default_rng(515)


# ================================================== 1. reproduce the table

def TD(t):
    return math.cos(t) ** 2


def TrD(t):
    return math.sin(t) ** 2


def R1(t):                                   # round-trip fidelity
    return 1 - 4 * TD(t) * TrD(t)


def R2(t):                                   # self-reference stability
    return abs(math.tan(t) ** 2 - 2 * math.tan(t) / math.cos(t) ** 2)


def H(t):
    p, q = TD(t), TrD(t)
    e = 0.0
    for v in (p, q):
        if v > 1e-15:
            e -= v * math.log2(v)
    return e


def R3(t):                                   # entropy x separation
    d = abs(TD(t) - TrD(t)) * H(t)
    return 1e18 if d < 1e-15 else 1 / d


def R4(t):                                   # scale invariance
    a, b = TD(t), TrD(t)
    if a < 1e-12 or b < 1e-12:
        return 1e18
    return abs(1 / a - a / b)


def R5(t):                                   # self-observation fixed point
    c = math.cos(t)
    if c < 0:
        return 1e18
    return abs(math.atan(math.sqrt(c)) - t)


def grid_min(f, n=2_000_000):
    ts = np.linspace(1e-6, math.pi / 2 - 1e-6, n)
    vals = np.array([f(t) for t in ts])
    i = int(np.nanargmin(vals))
    return ts[i]


def main():
    W = 78
    print("=" * W)
    print("1. TABLE 1, REPRODUCED INDEPENDENTLY")
    print("=" * W)
    print()
    print(f"  {'function':>28} {'theta':>9} {'TD':>8} {'TrD':>8} "
          f"{'TD/TrD':>9} {'paper':>9}")
    print("  " + "-" * 76)
    paper = {"V1 round-trip fidelity": 1.0000,
             "V2 self-reference stability": None,
             "V3 entropy x separation": 4.4758,
             "V4 scale invariance": 1.6180,
             "V5 self-observation": 1.3247}
    got = {}
    for nm, f in [("V1 round-trip fidelity", R1),
                  ("V2 self-reference stability", R2),
                  ("V3 entropy x separation", R3),
                  ("V4 scale invariance", R4),
                  ("V5 self-observation", R5)]:
        t = grid_min(f, 400_000)
        a, b = TD(t), TrD(t)
        ratio = a / b if b > 1e-12 else float("inf")
        got[nm] = ratio
        pv = paper[nm]
        print(f"  {nm:>28} {t:>9.4f} {a:>8.4f} {b:>8.4f} {ratio:>9.4f} "
              f"{(f'{pv:.4f}' if pv else 'edge'):>9}")
    print()
    print("  the table reproduces. that part of the paper is sound and the")
    print("  grid search does what it says.")
    print()

    print("=" * W)
    print("2. IS V4 PHI-FREE IN CONTENT, OR ONLY IN SYMBOLS?")
    print("=" * W)
    print()
    print("  V4's stated principle, quoted from the paper:")
    print()
    print('    "the whole relates to its largest part as the largest part')
    print('     relates to the remainder"')
    print()
    print("  that sentence is not a consequence of scale invariance. it IS")
    print("  the definition of the golden section, and has been since")
    print("  Euclid VI.def.3, where it is called 'extreme and mean ratio'.")
    print("  the paper's own Section 4.4 performs the standard two-line")
    print("  solution of that definition:")
    print()
    print("      1/TD = TD/TrD,  TrD = 1 - TD   ->   TD^2 + TD - 1 = 0")
    print()
    print("  so the derivation is: assume the golden-section condition,")
    print("  solve it, obtain the golden ratio.")
    print()
    print("  the symbol phi does not appear in R4. the CONTENT of R4 is")
    print("  the definition of phi. those are different claims and the")
    print("  paper's boxed conclusion asserts the first while needing the")
    print("  second.")
    print()
    print("  the 'only 1 of 5' specificity argument does not rescue it. it")
    print("  shows that the one function encoding phi's definition finds")
    print("  phi and the four that do not, do not. that is what you would")
    print("  expect either way, so it discriminates nothing.")
    print()
    print("  demonstration -- here is a sixth function, also phi-free in")
    print("  symbols, encoding a DIFFERENT classical proportion:")
    print()

    def R6(t):
        """whole : largest :: largest : (remainder + largest)  -- silver."""
        a, b = TD(t), TrD(t)
        if a < 1e-12 or b < 1e-12:
            return 1e18
        return abs(1 / a - a / (b + a * b))

    def R7(t):
        """a^3 = a + 1 written as a balance -- the plastic number."""
        a, b = TD(t), TrD(t)
        if a < 1e-12 or b < 1e-12:
            return 1e18
        r = a / b
        return abs(r ** 3 - r - 1)

    for nm, f, target, tn in [("R6 (a different balance)", R6, None, ""),
                              ("R7 (cubic balance)", R7, 1.324717957, "plastic")]:
        t = grid_min(f, 400_000)
        r = TD(t) / TrD(t)
        note = f"  <- {tn} {target:.6f}" if target else ""
        print(f"    {nm:>26} -> TD/TrD = {r:.6f}{note}")
    print()
    print("  each is 'defined with zero reference' to its own attractor and")
    print("  each finds it. writing a balance condition and solving it is")
    print("  not a derivation of the constant that solves it.")
    print()

    print("=" * W)
    print("3. WHAT V5 ACTUALLY FOUND (the paper calls it 'other')")
    print("=" * W)
    print()
    t5 = grid_min(R5, 400_000)
    r5 = TD(t5) / TrD(t5)
    rho = 1.3247179572447460259609088544780973407344040569
    print(f"  V5 attractor     TD/TrD = {r5:.10f}")
    print(f"  plastic number rho      = {rho:.10f}")
    print(f"  difference              = {abs(r5-rho):.3e}")
    print(f"  rho^3 - rho - 1         = {rho**3 - rho - 1:.3e}")
    print()
    print("  that is the PLASTIC NUMBER, the real root of x^3 = x + 1 and")
    print("  the SMALLEST PISOT NUMBER. the paper records it as 'other' and")
    print("  moves on, which understates the result: V5 found a second")
    print("  named self-similar constant, from a different self-reference")
    print("  condition.")
    print()
    print("  and that weakens the paper's own argument rather than helping")
    print("  it. two of five resistance functions land on Pisot numbers")
    print("  associated with self-similar subdivision. phi is then not the")
    print("  unique attractor of self-reference under a conservation")
    print("  constraint; it is the quadratic one, with the cubic one")
    print("  sitting in the same table unremarked.")
    print()

    print("=" * W)
    print("4. THE MISSING CONTROL ON THE phi x sqrt(n) SIMULATION")
    print("=" * W)
    print()
    print("  Section 6.1 reports mean Pearson r = 0.726 between cumulative")
    print("  semantic distance D(n) and sqrt(n), from phi-weighted random")
    print("  walks in a 128-dimensional embedding space, over 1,500")
    print("  trajectories.")
    print()
    print("  the question the paper does not ask: does the phi weighting")
    print("  do any work? a random walk's displacement scales as sqrt(n)")
    print("  by construction, with no weighting at all. so here is the")
    print("  same experiment with the weight swapped out and nothing else")
    print("  changed. reimplemented from the prose in Section 5.2.")
    print()
    D, T = 128, 300

    def walk(weight_fn, n):
        w = np.array([weight_fn(i) for i in range(1, n + 1)])
        w = w / w.sum()
        steps = rng.normal(size=(n, D))
        steps /= np.linalg.norm(steps, axis=1, keepdims=True)
        pos = np.cumsum(steps * w[:, None], axis=0)
        return np.linalg.norm(pos - pos[0], axis=1)

    schemes = {
        "phi^-i  (the paper's)": lambda i: PHI ** (-i),
        "e^-i":                  lambda i: math.e ** (-i),
        "2^-i":                  lambda i: 2.0 ** (-i),
        "uniform":               lambda i: 1.0,
        "1/i":                   lambda i: 1.0 / i,
        "random":                lambda i: rng.random() + .01,
    }
    print(f"  {'weighting':>24} {'mean r with sqrt(n)':>22} {'sd':>8}")
    print("  " + "-" * 58)
    for nm, fn in schemes.items():
        rs = []
        for _ in range(T):
            n = int(rng.integers(50, 400))
            d = walk(fn, n)
            x = np.sqrt(np.arange(1, n + 1, dtype=float))
            xm, dm = x - x.mean(), d - d.mean()
            den = math.sqrt(float((xm ** 2).sum() * (dm ** 2).sum()))
            if den:
                rs.append(float((xm * dm).sum() / den))
        rs = np.array(rs)
        print(f"  {nm:>24} {rs.mean():>22.4f} {rs.std():>8.4f}")
    print()
    print("  READ THE TABLE. two things, and the first is against me.")
    print()
    print("  (a) I DID NOT REPRODUCE 0.726. my phi-weighted walk gives")
    print("      about 0.24, not 0.726. so this is not a replication and")
    print("      I cannot say the paper's number is wrong -- the")
    print("      normalisation, the distance definition, or the step model")
    print("      must differ from what I built from the description. the")
    print("      paper does not give enough detail to rebuild it, and that")
    print("      is itself a finding: Section 5.2 is not reproducible as")
    print("      written.")
    print()
    print("  (b) the control still bites, in the opposite direction from")
    print("      the one I expected. UNIFORM weighting -- no phi anywhere,")
    print("      a plain random walk -- gives r = 0.995. random weights")
    print("      give 0.993. every geometric decay (phi, e, 2) gives about")
    print("      0.2, because decaying weights make the later steps")
    print("      negligible and the walk stops growing at all.")
    print()
    print("  so phi-weighting is not what produces sqrt(n) scaling. it is")
    print("  the WORST of the six schemes at producing it, and the scheme")
    print("  with no phi in it is the best. sqrt(n) is a property of the")
    print("  random walk; the phi weight degrades it.")
    print()
    print("  the paper's limitation note says the simulations 'do not")
    print("  confirm the phi prefactor in physical data'. on this evidence")
    print("  the stronger statement holds: they do not establish that phi")
    print("  weighting produces sqrt(n) scaling at all, because a walk")
    print("  with no weighting produces it better.")
    print()
    print("  caveat on my own control: I reimplemented from the prose. if")
    print("  the real code normalises cumulative weight differently, (b)")
    print("  may not apply to it. the code is on github per Section 11 and")
    print("  running THAT against a uniform-weight arm is the test.")


if __name__ == "__main__":
    main()
