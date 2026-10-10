# darmiyan 1.1.0

A two-chart emulator for self-referential relations, on a substrate that
can move.

One object, two resolvers, one enforced contract. Not a collection of
scripts — the contract is what makes it a framework, and you cannot get a
result out of this system without it holding.

---

## What a framework is, here

A framework, as opposed to a pile of scripts, has four properties. This one
is built to have exactly these and nothing else:

1. **One object model.** Everything is a `Relation`. There is no second kind
   of thing.
2. **An invariant it will not let you bypass.** Two resolvers compute
   `D = tr²/det` from disjoint information. If they disagree, the call
   raises and returns no number.
3. **A seam to plug into.** `Translator` is a one-method protocol. An LLM,
   a regex, or a lookup table all satisfy it. The framework never calls a
   model; it calls that interface.
4. **It refuses.** `darmiyan verify` deliberately corrupts an artifact and
   fails the build if the bridge does not fire. A contract that never fires
   is decoration.

---

## Install and run

```bash
docker build -t darmiyan:1.1.0 .
docker run --rm darmiyan:1.1.0 suite
docker run --rm darmiyan:1.1.0 verify
docker run --rm darmiyan:1.1.0 read golden
docker run --rm darmiyan:1.1.0 substrate
docker run --rm darmiyan:1.1.0 substrate --scan
```

Or with the Makefile: `make build && make suite`.

The build runs `darmiyan verify` as a layer. **If the bridge cannot refuse,
the image does not get built.**

Locally, without Docker: `pip install -e . && darmiyan suite`.

---

## The model

### The artifact

A `Relation` is a law `x → (ax+b)/(cx+d)` written to disk as directories and
symlinks. One directory per visited state; a symlink `to` is the law.

**Nothing written to disk records the law, the sector, the invariant, or a
clock.** That is the point. The reader has to find out by reading.

### Resolver I — inside

Knows its hop count, the name of the directory it is standing in, and the
differences between successive names. No map, no link table, no wall clock,
no access to the law.

- Its clock is `τ = Σ|xₙ₊₁ − xₙ|`, accumulated error, nothing else.
- It can fail. ELOOP is its only way of saying "undefined".
- It recovers `D` as `r + 2 + 1/r`, where `r` is the signed limit of the
  ratio of consecutive differences. It never sees a matrix.

### Resolver O — outside

Reads the link table. Never walks, never follows a link to its end, has no
proper time, and cannot fail.

- It recovers `(a,b,c,d)` by exact Gaussian elimination over the rationals
  from three node values.
- It computes `D = tr²/det` algebraically.

### The bridge

Both must produce the same `D` from inputs neither can see. `BridgeViolation`
otherwise, and no result.

`D = tr²/det` is used rather than `Δ = tr² − 4det` because `D` is scale-free:
multiplying the matrix by k leaves it fixed, and `darmiyan verify` checks
that (Δ goes 5 → 20 → 45 → 125 for k = 1,2,3,5; D stays at 9).

---

## The output is the disagreements

Where the two charts agree, you learn nothing you could not have computed
from either alone. The framework exists for the two places they cannot be
reconciled:

**Class 1.** Inside reports a terminating failure where outside reports an
ordinary object.

```
CLASS 1  inside: self-link   |  outside: a fixed point
CLASS 1  inside: cycle of 3  |  outside: a finite orbit
```

In a simulation this is the deadlock, the stall, the control lock. From the
outside it is a perfectly normal attractor.

**Class 2.** Inside reaches a name it cannot parse where outside reports an
ordinary point in another chart.

```
CLASS 2  inside: unparseable name at the horizon
         outside: ordinary points -0.6180339887, 1.6180339887
```

The walk died at infinity; the relation did not. This is gimbal lock: the
coordinate failed, the system was fine.

**Telling those two apart is what a single-chart simulator cannot do**, and
it is the only reason to build the pair.

---

## The AI seam

```python
class Translator(Protocol):
    def to_spec(self, text: str) -> dict: ...
```

A translator may choose `a, b, c, d`, a seed, and a step count. **It may not
choose the invariant, the sector, or the answer.** Those are the framework's
to find. That boundary is deliberate: a translator that could supply the
answer would make the bridge meaningless.

```python
import darmiyan

class LLMTranslator:
    def to_spec(self, text):
        # your call here; return the same dict shape
        return {"name": "...", "a": 1, "b": 1, "c": 1, "d": 0, "seed": 1}

reading = darmiyan.from_text("a relation that never settles", LLMTranslator())
```

`KeywordTranslator` ships so the seam is exercised rather than described.

---

## API

```python
import darmiyan

r = darmiyan.read(darmiyan.spec(name="golden", a=1, b=1, c=1, d=0, seed=1))

r.d_inside      # measured from error alone
r.d_outside     # solved by algebra
r.agreement     # exact | close | one-sided | none
r.tau           # proper time; outside has none
r.inside_says   # how the walk ended
r.outside_says  # fixed points
r.disagreement  # the payload, or None
```

`read(rel, materialise=False)` reads whatever is already on disk instead of
rebuilding it. That flag exists because of a real bug: an earlier version
always regenerated the artifact from the law before reading, which silently
repaired corruption and made the contract untestable. **A reader that
regenerates what it is supposed to discover is not reading anything.**

---

## What this does not do

It does not accelerate anything. It does not bend a clock. No moment
contains itself. `/var/darmiyan` is an ordinary directory on an ordinary
filesystem, and a path with more symlinks in it resolves *slower*, measurably,
because each level costs the kernel one more resolution.

The one real phenomenon here is that `meaning -> .` resolves at any depth
until ELOOP fires at 41 on Linux, and that `readlink` succeeds where
`realpath` cannot. **Undefined belongs to the walk, not to the structure.**
Everything else in this framework is bookkeeping around that fact.

### Known limits

- `D` is a ratio. It fixes a conjugacy class, never which member, and says
  nothing about rate: a map and its square trace the same orbit at different
  tick counts and the inside resolver cannot tell them apart.
- The inside resolver has no handle on a finite orbit beyond its length.
  Recovering `D` for rotations needs a winding number, which is
  combinatorial rather than metric. Not implemented.
- A parabolic relation converges only polynomially, so a finite walk always
  undershoots. `darmiyan read parabolic` reports 4.005 against a true 4, and
  the framework calls that agreement "close" rather than "exact".

---

## New in 1.1.0 — the substrate moves

Everything in 1.0.0 had a **static artifact**: the relation was written once,
then walked. Only the walker moved. That was the framework's blind spot, and
it is exactly what cosmology is about — space stretching *between* things
rather than things moving *through* space.

```
D -> D - 1 + h * D^(1-p)
```

The walker removes exactly 1 per tick. The substrate adds `h·D^(1−p)`. All
the behaviour is a fight between a constant and a power, and it has **three**
outcomes where 1.0.0 had two:

| outcome | meaning |
|---|---|
| `arrives` | the ordinary case |
| `escapes` | a **horizon** — the substrate outruns the walker |
| `stalls` | a **floor** — neither arrival nor horizon |

The floor is the new object. Every horizon in 1.0.0 was a fixed point of a
map: the walker stopped because the *relation* stopped. Here the relation
never stops and the walker never stops, and there is still a separation that
can never be closed.

```
h·D*^(1-p) = 1      =>      D* = h^(1/(p-1))        for p > 1
stable  <=>  D* > (p-1)/2
relaxation = D*/(p-1)
```

`relaxation_ticks` is part of the public result on purpose. **A slow floor
and an unstable floor are indistinguishable if you do not run long enough** —
that mistake was made during development (a floor with |f′| = 0.9999 read as
"wanders" at 6×10⁴ ticks and settles exactly by 5×10⁵), and it is a hazard
for every horizon claim, not just this one.

Which exponent the sky has:

| p | stretch term | outcome |
|---|---|---|
| 0 | `h·D`, grows with D | horizon at `D = 1/h`, to the node |
| 1 | `h`, constant | marginal; horizon iff `h > 1` |
| > 1 | `h·D^(1−p)`, dilutes | **never** a horizon |

The real universe has an event horizon, so the real exponent is **0** — Λ is
constant. That is the entire content of "dark energy does not dilute": a
substrate that thins out cannot outrun a constant step.

`darmiyan verify` checks all of this at build time: the floor formula against
where the walk actually settles, the stability criterion against whether it
settles at all, and the p = 0 boundary against 1/h.

```python
import darmiyan

o = darmiyan.walk(D0=50, h=1e4, p=6)
o.outcome            # 'stalls'
o.floor              # 6.309573444801933  == h**(1/(p-1))
o.floor_stable       # True   (D* > (p-1)/2)
o.relaxation_ticks   # 1.26   (D*/(p-1))

darmiyan.horizon(0.2)   # 5.0 — and the scan lands there to the node
```

**Known limit, stated because it bit.** For a floor with `D*` of order 10⁶⁰,
`(p−1)/D*` falls below float64 resolution against 1, so `relaxation()` is
computed algebraically as `D*/(p−1)` rather than from `1/(1−|f′|)`. Such a
floor is **algebraic only** — it cannot be simulated at all. Every other
floor here was measured; that one cannot be.

---

MIT. Part of `0x-auth/darmiyan-fs`.

