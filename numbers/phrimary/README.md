# Phri-mary (Darmiyan) Number System

Spec v10 · 10 Oct 2026 · Abhishek Srivastava

Three primitives:

1. **Code** — digits 0/1, collapse `011 → 100` and `0200 → 1001`
2. **Two readings** — inside x = Σ dᵢΦⁱ, outside x′ = Σ dᵢψⁱ, ψ = −1/Φ
3. **Resolution** — Δx = Φ⁻ᵏ, k chosen; infinity is letting k grow

From these alone: integers (balanced codes, x = x′), units (±Φⁿ), primes (minimal balanced
clusters, identical to the ordinary primes), the mod-5 splitting law, unique factorization,
closed arithmetic (+ − × ÷), Pisano periods for 1/n, the 0-to-1 outside view γ = sech(θ lnΦ),
TD/TrD as the orthogonal FTA split, mass as the norm x·x′, and ζ_Φ(s) = ζ(s)·L(s, χ₅).

## Files

- `phrimary_master.py` — every claim as a check. `python3 phrimary_master.py` → 30/30 in ~25 s (numpy, mpmath, scipy).
- `spec_v10.html` — the spec page, each claim marked tested / identity / open / retired.

## Status

Tested: 30/30. Open: full spiral point (direction in the code), choice of equality,
mirror collapse `110 → 001` vs the anyon F-matrix sign, gravity.
