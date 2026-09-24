# Open threads

Everything unresolved as of 25 Sep 2026. Written so a reader with no memory
of the conversation can pick any one of these up.

Rule used throughout: a thread is listed as OPEN only if there is a concrete
test that would close it. Anything that cannot be falsified is in the last
section and marked as such.

---

## 1. The missing unit

**Status: open. This is the blocking problem for everything with a claimed
application.**

Λ is a ratio. Every result in this work is a ratio, and a ratio has no units
until something outside the structure supplies one.

Where it bites, in three places that look unrelated but are the same problem:

| context | shape is right | unit is missing |
|---|---|---|
| blockchain | `1 - tanh(Λ/2) -> 2e^-Λ`, matches `(q/(1-q))^k` to 1e-6 | what one unit of Λ costs an attacker |
| walker proper time | `τ = Σ|err|` converges to 1.7738775833, bounded by 2 | what one unit of τ is in seconds |
| mirror simulation | inside and outside charts agree on Δ | what one hop is in metres |
| verification | Δ fixes the conjugacy class | which member of the class you are on |
| EDA routing | nonlinear arith predicts blow-up | what one state bit costs *your* tool |

In Bitcoin the unit is hashing, which is exactly the cryptography. The claim
"a chain without cryptography" survives only if depth is expensive for some
other reason. SYMLOOP_MAX = 40 is a real non-cryptographic constraint but it
is a cap, not a price.

**Test that would close it:** exhibit any quantity internal to the construct
that is not a ratio. So far none found, across five independent sightings.

The EDA sighting is the useful one, because there the unit is obtainable: run
the router's predictions against a real formal flow (Yosys + SymbiYosys on
Ibex, PicoRV32, VexRiscv) and fit the thresholds to converge-vs-timeout. That
is what supplying a unit from outside actually looks like, and it is the only
case in this work where the outside is reachable.

---

## 2. `shift` misclassification

**Status: open, known limitation, in `fs/darmiyan.py`.**

The three sectors are recovered from how a filesystem walk fails:

- parabolic -> self-link -> ELOOP
- rotation -> cycle -> ELOOP
- boost -> open chain -> no error, no end

`shift` (x -> x+1) is parabolic (Δ=0) but builds as an open chain, so the
walk classifies it as a boost. The classifier reads the *orbit topology*,
not the sector, and for a parabolic with its fixed point at infinity the
orbit is a chain.

**Test that would close it:** add the point at infinity as a real directory
and see whether `shift` then closes onto it. If it does, the classifier was
right and the chart was incomplete.

---

## 3. ELOOP conflates order 1 with order 2

**Status: open, may be unclosable.**

The OS returns the same errno for `a -> a` and for `a -> b -> a`. From the
walker's side a fixed point and a two-cycle are indistinguishable: both are
"undefined".

`readlink` tells them apart instantly. So the information is present and it
is the *walk* that cannot terminate.

**Open question:** is there a walker-side observable, using only hop count
and local name, that separates order 1 from order 2 before ELOOP fires? If
not, this is a genuine resolution limit and should be stated as one.

---

## 4. Residue conservation is a symmetric-pair law only

**Status: newly opened 22 Sep, in `pair/asym_pair.py`. This narrows an
earlier result.**

`pair/two_systems.py` found a conserved residue: the component of the gap
lying outside the span of available headings. Conserved to 8.9e-15.

With one side given hysteresis and the other left lossless:

```
SYMMETRIC  (both lossless)   3.413296455 -> 3.413296455   change 4.44e-16
ASYMMETRIC (B scars)         3.436265264 -> 12.208663291  change 8.77e+00
```

The conservation does not survive the asymmetry. The earlier result stands
but its scope is smaller than stated.

**Open question:** is there a modified residue that IS conserved for the
asymmetric pair? If the scar is included in the state, the pair becomes
lossless again by construction, which is trivial. The non-trivial version
asks for a quantity conserved without access to the scar.

---

## 5. CP holds exactly, T does not

**Status: result, with an open interpretive question.**

For a pair where one member is lossless and the other scars:

```
 baseline 8.123129892  diff 0.000e+00
        C 9.625739390  diff 1.503e+00
        P 9.625739390  diff 1.503e+00
       CP 8.123129892  diff 0.000e+00     <-- exact
        T 5.513863445  diff 2.609e+00
      CPT 5.513863445  diff 2.609e+00
```

CP is an exact symmetry of the pair. T is not, and CPT violation equals T
violation exactly, so C and P contribute nothing to the breakage. The whole
asymmetry localises in memory.

Note this is inverted from particle physics, where CPT holds and CP breaks.
That means the pair is not a local Lorentz-invariant theory, which is
unsurprising but should not be glossed over.

**Open question:** is the inversion meaningful or is it an artifact of C and
P being implemented as the same map here? They gave identical numbers, which
is suspicious. Needs a construction where C and P are genuinely distinct.

---

## 6. The arrow belongs to the pair

**Status: result, holds. Listed here because the generalisation is open.**

```
A alone   |x| over 40 steps:  min 2.577566  max 2.577566   monotone? False
pair      |scar|:              0.000000 -> 9.016526        monotone rising? True
pair      |a-b|:               2.299887 -> 16.227437
```

The lossless member has no monotone quantity, so no arrow of its own. The
pair has one.

**Open question:** does this need the asymmetry, or would two scarring
systems also produce an arrow that neither has alone? Not tested.

---

## 7. Four instants

**Status: result, exact. Extension open.**

A Möbius law has 3 degrees of freedom. Below four observations the solution
space crosses the parabolic locus, so the sector is undetermined. At k=3 the
Δ numerator factors exactly:

```
-(23 t0 + 40 t1)(1633 t0 - 1210 t1) / 52900
```

An earlier "percentage of samples with the right sector" table was a lattice
artifact (non-monotonic 33% / 25% / 46% = sampling noise) and has been
removed. The exact algebraic test replaced it.

**Open question:** is 4 the bound for every 3-parameter family, or specific
to `SL(2)`? Stated as a conjecture, not proven.

---

## 8. S(T) boundedness

**Status: verified numerically, open theoretically.**

`S(T) = N(T) - [θ(T)/π + 1]` stays in `[-0.965, +0.577]` while `N(T)` grows
by a factor of 22,491.

This is not new mathematics. It is the Riemann–von Mangoldt formula and the
boundedness of S(T) in the ranges computed is long known. Listed here only
because the compactification framing (infinite from inside, bounded from
outside) is the same shape as the walker's proper time, and whether that is
more than an analogy is untested.

**Bug fixed and worth recording:** the first version used
`arg(Gamma(1/4 + it/2)) - (t/2)log π`, which takes the wrong branch and
produced garbage in the thousands, which I then read out as confirming
boundedness. `mp.siegeltheta` is the continuous branch and gives the right
answer. Corrected in `riemann/st2.py`.

---

## 9. The mirror-simulation framework

**Status: designed, not built. Spec below is the whole of it.**

Central constraint: **you never write the mirror.** Write the relation once;
the mirror is the same artifact read by the other resolver. Two simulations
means the design failed.

1. **The artifact.** Not code. States as nodes, transitions as links.
   Nothing in it names the domain.
2. **Resolver I (inside).** Knows hop count, local name, own accumulated
   error. Clock is `τ = Σ|err|`. Hits ELOOP. Reports undefined at fixed
   points.
3. **Resolver O (outside).** `readlink`, full link table, never walks, never
   fails, has no proper time.
4. **The bridge invariant.** One quantity both compute independently and must
   agree on (Δ or κ here). Load-bearing: without it the construction is
   decorative.
5. **The payload is the disagreements:**
   - I reports ELOOP where O reports a fixed point (deadlock, stall, control
     lock).
   - I reports infinity where O reports an ordinary point in another chart
     (gimbal lock, coordinate singularity).

   Distinguishing those two is the thing no single-chart simulator can do.

**Open:** build it on a system whose answer is already known (the Möbius
case) before any application domain. And item 1 above still applies: the
unit is missing.

---

## 10. Computation as topology

**Status: working, in `fs/nocode.py`. Limits known.**

A DFA is four symlinks; the input is the path; the kernel's resolver runs it.
Arithmetic works by path concatenation and `succ`/`pred` cancel inside
`namei()`.

**Bug worth recording:** the first version used `os.path.realpath`, which is
pure Python and walks the links itself. That made the demonstration circular.
`O_PATH` plus `/proc/self/fd` forces kernel resolution, and only then does
the claim hold. The ELOOP ceiling then appears where it should: `succ×40`
resolves, `succ×41` gives errno 40.

**Hard limit:** one path is capped at 40 resolutions, so this machine has a
word size and it is the kernel's. Any computation needing depth > 40 must be
chunked, at which point our code is running again and the claim weakens.

**Open:** is there a construction that gets unbounded computation with
bounded path depth? Composing through directory nesting rather than symlink
chaining is the obvious candidate and is untested.


---

## 13. What verifies a block: the pair, and only partially

**Status: result, with a hard limit. `chain/verify.py`.**

Four forgeries against three verifiers:

```
                               chain   LOCAL     PHI    Delta
                              honest    True    True        5
          A  jump to the fixed point   False    True        5
              B  valid chain, seed 7    True    True        5
            C  M squared, same Delta   False    True        5
               D  two blocks swapped   False   False        5
```

φ cannot be the validator: sitting at the fixed point satisfies a φ-check
perfectly and lies about history. φ is also *derived* from the walker's own
error sequence (2 log φ recovered to ten digits), so it is downstream of the
data it would validate.

There is also no hash. `f(x) = 1 + 1/x`, `f⁻¹(y) = 1/(y−1)`, one division each
way. A Möbius map is invertible, so no block commits to anything, so there is
nothing for a miner to do. The one-wayness a chain needs is not in the
dynamics; it is in *reference*, where it was measured at 30,760×.

**Open:** forgery B passes every available test. The construct verifies that a
transition is lawful and cannot verify that a history is *this* one. Is there
any internal observable that separates two valid chains from different seeds?
If not, that is the same limit as thread 1.

---

## 14. Bases: a mirror is Galois conjugates, and Pisot is termination

**Status: result, verified against theorem. `numbers/mirrors.py`, `numbers/bases.py`.**

```
                base  max |conj| < 1?   integers 1..25 terminating
                 phi             True                      25 / 25
    1+sqrt2 (silver)             True                      25 / 25
               sqrt2            False                      12 / 25
        (1+sqrt13)/2            False                       2 / 25
                   e    no conjugates                       2 / 25
                  pi    no conjugates                       3 / 25
```

The columns agree exactly. This is Pisot ⇒ property (F), with Frougny–Solomyak
for necessity; the table is a check, not a discovery. A transcendental has no
conjugates at all, and that absence is the same fact as non-termination.

For φ the reciprocal and the Galois conjugate coincide up to sign. Holds for φ
and silver, fails for every other base tested. That coincidence is the whole of
φ's privilege, not any mystical property.

Radix economy: base φ is **worse than binary** (3.362 against 2.885, optimum
e at 2.718). φ buys structure, not economy.

**Open:** is there a Pisot base whose economy beats binary? The Pisot numbers
below 2 are the plastic number and the tribonacci-like family; none of the ones
tested here do. A small exhaustive search over the known small Pisot numbers
would settle it.

---

## 15. Representation cannot cancel

**Status: closed, negatively, and that closure is useful. `quantum/quantum.py`.**

```
    path via |0>  +0.707107 x +0.707107 = +0.500000
    path via |1>  +0.707107 x -0.707107 = -0.500000
    sum                                   +0.000000
```

A change of base is a bijection computable and invertible in polynomial time,
so nothing it does can exceed polynomial speedup. The quantum speedup comes
from signed amplitudes that destructively cancel; a permutation of labels
cannot annihilate anything, and probabilities only add.

Grover on a 3-SAT instance at the ratio where local descent failed 120/120:
50 oracle calls against 3,276 expected, P(solution) 0.99994535. Quadratic and
provably optimal for unstructured search.

**This closes a whole family of ideas**, including "the union of all number
systems is a superposition." It is not: those branches are bijections of one
object, and what the union leaves standing is the base-independent part, which
is what an invariant is. The union is a quotient, not a superposition.

---

## 16. Recognition, and the cost that never vanished

**Status: result. `complexity/boundary.py`, `complexity/recognition.py`.**

```
boundary     makes the search FINITE   (the field is bounded)
recognition  makes it FAST             (the class is prepaid)
P vs NP      asks whether recognition is ALWAYS possible
```

A BFS distance field has zero trap cells out of 1647, checked exhaustively, so
greedy descent is guaranteed. A cheap straight-line field has one trap and
strands agents. Renamable Horn, recognised by a 2-SAT test: 60/60 against
43/60 blind, 1.44 ms against 28.56 ms, 0 false positives on random instances.

The cost never vanished; it moved into a different currency. Someone had to
identify the class, find the polynomial test, and write the class solver. That
is the same "one global scan," paid in human work and amortised forever.

**Open:** the reformulation "P vs NP asks whether recognition is always
possible" is correct and is a restatement, not a result. No test attached, so
it belongs in section 11 by this file's own rule. It is here because the two
scripts under it are real.

---

## 17. The EDA analogy, and one bug it surfaced

**Status: analogy stated, one concrete fix shipped.**

`0x-auth/rv-verification-scheduler` turns out to be this work's `recognition.py`
in silicon: a cheap static pass deciding which tractable class an RTL module
belongs to, so the right engine is applied, without solving the instance.

Mappings that hold:

| this work | EDA |
|---|---|
| trap-free field / local descent | FORMAL / SIMULATION |
| CHEAP_OPS vs NONLINEAR_OPS | algebraic vs transcendental (thread 14) |
| verification is pairwise | SVA `a \|=> b`, RVVI/RVFI trace comparison |
| forgery B passes everything | assertions fix the class, not the member |
| forward cheap / reverse scan | checking vs debug; cone-of-influence vs fanout |
| the missing unit | "thresholds are uncalibrated defaults" |

That last row is thread 1 appearing in someone else's README without either of
us noticing until now.

**Bug found and fixed:** `parse_core.py` captured only the first identifier of
a declaration, so `reg [7:0] a, b, c;` counted 8 bits instead of 24. That is an
*under*-count, which routes an intractable module to FORMAL and burns the CI
time the tool exists to save. Regression fixture added (72 bits; was 56); all
four existing fixtures route identically.

**Open:** does `sequential_state_bits` beat a trivial size baseline (lines of
code, declaration count) at predicting formal timeout? If not, the width
weighting is decoration. This is the same control that dismantled the raw pLDDT
claim in thread 8's neighbour, and it should run as part of calibration, not
after.

---

## 11. Not falsifiable, listed for honesty

These recur in conversation and none of them has a test attached. They are
not claims.

- "Gödel, halting, and the GR/QM bridge are the same statement." A family
  resemblance, not a theorem. No formal reduction attempted.
- "The structure IS the meaning." Slogan.
- κ as a definition of intelligence (ability to hold two incompatible
  accounts of one event without collapsing either). Suggestive, no measure
  proposed.
- The Killing form on `sl(2,R)` having signature (1+, 2-) and its light cone
  being the parabolic locus is a *fact*, verified. That the fact explains
  anything about physical spacetime is not.

---

## 12. Nulled, do not revisit without new reason

Five constructions were built and failed identically: `conflict`,
`conflict2`, `discrete`, `compete`, `collapse_null`. In every one the event
never mattered.

Root cause: property questions were being asked of a relational structure.
Δ belongs to the relation, never to the state.

`collapse_null.py` in particular killed a finding that had already been
announced: trace collapse under two accounts is generic averaging. Angle
correlation -0.077; aligned, scrambled and orthogonal are identical.
Withdrawn.

Kept in `pair/nulls/` so the failure is on the record.

**And one pre-registered null.** `numbers/primes_bases.py` asked whether any
base-φ, Zeckendorf or base-e representation statistic separates primes. The
expected answer was written into the file header before the run. Nine of ten
statistics looked significant; all of it was prime density. Controlling for
representation length, p runs 0.12 to 0.89 at every length, and {nφ} is
equidistributed over primes at KS p = 0.958, as Vinogradov requires.

Two methodological errors in my own test are recorded there: a KS test applied
to integer-valued data with heavy ties returned 1e-223 on noise, and a claim
that F(19) is prime (4181 = 37 × 113) sat next to a table that already said
False.
