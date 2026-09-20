"""
Is the observable/unobservable split the same as QM's inside/outside?

The question: GR draws a horizon -- a boundary light does not cross.
QM has an outside (unitary psi) and an inside (measurement outcomes)
that it cannot reconcile. Are these the same boundary?

This is calculable. The standard construction:

  1. Take a system with a horizon. Split the degrees of freedom
     into ACCESSIBLE (this side) and INACCESSIBLE (other side).
  2. The global state is pure -- that is GR's outside view, a
     single deterministic object.
  3. An observer confined to one side has the REDUCED density
     matrix rho_A = Tr_B(|psi><psi|).
  4. If rho_A is mixed, the inside observer sees probabilities
     where the outside sees determinism.

If the horizon split produces exactly the pure-to-mixed transition,
then yes: the unobservable/observable split IS the outside/inside
split, and the Born-rule probabilities an inside observer sees are
the shadow of what the horizon removed.

CONCRETE CASE -- Unruh.
An accelerating observer in flat, EMPTY Minkowski space has a
horizon. The Minkowski vacuum is a PURE state. Traced over the
region behind the Rindler horizon, it becomes a THERMAL state at
temperature T = a / 2pi (natural units).

That is not an analogy. It is a theorem, and it is computable
exactly for each field mode:

    |0_M> = prod_k  (1/cosh r_k) sum_n (tanh r_k)^n |n,n>_Rindler
    tanh r_k = exp(-pi omega_k / a)

The entanglement entropy of one wedge, per mode:

    S = cosh^2(r) log cosh^2(r) - sinh^2(r) log sinh^2(r)

This script computes:
  (a) the pure global state and the mixed reduced state, exactly
  (b) the entropy as a function of acceleration -- zero horizon,
      zero mixing; the split CREATES the probabilities
  (c) whether the thermal character is exact (it is) and what
      the temperature is
  (d) the Delta-sector reading: is the Rindler horizon the
      parabolic locus?
"""

import numpy as np

# ------------------------------------------------------------ two-mode
# squeezed state, exactly the Unruh structure, truncated at N levels


def unruh_state(r, N=60):
    """|psi> = (1/cosh r) sum_n (tanh r)^n |n,n>. Returns coeffs c_n."""
    n = np.arange(N)
    c = (np.tanh(r) ** n) / np.cosh(r)
    return c / np.linalg.norm(c)


def reduced_rho(c):
    """Tr_B of |psi><psi| for psi = sum c_n |n,n>  ->  diag(c_n^2)."""
    return c ** 2


def entropy(p):
    p = p[p > 1e-300]
    return float(-(p * np.log(p)).sum())


def purity(p):
    return float((p ** 2).sum())


def r_of(omega, a):
    """tanh r = exp(-pi omega / a)."""
    t = np.exp(-np.pi * omega / a)
    return np.arctanh(min(t, 1 - 1e-15))


print("=" * 78)
print("(a) GLOBAL PURE  ->  LOCAL MIXED.  Does the horizon do it?")
print("=" * 78)
print()
print("  global state |0_M> is PURE:  S_global = 0 exactly.")
print("  reduced to one wedge:")
print()
print(f"  {'accel a':>9} {'omega':>7} {'r':>9} {'S (nats)':>11} "
      f"{'purity':>10} {'<n>':>10}")
print("  " + "-" * 62)
for a in (0.0001, 0.1, 0.5, 1.0, 2.0, 5.0, 20.0):
    om = 1.0
    r = r_of(om, a)
    c = unruh_state(r)
    p = reduced_rho(c)
    nbar = float((np.arange(len(p)) * p).sum())
    print(f"  {a:9.4f} {om:7.2f} {r:9.5f} {entropy(p):11.6f} "
          f"{purity(p):10.6f} {nbar:10.5f}")
print()
print("  a -> 0 : no horizon. r -> 0, S -> 0, purity -> 1.")
print("           the inside observer sees the SAME pure state.")
print("  a large: horizon close. S grows, purity falls.")
print()
print("  *** THE MIXING IS CREATED BY THE SPLIT, NOT BY THE STATE. ***")
print()

print("=" * 78)
print("(b) IS THE REDUCED STATE EXACTLY THERMAL?")
print("=" * 78)
print()
print("  thermal:  p_n proportional to exp(-n omega / T)")
print("  Unruh predicts  T = a / 2pi")
print()
print(f"  {'a':>8} {'T_pred':>10} {'T_fit':>10} {'rel err':>11} "
      f"{'max |dp|':>11}")
print("  " + "-" * 54)
for a in (0.2, 0.5, 1.0, 2.0, 5.0, 10.0):
    om = 1.0
    r = r_of(om, a)
    p = reduced_rho(unruh_state(r))
    # fit log p_n = const - n*omega/T
    n = np.arange(len(p))
    m = p > 1e-250
    slope = np.polyfit(n[m], np.log(p[m]), 1)[0]
    T_fit = -om / slope
    T_pred = a / (2 * np.pi)
    # thermal prediction
    beta = om / T_pred
    p_th = np.exp(-beta * n)
    p_th /= p_th.sum()
    print(f"  {a:8.3f} {T_pred:10.6f} {T_fit:10.6f} "
          f"{abs(T_fit-T_pred)/T_pred:11.3e} "
          f"{np.abs(p - p_th).max():11.3e}")
print()
print("  exact, to machine precision. the inside observer sees a")
print("  thermal bath in a vacuum the outside observer calls empty.")
print()

print("=" * 78)
print("(c) THE ANSWER TO THE QUESTION")
print("=" * 78)
print()
print("  outside view  : one pure state, deterministic, no")
print("                  probabilities anywhere. = GR's global")
print("                  description, and QM's unitary psi.")
print()
print("  inside view   : a mixed state. probabilities. a")
print("                  temperature. = what a confined observer")
print("                  measures.")
print()
print("  the horizon is what turns one into the other, and the")
print("  conversion is EXACT and CALCULABLE, not speculative.")
print()
print("  SO: yes. the observable/unobservable split produces the")
print("  same pure/mixed, determinism/probability structure that")
print("  QM's outside/inside split has. NOT an analogy -- the")
print("  Unruh effect is this statement.")
print()
print("  WHAT IT DOES NOT DO:")
print("    - it does not derive the Born rule. tracing out gives")
print("      a mixed state; interpreting diag(rho) as PROBABILITIES")
print("      is still an extra assumption.")
print("    - it needs a background metric to define the modes. so")
print("      it does not bridge GR and QM -- it is QFT on a FIXED")
print("      curved background, the regime where both already work.")
print("    - at the singularity there is no background, and this")
print("      whole calculation is unavailable.")
print()

print("=" * 78)
print("(d) DELTA SECTOR: what is a boost, group-theoretically?")
print("=" * 78)
print()
print("  Rindler observers are orbits of a BOOST. The Rindler")
print("  horizon is the fixed locus of the boost generator.")
print()


def delta(M):
    M = np.asarray(M, float)
    return np.trace(M) ** 2 - 4 * np.linalg.det(M)


print(f"  {'rapidity':>10} {'matrix':>28} {'tr':>10} {'Delta':>12} "
      f"{'sector':>12}")
print("  " + "-" * 76)
for eta in (0.0, 0.25, 0.5, 1.0, 2.0):
    B = np.array([[np.cosh(eta), np.sinh(eta)],
                  [np.sinh(eta), np.cosh(eta)]])
    D = delta(B)
    sec = ("LIGHTLIKE" if abs(D) < 1e-12
           else "BOOST" if D > 0 else "ROTATION")
    print(f"  {eta:10.3f} {'[[ch,sh],[sh,ch]]':>28} "
          f"{np.trace(B):10.5f} {D:12.6e} {sec:>12}")
print()
print("  eta = 0 is the identity: Delta = 0, parabolic. NO horizon.")
print("  eta > 0: Delta = 4 sinh^2(eta) > 0, hyperbolic. HORIZON.")
print()
print("  Delta > 0 <=> the boost has two real fixed points <=> the")
print("  two null rays <=> a horizon exists.")
print()
print("  and from (a): a -> 0 gave S -> 0. Same statement.")
print("  Delta = 0  <=>  no horizon  <=>  no mixing  <=>  the")
print("  inside observer and the outside observer agree.")
print()
print("  *** THE PARABOLIC LOCUS IS WHERE INSIDE AND OUTSIDE ARE")
print("      THE SAME VIEW. THAT IS THE DARMIYAN. ***")
print()
print(f"  {'a':>8} {'eta ~ a':>10} {'Delta(boost)':>14} {'S':>11}")
print("  " + "-" * 46)
for a in (0.0, 0.1, 0.5, 1.0, 2.0, 5.0):
    B = np.array([[np.cosh(a), np.sinh(a)],
                  [np.sinh(a), np.cosh(a)]])
    if a == 0:
        S = 0.0
    else:
        S = entropy(reduced_rho(unruh_state(r_of(1.0, a))))
    print(f"  {a:8.3f} {a:10.3f} {delta(B):14.6e} {S:11.6f}")
