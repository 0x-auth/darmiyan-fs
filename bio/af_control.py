#!/usr/bin/env python3
"""
================================================================================
AF_CONTROL -- the control experiment for alphafold issue #1122
================================================================================

THE CLAIM IN THE ISSUE

  Backbone/H-bond coupling angles are conserved in secondary structure,
  AlphaFold reproduces them, and deviation from the canonical angle
  correlates negatively with pLDDT. ~0.7% of variance explained. Sheets
  borderline.

THE OBVIOUS OBJECTION, WHICH THE ISSUE DOES NOT ADDRESS

  Low-pLDDT regions are geometrically sloppy at EVERYTHING. So ANY local
  geometric deviation will correlate with pLDDT. The question is not
  "does the H-bond angle correlate" -- of course it does -- but

      does it correlate MORE than a geometric quantity that has nothing
      to do with hydrogen bonds?

  If a generic backbone measure does just as well, the finding is about
  disorder, not about H-bond coupling, and the mechanism in the title is
  not doing any work.

WHAT THIS SCRIPT DOES

  1. Downloads real AlphaFold models across a confidence range.
  2. Assigns secondary structure with Kabsch-Sander H-bond energies.
  3. Computes the coupling angle and its deviation from canonical.
  4. Computes FOUR control geometries that involve no H-bond at all:
       - CA pseudo-bond angle      (i-1, i, i+1)
       - CA pseudo-dihedral        (i-1, i, i+1, i+2)
       - tau, the N-CA-C angle
       - omega planarity           |180 - |omega||
  5. Correlates all of them with pLDDT, on the same residues.
  6. Partial correlation: does the H-bond angle survive controlling for
     the generic ones?

  Step 6 is the whole point. Everything before it is setup.

Run:  python3 af_control.py
================================================================================
"""

import io
import math
import os
import sys
import urllib.request

import numpy as np

CACHE = "/tmp/af_cache"
os.makedirs(CACHE, exist_ok=True)

# a spread of human proteins: globular, multi-domain, and some with long
# disordered stretches, so pLDDT actually varies
ACCS = """
P69905 P68871 P01308 P00533 P04637 P38398 Q9Y6K9 P04150 P06400 P42336
P42345 O00459 P27361 Q02750 P15056 P01116 P10275 P03372 Q13485 P84022
P37231 P19793 Q9UBK2 P11021 P07900 P08238 P0DMV8 P11142 P62937 P17987
P49411 P68104 P06733 P04406 P00558 P60174 P14618 P07195 P00338 P02768
Q8WZ42 P35579 P21333 P12931 P06239 Q06124 P29350 P18031 P23458 O60674
""".split()

CANON = {"H": None, "E": None}   # filled from the data itself


# ============================================================== downloading

def fetch(acc):
    p = os.path.join(CACHE, f"{acc}.pdb")
    if os.path.exists(p) and os.path.getsize(p) > 2000:
        return p
    for v in (6, 5, 4):
        url = f"https://alphafold.ebi.ac.uk/files/AF-{acc}-F1-model_v{v}.pdb"
        try:
            with urllib.request.urlopen(url, timeout=40) as r:
                d = r.read()
            if len(d) > 2000:
                open(p, "wb").write(d)
                return p
        except Exception:
            continue
    return None


def parse(path):
    """Returns dict of arrays: N, CA, C, O (n,3) and plddt (n,)."""
    res = {}
    for line in open(path):
        if not line.startswith("ATOM"):
            continue
        nm = line[12:16].strip()
        if nm not in ("N", "CA", "C", "O"):
            continue
        ri = int(line[22:26])
        xyz = (float(line[30:38]), float(line[38:46]), float(line[46:54]))
        b = float(line[60:66])
        res.setdefault(ri, {})[nm] = xyz
        res[ri]["b"] = b
    keys = sorted(k for k in res if all(a in res[k] for a in ("N", "CA", "C", "O")))
    if len(keys) < 30:
        return None
    out = {a: np.array([res[k][a] for k in keys], float)
           for a in ("N", "CA", "C", "O")}
    out["plddt"] = np.array([res[k]["b"] for k in keys], float)
    out["idx"] = np.array(keys)
    return out


# ================================================== Kabsch-Sander H-bonds

def hbond_energies(s):
    """
    E = 0.084 * (1/r_ON + 1/r_CH - 1/r_OH - 1/r_CN) * 332  kcal/mol
    Amide H placed at N + unit(N - (C_prev + O_prev)/... ) per DSSP:
      H = N + (N_i - C_{i-1}) is not it; DSSP uses
      H = N + unit(C_{i-1} - O_{i-1})
    """
    N, CA, C, O = s["N"], s["CA"], s["C"], s["O"]
    n = len(N)
    H = np.full_like(N, np.nan)
    d = C[:-1] - O[:-1]
    d = d / np.linalg.norm(d, axis=1, keepdims=True)
    H[1:] = N[1:] + d

    E = np.full((n, n), 1e9)
    for i in range(1, n):
        if not np.isfinite(H[i]).all():
            continue
        rON = np.linalg.norm(O - N[i], axis=1)
        rCH = np.linalg.norm(C - H[i], axis=1)
        rOH = np.linalg.norm(O - H[i], axis=1)
        rCN = np.linalg.norm(C - N[i], axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            e = 0.084 * (1/rON + 1/rCH - 1/rOH - 1/rCN) * 332
        e[np.abs(np.arange(n) - i) < 2] = 1e9
        E[i] = e
    return E


def assign_ss(E, CA):
    """
    Minimal DSSP: helix if i donates to i-4 (n->n-4 pattern), sheet if a
    bridge partner exists with |i-j| > 2 and CA distance in range.
    Returns arrays ss ('H','E','-') and, for each residue, its partner.
    """
    n = E.shape[0]
    ss = np.array(["-"] * n, dtype="<U1")
    partner = np.full(n, -1)
    HB = E < -0.5
    for i in range(4, n):
        if HB[i, i - 4]:
            ss[i] = "H"
            partner[i] = i - 4
    for i in range(n):
        if ss[i] == "H":
            continue
        cand = np.where(HB[i])[0]
        cand = cand[np.abs(cand - i) > 3]
        if len(cand):
            j = cand[np.argmin(E[i, cand])]
            if 4.0 < np.linalg.norm(CA[i] - CA[j]) < 7.0:
                ss[i] = "E"
                partner[i] = j
    return ss, partner


# =================================================== the geometries

def unit(v):
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(n == 0, 1, n)


def coupling_angle(s, i, j):
    """Angle between local backbone propagation and the H-bond vector."""
    CA, N, O = s["CA"], s["N"], s["O"]
    if i - 1 < 0 or i + 1 >= len(CA):
        return np.nan
    p = unit(CA[i + 1] - CA[i - 1])
    h = unit(O[j] - N[i])
    c = float(np.clip(np.dot(p, h), -1, 1))
    return math.degrees(math.acos(abs(c)))


def ca_pseudo_angle(CA, i):
    if i - 1 < 0 or i + 1 >= len(CA):
        return np.nan
    a, b = unit(CA[i - 1] - CA[i]), unit(CA[i + 1] - CA[i])
    return math.degrees(math.acos(float(np.clip(np.dot(a, b), -1, 1))))


def dihedral(p0, p1, p2, p3):
    b0, b1, b2 = p0 - p1, p2 - p1, p3 - p2
    b1n = b1 / np.linalg.norm(b1)
    v = b0 - np.dot(b0, b1n) * b1n
    w = b2 - np.dot(b2, b1n) * b1n
    x = np.dot(v, w)
    y = np.dot(np.cross(b1n, v), w)
    return math.degrees(math.atan2(y, x))


def ca_pseudo_dih(CA, i):
    if i - 1 < 0 or i + 2 >= len(CA):
        return np.nan
    return dihedral(CA[i - 1], CA[i], CA[i + 1], CA[i + 2])


def tau_angle(s, i):
    N, CA, C = s["N"], s["CA"], s["C"]
    a, b = unit(N[i] - CA[i]), unit(C[i] - CA[i])
    return math.degrees(math.acos(float(np.clip(np.dot(a, b), -1, 1))))


def omega_dev(s, i):
    CA, C, N = s["CA"], s["C"], s["N"]
    if i + 1 >= len(CA):
        return np.nan
    w = dihedral(CA[i], C[i], N[i + 1], CA[i + 1])
    return abs(180 - abs(w))


# ==================================================== stats

def pearson(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    a, b = a[m], b[m]
    if len(a) < 10:
        return np.nan, 0
    a = a - a.mean(); b = b - b.mean()
    d = np.sqrt((a * a).sum() * (b * b).sum())
    return (float((a * b).sum() / d) if d else np.nan), len(a)


def partial(y, x, Z):
    """corr(y, x) controlling for the columns of Z, by residualising both."""
    m = np.isfinite(y) & np.isfinite(x) & np.isfinite(Z).all(axis=1)
    y, x, Z = y[m], x[m], Z[m]
    if len(y) < 20:
        return np.nan, 0
    Z = np.column_stack([np.ones(len(y)), Z])
    def resid(v):
        c, *_ = np.linalg.lstsq(Z, v, rcond=None)
        return v - Z @ c
    return pearson(resid(y), resid(x))[0], len(y)


# ==================================================== run

def main():
    rows = {k: [] for k in
            ("plddt", "dev", "ca_ang", "ca_dih", "tau", "omega", "ss")}
    got = 0
    for acc in ACCS:
        p = fetch(acc)
        if not p:
            continue
        s = parse(p)
        if s is None:
            continue
        got += 1
        E = hbond_energies(s)
        ss, pa = assign_ss(E, s["CA"])
        for i in range(len(ss)):
            if ss[i] == "-" or pa[i] < 0:
                continue
            ang = coupling_angle(s, i, pa[i])
            if not np.isfinite(ang):
                continue
            rows["plddt"].append(s["plddt"][i])
            rows["dev"].append(ang)
            rows["ca_ang"].append(ca_pseudo_angle(s["CA"], i))
            rows["ca_dih"].append(ca_pseudo_dih(s["CA"], i))
            rows["tau"].append(tau_angle(s, i))
            rows["omega"].append(omega_dev(s, i))
            rows["ss"].append(ss[i])
        sys.stdout.write(f"\r  fetched {got}/{len(ACCS)}  residues "
                         f"{len(rows['dev']):,}   ")
        sys.stdout.flush()
    print()
    print()

    for k in rows:
        rows[k] = np.array(rows[k])
    ss = rows["ss"]

    print("=" * 78)
    print("0. DID THE CANONICAL ANGLES REPRODUCE?")
    print("=" * 78)
    print()
    print(f"  structures used: {got},  residues in H or E: {len(ss):,}")
    print()
    print(f"  {'class':>10} {'n':>8} {'mean angle':>12} {'sd':>8} "
          f"{'issue says':>12}")
    print("  " + "-" * 56)
    for c, lbl in (("H", "22.91"), ("E", "12.12")):
        v = rows["dev"][ss == c]
        print(f"  {c:>10} {len(v):>8} {v.mean():>12.2f} {v.std():>8.2f} "
              f"{lbl:>12}")
    print()
    print("  note: this is MY reading of 'coupling angle'. the issue does")
    print("  not pin the definition down, so if these numbers do not match,")
    print("  the definition differs, not necessarily the finding.")
    print()

    print("=" * 78)
    print("1. THE CORRELATION IN THE ISSUE, AND FOUR CONTROLS")
    print("=" * 78)
    print()
    for c in ("H", "E"):
        m = ss == c
        pl = rows["plddt"][m]
        base = rows["dev"][m]
        dev = np.abs(base - np.median(base))     # deviation from canonical
        print(f"  secondary structure {c}   (n = {m.sum():,})")
        print(f"  {'quantity':>34} {'r with pLDDT':>14} {'r^2 %':>9} "
              f"{'H-bond involved?':>18}")
        print("  " + "-" * 78)
        items = [
            ("|coupling angle - canonical|", dev, "YES"),
            ("|CA pseudo-bond angle - med|",
             np.abs(rows["ca_ang"][m] - np.nanmedian(rows["ca_ang"][m])), "no"),
            ("|CA pseudo-dihedral - med|",
             np.abs(rows["ca_dih"][m] - np.nanmedian(rows["ca_dih"][m])), "no"),
            ("|tau (N-CA-C) - med|",
             np.abs(rows["tau"][m] - np.nanmedian(rows["tau"][m])), "no"),
            ("omega non-planarity", rows["omega"][m], "no"),
        ]
        for nm, v, hb in items:
            r, n = pearson(v, pl)
            print(f"  {nm:>34} {r:>14.4f} {100*r*r:>9.3f} {hb:>18}")
        print()

    print("=" * 78)
    print("2. THE DECISIVE TEST: PARTIAL CORRELATION")
    print("=" * 78)
    print()
    print("  does the coupling angle still predict pLDDT once the generic")
    print("  backbone geometry is taken out?")
    print()
    for c in ("H", "E"):
        m = ss == c
        pl = rows["plddt"][m]
        base = rows["dev"][m]
        dev = np.abs(base - np.median(base))
        Z = np.column_stack([
            np.abs(rows["ca_ang"][m] - np.nanmedian(rows["ca_ang"][m])),
            np.abs(rows["ca_dih"][m] - np.nanmedian(rows["ca_dih"][m])),
            np.abs(rows["tau"][m] - np.nanmedian(rows["tau"][m])),
            rows["omega"][m],
        ])
        r0, n0 = pearson(dev, pl)
        r1, n1 = partial(dev, pl, Z)
        print(f"  {c}:  raw r = {r0:+.4f}  ({100*r0*r0:.3f}% variance)")
        print(f"      partial r = {r1:+.4f}  ({100*r1*r1:.3f}% variance)  "
              f"n = {n1:,}")
        drop = (1 - (r1*r1)/(r0*r0)) * 100 if r0 else float("nan")
        print(f"      variance lost to the controls: {drop:.1f}%")
        print()

    print("=" * 78)
    print("3. THE OTHER CONFOUND: pLDDT IS NOT UNIFORM ALONG A CHAIN")
    print("=" * 78)
    print()
    print("  termini and loops are low-pLDDT AND geometrically odd. if the")
    print("  effect is carried by residues near the ends, it is a position")
    print("  effect wearing an H-bond costume.")
    print()
    for c in ("H", "E"):
        m = ss == c
        pl = rows["plddt"][m]
        base = rows["dev"][m]
        dev = np.abs(base - np.median(base))
        for lo, hi, lbl in [(0, 70, "pLDDT < 70"), (70, 90, "70-90"),
                            (90, 101, "> 90")]:
            k = (pl >= lo) & (pl < hi)
            if k.sum() < 30:
                print(f"  {c}  {lbl:>12}: n = {k.sum()} (too few)")
                continue
            r, _ = pearson(dev[k], pl[k])
            print(f"  {c}  {lbl:>12}: n = {k.sum():>6,}  "
                  f"within-band r = {r:+.4f}  mean dev = {dev[k].mean():.2f}")
        print()


if __name__ == "__main__":
    main()
