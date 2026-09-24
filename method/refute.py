#!/usr/bin/env python3
"""
================================================================================
REFUTE -- a harness that makes it hard to report an effect you did not try
          to kill
================================================================================

WHY THIS EXISTS

Across six days of work the results that held were not the ones that looked
strongest. They were the ones that survived a control. And every single error
in this project came from the same three places:

  1. an effect that was really a confound          (pLDDT, primes)
  2. a statistic applied outside its assumptions   (KS on tied integers)
  3. prose that disagreed with the table beside it (three separate times)

None of those are hard problems. They are just easy to skip, because skipping
them is what a positive result feels like. So this is the smallest tool that
makes skipping them inconvenient.

WHAT IT DOES

You declare, in this order and before you look:

    outcome      what you are predicting
    effect       the thing you think predicts it
    nuisances    every boring thing that could predict it instead
    expectation  what you expect to find, in words, written FIRST

It then reports, and will not report the headline without the rest:

    raw         corr(effect, outcome)
    rivals      corr(nuisance, outcome) for each nuisance
    partial     corr(effect, outcome) with all nuisances regressed out
    strata      the effect within bins of the strongest nuisance
    delta R2    what the effect adds to a model of nuisances alone
    verdict     one of: CONFOUNDED, SURVIVES, NULL, UNDERPOWERED

It also refuses a few things outright:

  - a KS test on data with heavy ties (returns a warning, not a p-value)
  - a "converged" claim whose tolerance is near the working precision
  - a verdict at all, if `expectation` was left empty

SELF-TESTS at the bottom run it against three cases whose answers are known
in advance, including real prime data.

Run:  python3 refute.py
================================================================================
"""

import math
from collections import Counter

import numpy as np


# ============================================================ small stats

def _finite(*arrs):
    m = np.ones(len(arrs[0]), bool)
    for a in arrs:
        m &= np.isfinite(a)
    return m


def pearson(x, y):
    m = _finite(x, y)
    x, y = np.asarray(x, float)[m], np.asarray(y, float)[m]
    if len(x) < 10:
        return float("nan"), 0
    x = x - x.mean()
    y = y - y.mean()
    d = math.sqrt(float((x * x).sum() * (y * y).sum()))
    return (float((x * y).sum() / d) if d else float("nan")), len(x)


def p_from_r(r, n):
    """Two-sided p for a correlation, normal approximation on Fisher z."""
    if not np.isfinite(r) or n < 10 or abs(r) >= 1:
        return float("nan")
    z = 0.5 * math.log((1 + r) / (1 - r)) * math.sqrt(n - 3)
    return math.erfc(abs(z) / math.sqrt(2))


def residualise(v, Z):
    A = np.column_stack([np.ones(len(v)), Z])
    c, *_ = np.linalg.lstsq(A, v, rcond=None)
    return v - A @ c


def partial(x, y, Z):
    m = _finite(x, y) & np.isfinite(Z).all(axis=1)
    x, y, Z = np.asarray(x, float)[m], np.asarray(y, float)[m], Z[m]
    if len(x) < 20:
        return float("nan"), 0
    return pearson(residualise(x, Z), residualise(y, Z))[0], len(x)


def r2(y, X):
    m = np.isfinite(y) & np.isfinite(X).all(axis=1)
    y, X = y[m], X[m]
    A = np.column_stack([np.ones(len(y)), X])
    c, *_ = np.linalg.lstsq(A, y, rcond=None)
    ss = float(((y - A @ c) ** 2).sum())
    tot = float(((y - y.mean()) ** 2).sum())
    return (1 - ss / tot) if tot else float("nan"), len(y)


def tie_fraction(a):
    """How much of the sample sits on repeated values."""
    a = np.asarray(a, float)
    a = a[np.isfinite(a)]
    if len(a) == 0:
        return 1.0
    c = Counter(np.round(a, 12))
    return 1.0 - len(c) / len(a)


# ============================================================== the harness

class Claim:
    def __init__(self, name, outcome, effect, nuisances, expectation,
                 strata=None, n_bins=5):
        if not expectation or not expectation.strip():
            raise ValueError(
                "expectation is required and must be written before looking. "
                "a harness that lets you fill it in afterwards is a harness "
                "that does nothing.")
        self.name = name
        self.y = np.asarray(outcome, float)
        self.x = np.asarray(effect, float)
        self.N = {k: np.asarray(v, float) for k, v in nuisances.items()}
        self.expectation = expectation.strip()
        self.strata = None if strata is None else np.asarray(strata)
        self.n_bins = n_bins

    # -------------------------------------------------------------- report
    def run(self, alpha=0.01):
        W = 78
        print("=" * W)
        print(f"CLAIM: {self.name}")
        print("=" * W)
        print()
        print("  expectation, recorded before the run:")
        for line in _wrap(self.expectation, 68):
            print(f"    {line}")
        print()

        r_raw, n = pearson(self.x, self.y)
        p_raw = p_from_r(r_raw, n)

        print(f"  n = {n:,}")
        print()
        print(f"  {'predictor':>26} {'r':>9} {'r^2 %':>8} {'p':>11} "
              f"{'role':>10}")
        print("  " + "-" * 70)
        print(f"  {'THE EFFECT':>26} {r_raw:>9.4f} {100*r_raw**2:>8.3f} "
              f"{p_raw:>11.2e} {'claimed':>10}")
        rivals = []
        for k, v in self.N.items():
            rk, nk = pearson(v, self.y)
            rivals.append((k, rk, nk))
            flag = "BEATS IT" if abs(rk) > abs(r_raw) else "rival"
            print(f"  {k:>26} {rk:>9.4f} {100*rk**2:>8.3f} "
                  f"{p_from_r(rk, nk):>11.2e} {flag:>10}")
        print()

        beaten = [k for k, rk, _ in rivals if abs(rk) > abs(r_raw)]
        if beaten:
            print(f"  {len(beaten)} nuisance(s) outperform the effect on raw")
            print(f"  correlation: {', '.join(beaten)}.")
            print("  the raw number is not the headline. the partial is.")
            print()

        # partial
        if self.N:
            Z = np.column_stack(list(self.N.values()))
            r_par, n_par = partial(self.x, self.y, Z)
            p_par = p_from_r(r_par, n_par)
            lost = (1 - (r_par ** 2) / (r_raw ** 2)) * 100 if r_raw else float("nan")
            base, _ = r2(self.y, Z)
            full, _ = r2(self.y, np.column_stack([Z, self.x]))
            print(f"  {'partial r (all nuisances out)':>34} {r_par:>10.4f}")
            print(f"  {'partial p':>34} {p_par:>10.2e}")
            print(f"  {'variance lost to controls':>34} {lost:>9.1f}%")
            print(f"  {'R^2 nuisances alone':>34} {100*base:>9.3f}%")
            print(f"  {'R^2 nuisances + effect':>34} {100*full:>9.3f}%")
            print(f"  {'incremental':>34} {100*(full-base):>+9.3f} points")
            print()
        else:
            r_par, p_par, n_par = r_raw, p_raw, n
            print("  no nuisances declared. that is itself a finding about")
            print("  the claim, not about the data.")
            print()

        # strata on the strongest nuisance
        strat_ps = []
        if self.N:
            worst = max(rivals, key=lambda t: abs(t[1]) if np.isfinite(t[1]) else 0)
            sv = self.N[worst[0]] if self.strata is None else self.strata
            label = worst[0] if self.strata is None else "declared strata"
            print(f"  within bins of {label} "
                  f"(magnitude cannot carry the effect):")
            print()
            print(f"  {'bin':>22} {'n':>8} {'r':>9} {'p':>11}")
            print("  " + "-" * 54)
            ok = np.isfinite(sv)
            qs = np.quantile(sv[ok], np.linspace(0, 1, self.n_bins + 1))
            qs = np.unique(qs)
            for i in range(len(qs) - 1):
                lo, hi = qs[i], qs[i + 1]
                sel = ok & (sv >= lo) & ((sv < hi) if i < len(qs) - 2
                                         else (sv <= hi))
                if sel.sum() < 30:
                    continue
                rb, nb = pearson(self.x[sel], self.y[sel])
                pb = p_from_r(rb, nb)
                strat_ps.append(pb)
                print(f"  {f'[{lo:.4g}, {hi:.4g}]':>22} {nb:>8,} "
                      f"{rb:>9.4f} {pb:>11.2e}")
            print()

        # assumption guards
        print("  assumption checks:")
        tx, ty = tie_fraction(self.x), tie_fraction(self.y)
        for nm, t in (("effect", tx), ("outcome", ty)):
            if t > 0.5:
                print(f"    {nm} is {100*t:.1f}% ties. rank and KS tests "
                      f"assume continuity;")
                print(f"    their p-values here are not trustworthy. "
                      f"Pearson and the")
                print(f"    within-stratum table are the ones to read.")
        if tx <= 0.5 and ty <= 0.5:
            print("    ties below 50% on both; continuity assumptions ok.")
        if n < 200:
            print(f"    n = {n} is small; treat every p below as indicative.")
        print()

        # verdict
        surv = np.isfinite(p_par) and p_par < alpha
        strat_ok = bool(strat_ps) and sum(1 for p in strat_ps if p < alpha) >= \
            max(1, len(strat_ps) // 2)
        if n < 100:
            verdict = "UNDERPOWERED"
            why = "too few observations to separate anything"
        elif not np.isfinite(p_raw) or p_raw > alpha:
            verdict = "NULL"
            why = "the effect does not appear even before controls"
        elif not surv:
            verdict = "CONFOUNDED"
            why = ("the effect disappears once the nuisances are removed; "
                   "it was measuring them")
        elif self.N and not strat_ok and strat_ps:
            verdict = "CONFOUNDED"
            why = ("survives partial correlation but not stratification; "
                   "the effect is carried by between-bin variation, i.e. "
                   "by magnitude")
        else:
            verdict = "SURVIVES"
            why = ("independent of every declared nuisance, on both the "
                   "partial and the within-stratum test")

        print("=" * W)
        print(f"  VERDICT: {verdict}")
        print("=" * W)
        for line in _wrap(why, 72):
            print(f"  {line}")
        print()
        print("  this verdict is only as good as the nuisance list. a")
        print("  confound you did not declare is not controlled, and the")
        print("  harness has no way to know it exists.")
        print()
        return verdict


def _wrap(s, w):
    out, line = [], ""
    for word in s.split():
        if len(line) + len(word) + 1 > w:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        out.append(line)
    return out


def converged(values, tol, working_precision_digits):
    """
    Guard for 'it terminated' claims. Returns (bool, message).

    An earlier base-termination test in this project ran at 50 digits with a
    1e-35 tolerance and reported e and pi as terminating. The tolerance has
    to sit far enough above the noise floor that accumulated rounding cannot
    reach it.
    """
    need = working_precision_digits - math.log10(1 / tol)
    if need < 20:
        return False, (f"tolerance 1e-{int(math.log10(1/tol))} at "
                       f"{working_precision_digits} digits leaves only "
                       f"{need:.0f} digits of headroom. raise precision or "
                       f"tighten tolerance; below 20 this reports noise as "
                       f"convergence.")
    last = abs(values[-1])
    if last < tol:
        return True, (f"converged: final residual {last:.3e} below tolerance "
                      f"{tol:.0e}, {need:.0f} digits of headroom")
    return False, (f"not converged: final residual {last:.3e} above tolerance "
                   f"{tol:.0e} (the guard itself is satisfied, "
                   f"{need:.0f} digits of headroom)")


# =================================================================== tests

def _sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0] = s[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return s


def selftest():
    rng = np.random.default_rng(515)
    W = 78

    print("#" * W)
    print("# SELF-TEST 1: a real, independent effect (answer known: SURVIVES)")
    print("#" * W)
    print()
    n = 3000
    size = rng.normal(0, 1, n)
    effect = rng.normal(0, 1, n)
    noise1 = size + rng.normal(0, .4, n)
    noise2 = size + rng.normal(0, .4, n)
    outcome = 1.4 * size + 0.35 * effect + rng.normal(0, 1, n)
    v1 = Claim("a signal built to be independent of the nuisances",
               outcome, effect,
               {"nuisance A": noise1, "nuisance B": noise2},
               "the effect was constructed independent of both nuisances, "
               "so it should survive partial correlation and stratification "
               "with a smaller coefficient than its raw value.").run()

    print("#" * W)
    print("# SELF-TEST 2: a pure confound (answer known: CONFOUNDED)")
    print("#" * W)
    print()
    # NOTE ON THIS FIXTURE. The first version used
    #     proxy = size + rng.normal(0, .4, n)
    # and the harness returned SURVIVES, which was CORRECT and my fixture was
    # wrong: `proxy` was an independent noisy reading of `size`, so it carried
    # information about the latent variable that neither nuisance captured.
    # A genuine confound has to be a copy of what you are controlling for,
    # not a sibling measurement of the same cause. That distinction is the
    # whole point of the tool and I got it wrong writing its own test.
    proxy = noise1 + rng.normal(0, .05, n)
    v2 = Claim("a signal that is nothing but a copy of nuisance A",
               outcome, proxy,
               {"nuisance A": noise1, "nuisance B": noise2},
               "this predictor is nuisance A plus a little jitter. it should "
               "correlate strongly and then vanish entirely under control. "
               "predicted verdict: CONFOUNDED.").run()

    print("#" * W)
    print("# SELF-TEST 3: real data -- do primes have a base-phi signature?")
    print("#" * W)
    print()
    N = 20000
    S = _sieve(N)
    PHI = (1 + 5 ** 0.5) / 2
    ns = np.arange(2, N + 1)
    isp = np.array([bool(S[i]) for i in ns], float)
    # base-phi digit weight and representation length, greedy, float is fine
    ones, lenint = [], []
    for k in ns:
        x = float(k)
        j = 0
        while PHI ** (j + 1) <= x:
            j += 1
        c, li = 0, j + 1
        for t in range(j, -1, -1):
            p = PHI ** t
            if p <= x + 1e-9:
                c += 1
                x -= p
        ones.append(c)
        lenint.append(li)
    ones = np.array(ones, float)
    lenint = np.array(lenint, float)
    v3 = Claim("base-phi digit weight predicts primality",
               isp, ones,
               {"representation length": lenint,
                "magnitude (log n)": np.log(ns.astype(float))},
               "primes thin out as n grows, so any length-like statistic "
               "will separate them. the digit weight is expected to be a "
               "proxy for length and to die under control. predicted "
               "verdict: CONFOUNDED or NULL.").run()

    print("#" * W)
    print("# SELF-TEST 4: the convergence guard")
    print("#" * W)
    print()
    for dps, tol in ((50, 1e-35), (400, 1e-300), (400, 1e-35)):
        ok, msg = converged([1e-38], tol, dps)
        verdict = ("converged" if ok
                   else ("GUARD REFUSED" if "headroom. raise" in msg
                         else "not converged"))
        print(f"  {dps:>4} digits, tol {tol:.0e}  ->  {verdict}")
        for line in _wrap(msg, 66):
            print(f"        {line}")
        print()

    print("=" * W)
    print("  SELF-TEST SUMMARY")
    print("=" * W)
    print()
    exp = [("independent effect", "SURVIVES", v1),
           ("pure confound", "CONFOUNDED", v2),
           ("primes in base phi", ("CONFOUNDED", "NULL"), v3)]
    allok = True
    for nm, want, got in exp:
        ok = got in (want if isinstance(want, tuple) else (want,))
        allok &= ok
        print(f"  {nm:>24}  expected {str(want):>26}  got {got:>12}  "
              f"{'ok' if ok else 'FAIL'}")
    print()
    print(f"  {'all self-tests pass' if allok else 'SELF-TEST FAILURE'}")


if __name__ == "__main__":
    selftest()
