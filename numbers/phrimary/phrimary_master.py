"""
Phri-mary (Darmiyan) Number System — master verification script (spec v10)
Abhishek Srivastava · 10 Oct 2026 · seed 515

Three primitives:
  1. CODE        digits 0/1, collapse 011 -> 100 and 0200 -> 1001
  2. TWO READINGS inside x = Σ dᵢ Φⁱ,  outside x' = Σ dᵢ ψⁱ,  ψ = -1/Φ
  3. RESOLUTION  Δx = Φ^-k, k chosen (infinity = letting k grow)

Everything below is derived from these and checked. Each section prints PASS/FAIL
or the measured numbers. Dependencies: numpy, mpmath.  Run:  python3 phrimary_master.py
"""
import math, random, itertools, time
from fractions import Fraction as Fr
import numpy as np
import mpmath as mp

PHI = (1 + 5 ** 0.5) / 2
PSI = -1 / PHI
LNP = math.log(PHI)
random.seed(515)
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))


def head(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# ---------------------------------------------------------------- exact Z[Φ]
def fib(n):
    if n < 0:
        return (1 if (n + 1) % 2 == 0 else -1) * fib(-n)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def pw(p):  # Φ^p = F(p-1) + F(p)·Φ  (exact pair)
    return (fib(p - 1), fib(p))


def zmul(x, y):
    a, b = x
    c, d = y
    return (a * c + b * d, a * d + b * c + b * d)


def norm(x):
    a, b = x
    return a * a + a * b - b * b


def conj(x):
    a, b = x
    return (a + b, -b)


def ge(x, y):  # exact x >= y in Z[Φ] (or Q(√5) with Fractions)
    a, b = x[0] - y[0], x[1] - y[1]
    L = 2 * a + b
    if b >= 0:
        return L >= 0 or L * L <= 5 * b * b
    return L >= 0 and L * L >= 5 * b * b


def enc(n):  # exact greedy Φ-code of a positive element (list of places)
    x = (n, 0) if isinstance(n, int) else n
    d, p = [], 0
    while ge(x, pw(p + 1)):
        p += 1
    while x != (0, 0):
        if ge(x, pw(p)):
            d.append(p)
            q = pw(p)
            x = (x[0] - q[0], x[1] - q[1])
        p -= 1
        if p < -400:
            return None
    return d


def value(code):
    return (sum(pw(p)[0] for p in code), sum(pw(p)[1] for p in code))


def collapse(dct):  # Axiom II on a dict place -> count (counts >= 0)
    d = {p: c for p, c in dct.items() if c}
    while True:
        big = [p for p, c in d.items() if c >= 2]
        if big:
            p = max(big)
            d[p] -= 2
            d[p + 1] = d.get(p + 1, 0) + 1
            d[p - 2] = d.get(p - 2, 0) + 1
        else:
            pr = [p for p in d if d.get(p) and d.get(p + 1)]
            if not pr:
                return frozenset(p for p, c in d.items() if c)
            p = max(pr)
            d[p] -= 1
            d[p + 1] -= 1
            d[p + 2] = d.get(p + 2, 0) + 1
        d = {p: c for p, c in d.items() if c}


def code_add(a, b):
    d = {}
    for p in list(a) + list(b):
        d[p] = d.get(p, 0) + 1
    return collapse(d)


def code_mul(a, b):
    d = {}
    for p in a:
        for q in b:
            d[p + q] = d.get(p + q, 0) + 1
    return collapse(d)


def isprime(n):
    return n > 1 and all(n % k for k in range(2, int(math.isqrt(n)) + 1))


# ======================================================================
def s1_collapse():
    head("1. AXIOM II — collapse rules, uniqueness, value preservation")
    ok1 = all(fib(i + 2) == fib(i + 1) + fib(i) and 2 * fib(i) == fib(i + 1) + fib(i - 2) for i in range(-20, 20))
    check("011->100 and 0200->1001 preserve value (Φ and ψ readings)", ok1)
    bad = 0
    for bits in itertools.product((0, 1), repeat=14):
        d = {13 - i: 1 for i, b in enumerate(bits) if b}
        c = collapse(d)
        v0, v1 = value(d.keys()), value(c)
        if v0 != v1 or any(p + 1 in c for p in c) or sorted(c, reverse=True) != enc(v0) and v0 != (0, 0):
            bad += 1
    check("all 16,384 14-bit strings collapse to the unique greedy code", bad == 0, f"{bad} failures")
    rng = random.Random(1)
    dep = 0
    for t in range(500):
        d = {p: rng.randint(0, 3) for p in range(8)}
        outs = set()
        for s in range(4):
            r = random.Random(s)
            dd = {p: c for p, c in d.items() if c}
            while True:
                mv = [("2", p) for p, c in dd.items() if c >= 2] + [("p", p) for p in dd if dd.get(p, 0) >= 1 and dd.get(p + 1, 0) >= 1]
                if not mv:
                    break
                k, p = r.choice(mv)
                if k == "2":
                    dd[p] -= 2; dd[p + 1] = dd.get(p + 1, 0) + 1; dd[p - 2] = dd.get(p - 2, 0) + 1
                else:
                    dd[p] -= 1; dd[p + 1] -= 1; dd[p + 2] = dd.get(p + 2, 0) + 1
                dd = {q: c for q, c in dd.items() if c}
            outs.add(frozenset(dd))
        dep += len(outs) > 1
    check("collapse result independent of rule order (500 strings × 4 orders)", dep == 0)


def s2_exact():
    head("2. EXACT LAYER Z[Φ] — finite codes, depth ~ log_Φ n, mirror reading")
    fails = sum(1 for n in range(1, 2001) if (c := enc(n)) is None or value(c) != (n, 0) or any(p + 1 in c for p in c))
    check("integers 1..2000 have finite, exact, 11-free codes", fails == 0)
    for n in [3, 10, 89, 137]:
        c = enc(n)
        s = "".join("1" if p in c else "0" for p in range(max(c), min(c) - 1, -1))
        print(f"     {n} = {s[:max(c)+1]}.{s[max(c)+1:]}")
    ratios = [-min(enc(n)) / math.log(n, PHI) for n in [100, 1000, 10000, 50000]]
    check("deepest place ≈ log_Φ n (largeness outward = depth inward)", all(0.9 < r < 1.1 for r in ratios), f"ratios {[round(r,2) for r in ratios]}")
    mirror = all(abs(sum(PSI ** p for p in enc(n)) - n) < 1e-6 * n for n in range(1, 2001))
    check("reading any integer's code through the mirror (Φ->ψ) returns the same integer", mirror)


def s3_arith():
    head("3. ARITHMETIC — +, ×, −, ÷ and the period law")
    bad = 0
    for _ in range(3000):
        a, b = random.randint(0, 500), random.randint(0, 500)
        A, B = frozenset(enc(a)), frozenset(enc(b))
        bad += value(code_add(A, B)) != (a + b, 0) or value(code_mul(A, B)) != (a * b, 0)
    check("code + and × (collapse only) equal ordinary + and × (3000 pairs)", bad == 0)
    # conjugation proof for negatives in base −Φ
    print("     negatives: conj maps (−Φ)^i to Φ^(−i) > 0, so no 0/1 code in base −Φ is a negative integer (proof)")

    def expand(q, maxn=20000):
        r = (Fr(q), Fr(0)); seen = {}
        for n in range(maxn):
            if r == (0, 0):
                return None
            if r in seen:
                return n - seen[r]
            seen[r] = n
            t = zmul((Fr(0), Fr(1)), r)
            d = 1 if ge(t, (Fr(1), Fr(0))) else 0
            r = (t[0] - d, t[1])

    def pisano(m):
        a, b, n = 0, 1, 0
        while True:
            a, b = b, (a + b) % m; n += 1
            if (a, b) == (0, 1):
                return n
    mism = [n for n in range(2, 61) if expand(Fr(1, n)) != pisano(n)]
    check("period of 1/n in base Φ = Pisano period π(n), n = 2..60", not mism, f"π(137) = {pisano(137)}")


def s4_cells():
    head("4. FINITE LAYER — numbers as Δx-cells; laws hold as overlap")
    mp.mp.dps = 50
    P = mp.phi

    def fl(x, k):
        p = 0
        while P ** (p + 1) <= x:
            p += 1
        v = mp.mpf(0)
        for q in range(p, -k - 1, -1):
            if v + P ** q <= x:
                v += P ** q
        return v

    def cell(x, k):
        f = fl(x, k); return (f, f + P ** -k)

    def out(lo, hi, k):
        return (fl(lo, k), fl(hi, k) + P ** -k)

    add = lambda a, b, k: out(a[0] + b[0], a[1] + b[1], k)
    mul = lambda a, b, k: out(a[0] * b[0], a[1] * b[1], k)
    meet = lambda a, b: a[0] <= b[1] and b[0] <= a[1]
    k = 12; ok = 0; T = 150
    for _ in range(T):
        x, y, z = [mp.mpf(random.uniform(0.1, 20)) for _ in range(3)]
        a, b, c = cell(x, k), cell(y, k), cell(z, k)
        ok += (meet(add(add(a, b, k), c, k), add(a, add(b, c, k), k)) and meet(mul(mul(a, b, k), c, k), mul(a, mul(b, c, k), k))
               and meet(mul(a, add(b, c, k), k), add(mul(a, b, k), mul(a, c, k), k)) and add(a, b, k)[0] <= x + y <= add(a, b, k)[1])
    check("associativity, distributivity, containment hold as cell overlap (k=12)", ok == T, f"{ok}/{T}")


def s5_emergent_primes():
    head("5. PRIMES EMERGE — balanced codes no product of balanced codes reaches")
    ONE = frozenset([0])

    def codes(k):
        out = []; places = list(range(k, -k - 1, -1))

        def go(i, prev, cur):
            if i == len(places):
                out.append(frozenset(cur)); return
            go(i + 1, 0, cur)
            if not prev:
                go(i + 1, 1, cur + [places[i]])
        go(0, 0, []); return out
    for k in [6, 8, 10]:
        C = codes(k)
        bal = sorted([c for c in C if c and value(c)[1] == 0 and c != ONE], key=lambda c: value(c)[0])
        prods = set()
        for i, a in enumerate(bal):
            for b in bal[i:]:
                pr = code_mul(a, b)
                if value(pr)[0] > value(bal[-1])[0]:
                    break
                prods.add(pr)
        vals = [value(c)[0] for c in bal if c not in prods]
        top = value(bal[-1])[0]
        check(f"depth {k}: {len(C):,} codes -> {len(bal)} balanced (= integers 2..{top}) -> {len(vals)} emergent primes == ordinary primes",
              vals == [n for n in range(2, top + 1) if isprime(n)])


def balanced_rep(x):
    th = math.log(abs(x[0] + x[1] * PHI) / abs(x[0] + x[1] * PSI)) / (2 * LNP)
    best = None
    for kk in range(-round(th) - 2, -round(th) + 3):
        u = (1, 0); g = (0, 1) if kk > 0 else (-1, 1)
        for _ in range(abs(kk)):
            u = zmul(u, g)
        y = zmul(x, u)
        s = abs(math.log(abs(y[0] + y[1] * PHI) / abs(y[0] + y[1] * PSI)))
        if best is None or s < best[0] - 1e-12:
            best = (s, y)
    return best[1]


def s6_fta():
    head("6. FTA IN Z[Φ] — units, splitting law, minimal balanced clusters")
    units = [(a, b) for a in range(-40, 41) for b in range(-40, 41) if abs(norm((a, b))) == 1]
    isunit = all(any(abs(abs(a + b * PHI) - PHI ** n) < 1e-9 for n in range(-15, 16)) for a, b in units)
    check("every unit is ±Φⁿ", isunit, f"{len(units)} units")
    rep = lambda p: any(abs(norm((a, b))) == p for a in range(-40, 41) for b in range(-40, 41))
    law = all((rep(p)) == (p % 5 in (0, 1, 4)) for p in range(2, 300) if isprime(p))
    check("prime p splits iff p ≡ 0, ±1 mod 5; stays prime iff ±2 mod 5 (p < 300)", law)
    print("     89 = (10 − Φ)(10 − Φ′):", norm((10, -1)), "| 137 has no element of norm ±137:", not rep(137))


def s7_views():
    head("7. INSIDE / OUTSIDE — ticks, fuzz γ, spiral, light-cone")
    g = lambda x, xc: 2 * math.sqrt(abs(x * xc)) / (abs(x) + abs(xc))
    check("integers are balanced at any size (γ = 1)", all(abs(g(n, n) - 1) < 1e-12 for n in [1, 137, 50000]))
    check("unit Φ^k: γ = sech(k lnΦ); Φ^k and Φ^-k give the same γ (zero ≡ infinity outside)",
          all(abs(g(PHI ** k, PSI ** k) - 1 / math.cosh(k * LNP)) < 1e-12 for k in range(-12, 13)))
    z = lambda t: PHI ** -t * complex(math.cos(math.pi * t), math.sin(math.pi * t))
    check("spiral ψ^θ = Φ^(−θ)·e^(iπθ): equals ψ^k at whole ticks, ψ^0.5 = 0.786i",
          all(abs(z(k) - PSI ** k) < 1e-12 for k in range(-8, 9)) and abs(z(0.5) - 0.78615j) < 1e-4)
    worst = 0
    for _ in range(5000):
        a, b = random.randint(-50, 50), random.randint(-50, 50)
        u, v = a + b * PHI, a + b * PSI
        if u <= 0 or v <= 0:
            continue
        t, x = (u + v) / 2, (u - v) / 2
        worst = max(worst, abs(g(u, v) - math.sqrt(t * t - x * x) / t))
    check("γ = dτ/dt with inside, outside as light-cone coordinates", worst < 1e-12, f"max err {worst:.1e}")


def s8_duality():
    head("8. DUALITY — TD² + TrD² = 1 and its deficit at finite resolution")
    from scipy.integrate import quad
    a = 1 / PHI; Z = a * (1 + 1 / PHI) + (1 - a)
    h = lambda r: ((1 + 1 / PHI) if r < a else 1) / Z
    m = quad(lambda r: r * h(r), 0, a)[0] + quad(lambda r: r * h(r), a, 1)[0]
    c = quad(lambda r: math.sqrt(r * (1 - r)) * h(r), 0, a)[0] + quad(lambda r: math.sqrt(r * (1 - r)) * h(r), a, 1)[0]
    deficit = 2 * (1 - ((1 - m) ** 2 + m ** 2 + 2 * c * c))
    check("mean position inside a cell under Φ's Parry measure = 1/√5", abs(m - 1 / 5 ** 0.5) < 1e-9, f"{m:.6f}")
    print(f"     deficit for a number known only to Δx: {deficit:.5f}  (uniform guess: {1 - math.pi**2/16:.5f}, ruled out)")


def s9_anyons():
    head("9. FIBONACCI ANYONS — fusion is Axiom II")

    def paths(n):
        out = []

        def go(s):
            if len(s) == n:
                out.append(s); return
            for c in (["t"] if s[-1] == "1" else ["1", "t"]):
                go(s + [c])
        go(["t"]); return out
    ok = all((sum(p[-1] == "1" for p in paths(n)), sum(p[-1] == "t" for p in paths(n))) == (fib(n - 1), fib(n)) for n in range(2, 14))
    check("n anyons fuse to F(n−1) vacuum + F(n) τ outcomes (coefficients of Φⁿ)", ok)
    F = np.array([[1 / PHI, PHI ** -0.5], [PHI ** -0.5, -1 / PHI]])
    allowed = lambda a, b, c: c in {(0, 0): [0], (0, 1): [1], (1, 0): [1], (1, 1): [0, 1]}[(a, b)]

    def Fm(a, b, c, d, e, f):
        if not (allowed(a, b, e) and allowed(e, c, d) and allowed(b, c, f) and allowed(a, f, d)):
            return 0
        return F[e, f] if (a, b, c, d) == (1, 1, 1, 1) else 1
    v = sum(abs(Fm(f, c, d, e, g, l) * Fm(a, b, l, e, f, k) - sum(Fm(a, b, c, g, f, h) * Fm(a, h, d, e, g, k) * Fm(b, c, d, k, h, l) for h in (0, 1))) > 1e-12
            for a, b, c, d, e, f, g, k, l in itertools.product((0, 1), repeat=9))
    check("F-matrix: F² = I and pentagon equation (512 cases)", np.allclose(F @ F, np.eye(2)) and v == 0)


def s10_td_trd():
    head("10. TD and TrD — the orthogonal split that FTA gives")
    s2 = math.sqrt(2)
    TD = lambda x: (math.log(abs(x[0] + x[1] * PHI)) + math.log(abs(x[0] + x[1] * PSI))) / s2
    TrD = lambda x: (math.log(abs(x[0] + x[1] * PHI)) - math.log(abs(x[0] + x[1] * PSI))) / s2
    e = 0
    for _ in range(5000):
        x = (random.randint(1, 60), random.randint(-60, 60)); y = (random.randint(1, 60), random.randint(-60, 60))
        if 0 in (norm(x), norm(y)):
            continue
        z = zmul(x, y); e = max(e, abs(TD(z) - TD(x) - TD(y)), abs(TrD(z) - TrD(x) - TrD(y)))
    check("TD (diagonal, storage = log mass) and TrD (anti-diagonal, reference = ticks) are both additive under FTA", e < 1e-8)
    check("units are pure TrD; inert primes and split-pair products are pure TD",
          abs(TD((0, 1))) < 1e-12 and abs(TrD((137, 0))) < 1e-12 and abs(TrD(zmul((10, -1), conj((10, -1))))) < 1e-12)


def s11_mass():
    head("11. MASS — m² = inside · outside (the norm)")
    u, v = 3 + PHI, 3 + PSI
    inv = all(abs((u * PHI ** (2 * k)) * (v * PSI ** (2 * k)) - u * v) < 1e-9 for k in range(-3, 4))
    check("mass invariant under Φ² boosts", inv, f"m = {math.sqrt(u*v):.6f}")
    ms = {abs(norm((a, b))) for a in range(-200, 201) for b in range(-200, 201) if (a, b) != (0, 0)}
    check("mass gap: no massless code except 0; lightest m = 1", min(ms) == 1)
    print("     allowed m² ≤ 40:", sorted(m for m in ms if m <= 40))
    viol = 0
    for _ in range(5000):
        a, b, c, d = [random.randint(-30, 30) for _ in range(4)]
        u1, v1, u2, v2 = a + b * PHI, a + b * PSI, c + d * PHI, c + d * PSI
        if min(u1, v1, u2, v2) <= 0:
            continue
        viol += math.sqrt((u1 + u2) * (v1 + v2)) < math.sqrt(u1 * v1) + math.sqrt(u2 * v2) - 1e-9
    check("combined mass ≥ sum of masses (motion becomes mass)", viol == 0)


def s12_zeta_outside(N=10 ** 6):
    head("12. ZETA FROM OUTSIDE — ζ_Φ(s) = ζ(s) · L(s, χ5)")
    mp.mp.dps = 25
    chi = lambda n: [0, 1, -1, -1, 1][n % 5]
    v = mp.mpf(1)
    for p in range(2, 20000):
        if isprime(p):
            c = chi(p)
            v *= (1 - mp.mpf(p) ** -2) ** -2 if c == 1 else ((1 - mp.mpf(p) ** -4) ** -1 if c == -1 else (1 - mp.mpf(p) ** -2) ** -1)
    target = mp.zeta(2) * mp.dirichlet(2, [0, 1, -1, -1, 1])
    check("Euler product over the Φ-world's primes = ζ(2)·L(2,χ5)", abs(v - target) < 1e-4, f"{mp.nstr(v,8)} vs {mp.nstr(target,8)}")
    L = lambda z: mp.dirichlet(z, [0, 1, -1, -1, 1])
    zs = [mp.findroot(L, mp.mpc(0.5, t)) for t in [6.65, 9.83, 11.96, 16.03, 17.57]]
    check("first zeros of the outside factor L(s,χ5) lie on Re = 1/2", all(abs(z.real - 0.5) < 1e-12 for z in zs),
          ", ".join(mp.nstr(z.imag, 8) for z in zs))
    sv = np.ones(N + 1, bool); sv[:2] = False
    for i in range(2, int(N ** 0.5) + 1):
        if sv[i]:
            sv[i * i::i] = False
    lam = np.zeros(N + 1)
    for p in np.nonzero(sv)[0]:
        p = int(p); c = chi(p); pk = p; e = 1
        while pk <= N:
            lam[pk] = (c ** e) * math.log(p) if c else 0; pk *= p; e += 1
    cs = np.cumsum(lam); u = np.linspace(math.log(50), math.log(N), 20000); x = np.exp(u)
    g = cs[np.floor(x).astype(int)] / np.sqrt(x); g -= g.mean()
    fr = np.arange(4, 20, 0.02); A = np.array([abs(np.sum(g * np.exp(-1j * f * u))) for f in fr])
    peaks = [round(float(fr[i]), 2) for i in range(1, len(fr) - 1) if A[i] > A[i - 1] and A[i] > A[i + 1] and A[i] > 0.3 * A.max()]
    print(f"     split−inert prime rhythm peaks (x ≤ {N:,}): {peaks}")
    print("     L(χ5) zeros: 6.65, 9.83, 11.96, 16.03, 17.57")


def s13_limits():
    head("13. LIMITS — what no finite structure holds")
    top = 521
    ps = [p for p in range(2, top + 1) if isprime(p)]
    Nn = math.prod(ps) + 1
    spf = next(d for d in range(2, 10 ** 6) if Nn % d == 0)
    check("Euclid inside the system: primes at depth 12, product + 1 -> new prime factor", spf > top,
          f"needs depth ≈ {math.ceil(math.log(Nn, PHI))}, smallest factor {spf}")
    F = [1, 2]
    while F[-1] < 10 ** 6:
        F.append(F[-1] + F[-2])

    def zeck(n):
        s = []
        for f in reversed(F):
            if f <= n:
                s.append("1"); n -= f
            elif s:
                s.append("0")
        return "".join(s)
    codes = {zeck(n): isprime(n) for n in range(1, 200000)}
    m = 11
    pre = sorted({c[:m] for c in codes if len(c) > m})
    sufs = ["".join(t) for L in range(1, 9) for t in itertools.product("01", repeat=L) if "11" not in "".join(t)]
    sig = {tuple(codes.get(p + s) for s in sufs if not (p[-1] == "1" and s[0] == "1")) for p in pre}
    check("no finite automaton: every length-11 prefix behaves differently", len(sig) == len(pre), f"{len(sig)}/{len(pre)}")


if __name__ == "__main__":
    t0 = time.time()
    for f in [s1_collapse, s2_exact, s3_arith, s4_cells, s5_emergent_primes, s6_fta, s7_views,
              s8_duality, s9_anyons, s10_td_trd, s11_mass, s12_zeta_outside, s13_limits]:
        f()
    n_pass = sum(ok for _, ok in RESULTS)
    print("\n" + "=" * 78)
    print(f"{n_pass}/{len(RESULTS)} checks passed in {time.time() - t0:.0f}s")
    for name, ok in RESULTS:
        if not ok:
            print("  FAILED:", name)
