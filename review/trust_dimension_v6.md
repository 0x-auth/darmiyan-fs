# Storage and Reference as a Duality Relation

### A Conservation Law on the Circle, Not the Simplex

**Abhishek Srivastava**
Independent Researcher, Pune, India
bitsabhi@gmail.com | github.com/0x-auth | ORCID: 0009-0006-7495-5039

**September 2026 | Version 6**

---

## Abstract

We propose that storage (TD) and reference (TrD) are the two legs of a duality
relation governed by **TD² + TrD² = 1**. Version 6 corrects the central
equation of Versions 1 through 5, which stated the law as TD + TrD = 1.

The correction is not cosmetic. Under the linear law the framework's three
claimed mappings onto established physics are vacuous: every pair of
non-negative numbers summing to one satisfies them, so satisfying them carries
no information. Under the quadratic law, the first mapping becomes an exact
identity — TD² + TrD² = 1 **is** the Englert–Greenberger–Yasin duality
relation for pure states — and the deficit acquires a meaning it did not have,
being exactly twice the linear entropy of the state.

Version 6 also replaces the φ-boundary derivation. V5 claimed non-circularity
for a resistance function whose stated principle ("the whole relates to its
largest part as the largest part relates to the remainder") is the Euclidean
definition of the golden section. We give instead a derivation from Hurwitz's
theorem, which is a statement about all real numbers and in which √5 appears
only in the conclusion.

Two claims from V5 are withdrawn: the φ×√n simulation evidence, which does not
survive a uniform-weighting control, and the assertion that the framework
dissolves the measurement problem, which it does not.

**Keywords:** duality relation, wave–particle complementarity, linear entropy,
golden ratio, Hurwitz's theorem, Pisot numbers, storage–reference gap

---

## Version history

| Version | Change |
|---|---|
| V4 (Mar 2026) | Conservation law, quantum mappings, simulations, predictions |
| V5 (Mar 2026) | Claimed non-circular φ-derivation via five resistance functions |
| **V6 (Sep 2026)** | **Law corrected to TD² + TrD² = 1. φ-derivation replaced by Hurwitz. Simulation evidence withdrawn. Measurement-problem claim withdrawn.** |

Every correction in V6 came from a test that the author's own framework failed.
The tests are in `github.com/0x-auth/darmiyan-fs/review/`.

---

## 1. Introduction

In distributed computing there is a fundamental asymmetry with no classical
physics analogue: the distinction between where data is stored and where it is
referenced. A pointer is not its target. Traversing that gap requires a third
element — trust.

The observation that motivated this programme was concrete. Funds sent to an
account nicknamed `sys(void)` arrived at `void(sys)`. These are functional
inverses, f(g(x)) versus g(f(x)), and the routing hash produced identical
signatures for both. In trust-space, both accounts resolved to the same
identity.

**A note on the nature of dimensions.** Space, time, and any proposed fifth
dimension are human-constructed frameworks for organising physical
observation. The Trust Dimension is proposed in this spirit: as a construct
that, if adopted, does bookkeeping that the standard framing does not. Its
validity is empirical.

**A note on this version.** V6 exists because the central equation of V1–V5 was
wrong. That is stated here rather than buried, because a framework that cannot
survive its own corrections is not worth the versions.

---

## 2. The Conservation Law

### 2.1 What is exhaustive, and what that implies

Any physical interaction involves two roles. We assign:

- **TD** = the degree to which an outcome is locally stored (definite,
  time-local, classical)
- **TrD** = the degree to which an outcome is non-locally referenced
  (superposed, distributed, quantum)

The exhaustiveness postulate says every aspect of an event is either stored or
referenced, with no third category. A state that is neither stored anywhere nor
referenced by anything has no causal consequence, and physics does not deal in
causally inert categories.

**What exhaustiveness does NOT give you is a linear law.** V1–V5 wrote the
consequence as TD + TrD = 1, placing the pair on the 1-simplex. That step does
not follow from exhaustiveness: exhaustiveness fixes that the two roles cover
the interaction, not the metric in which they are summed.

### 2.2 The correct constraint

The accessible states lie on the unit circle, not the line:

$$\mathrm{TD}^2 + \mathrm{TrD}^2 = 1, \qquad \mathrm{TD}, \mathrm{TrD} \geq 0$$

Equivalently, parameterising by a single angle θ:

$$\mathrm{TD} = \cos\theta, \qquad \mathrm{TrD} = \sin\theta$$

The symmetry group is still Z₂, swapping TD ↔ TrD, corresponding to
observer–system duality: what is storage from one perspective is reference from
the dual perspective. The reflection θ ↦ π/2 − θ preserves the constraint.

### 2.3 Why the exponent matters

The two laws are not variants of one idea. They describe different sets of
states, and only one of them is instantiated by physics. Section 3 makes that
a measurement rather than an argument.

---

## 3. The Duality Relation

### 3.1 Complementarity, as an identity rather than an inequality

Bohr's complementarity principle is made quantitative by the
Englert–Greenberger–Yasin relation for a two-path interferometer:

$$\mathcal{D}^2 + \mathcal{V}^2 \leq 1$$

where 𝒟 is which-path distinguishability and 𝒱 is fringe visibility, **with
equality for pure states**.

Setting TD = 𝒟 and TrD = 𝒱, the V6 law is the EGY relation. Not an analogy:
the same equation.

V5's argument was that TD² + TrD² ≤ 1 is "satisfied for all (TD, TrD) on the
1-simplex." That is true and empty. Over 200,000 sampled simplex points,
**100%** satisfy the inequality, as must every pair summing to one whatever it
denotes. An inequality a constraint cannot violate is not being instantiated by
that constraint; it is being survived by it.

The linear law is also false as physics. Over 20,000 random pure qubit states:

| quantity | min | max | mean | always 1? |
|---|---|---|---|---|
| 𝒟 + 𝒱 (the V5 law) | 1.000049 | 1.414214 | 1.284537 | **no** |
| 𝒟² + 𝒱² (EGY, V6 law) | 1.000000 | 1.000000 | 1.000000 | **yes** |

At the balanced point 𝒟 = 𝒱 = 1/√2, which interferometers prepare routinely,
the linear law is violated by 41%.

### 3.2 The deficit is the mixedness

For mixed states EGY is a strict inequality, so TD² + TrD² < 1 and the state
lies inside the arc. The radial deficit is not free:

$$1 - (\mathrm{TD}^2 + \mathrm{TrD}^2) \;=\; 2\left(1 - \mathrm{Tr}\,\rho^2\right)$$

verified to 5.6 × 10⁻¹⁶ over 20,000 random mixed qubit states. The identity is
forced: for Bloch radius r the purity is (1 + r²)/2 while TD² + TrD² = r²
exactly.

**This is the framework's one genuine result.** The distance from the unit arc
measures exactly how much of the system is correlated with something outside
it. Under the linear law this quantity is identically zero and says nothing.

The interior of the quarter disc is therefore not reachable by an isolated
system. Reaching it requires an environment, and the law says how much.

### 3.3 Decoherence

Decoherence drives a system from TrD-dominance toward TD-dominance. On the
circle the transition is a rotation:

$$\frac{d\theta}{dt} = -\Gamma(t), \qquad \frac{d}{dt}\left(\mathrm{TD}^2 + \mathrm{TrD}^2\right) = 0$$

for unitary evolution of the system-plus-environment. When the environment is
traced out, the pair moves inward off the arc, and by §3.2 the inward distance
is the entropy produced. The conservation law holds along the arc; departure
from it is the record left in the environment.

### 3.4 Uncertainty: a correspondence, labelled as one

Position is a TD quantity, momentum a TrD quantity via the wavefunction's
global Fourier structure. For Gaussian states the Heisenberg product is
saturated, and the TD/TrD balance rotates along the arc as the state is
squeezed.

This is a **correspondence of form**, not an identity, and V6 does not claim
otherwise. Unlike §3.1 there is no single relation the law reproduces exactly.
V5 presented §3.1, §3.3 and §3.4 as three mappings of equal standing. They are
not. Only §3.1 is an identity.

---

## 4. The φ-Boundary, Derived Without Assuming It

### 4.1 Why V5's derivation was still circular

V5 defined five resistance functions "with zero reference to φ, √5, or any
Fibonacci number" and found that only V4, the scale-invariance condition,
produces φ. Its stated principle:

> the whole relates to its largest part as the largest part relates to the
> remainder

That sentence is the definition of the golden section — Euclid VI def. 3,
*extreme and mean ratio*. V5's §4.4 then performs the standard two-line
solution of that definition and recovers φ.

The **symbol** φ is absent from R₄. The **content** of R₄ is the definition of
φ. V5 closed the symbol-level circularity it had identified and left the
content-level one untouched.

The "only one of five" specificity argument does not rescue this. The function
encoding φ's definition finds φ and the four that do not, do not. That is what
one would observe under either hypothesis, so it discriminates nothing. Two
further φ-free functions, encoding the silver and plastic balances, each find
their own constant (2.414223 and 1.324728 respectively). Writing a balance
condition and solving it is not a derivation of the constant that solves it.

### 4.2 The Hurwitz route

Write r = TD/TrD = cot θ. A **rational** r makes the storage–reference balance
commensurate: some finite repeat closes exactly, the system acquires a period,
and its self-reference terminates. Define interaction resistance as resistance
to that termination — that is, as how poorly r is approximated by rationals,
measured by the Lagrange number

$$L(r) = \limsup_{q \to \infty} \frac{1}{q \,\lVert q r \rVert}$$

where ‖·‖ is distance to the nearest integer. This definition mentions no
proportion, no subdivision, no whole-to-part, and no particular constant. It is
a statement about every real number at once.

**Hurwitz (1891).** For every irrational α there are infinitely many rationals
p/q with |α − p/q| < 1/(√5 q²). The constant √5 is best possible, and it is
attained precisely on the GL(2,ℤ) orbit of φ.

Equivalently: inf L over the irrationals is √5, attained exactly on the φ
family. Checked at exact values:

| r | L(r) | continued fraction |
|---|---|---|
| φ | 2.237082 | [1,1,1,1,1,1,1,1,1] |
| 1/φ | 2.237082 | [0,1,1,1,1,1,1,1,1] |
| φ² | 2.237082 | [2,1,1,1,1,1,1,1,1] |
| √2 | 4.366084 | [1,2,2,2,2,2,2,2,2] |
| plastic | 141.459619 | [1,3,12,1,1,3,2,3,2] |
| π | 35.871195 | [3,7,15,1,292,1,1,1,2] |
| 3/2 | ∞ | [1,2] |

√5 = 2.236068. The φ family sits there and nothing is below it.

Fixing the labelling convention TD > TrD selects the point. **φ is the
maximally incommensurate storage–reference balance, and √5 enters as the value
of a theorem rather than as an ingredient of the premise.**

### 4.3 The comparison that matters

| | V5's R₄ | Hurwitz |
|---|---|---|
| mentions proportion / subdivision | yes, as its premise | no |
| is a statement about all reals | no, about one balance | yes |
| φ appears in the question | as its definition | no |
| √5 appears in the answer | yes | yes |
| extremum is a theorem | no, an identity | yes, Hurwitz 1891 |
| **could have come out otherwise** | **no** | **yes** |

The last row is the test. R₄ could not have produced anything but φ. The
Hurwitz condition could have been minimised by any badly-approximable number.

### 4.4 A methodological note: this cannot be grid-searched

V5's method was a grid search over 10,000 values of θ. That method **cannot**
evaluate the Hurwitz criterion, and the reason is structural rather than
numerical: every grid point is a float, hence rational, and L is infinite on
the rationals. A float supplies the continued fraction of a nearby rational,
which agrees with the target for a few terms and then becomes rounding noise.
The criterion lives in the infinite tail and is invisible to any finite grid.

The Hurwitz route is therefore an **analytic** characterisation, not a sixth
resistance function. That is why it is stronger.

### 4.5 The plastic number, promoted from "other"

V5's Table 1 records the V5 resistance function landing at TD/TrD ≈ 1.3247 and
labels it "other". It is the **plastic number** ρ, real root of x³ = x + 1, and
the **smallest Pisot number**.

This is a result, and it constrains the framework rather than supporting it.
Two of five resistance functions land on Pisot numbers associated with
self-similar subdivision. So φ is not *the* attractor of self-reference under a
conservation constraint; it is the **quadratic** one, with the cubic one
sitting in the same table.

Moreover ρ is **not** Hurwitz-extremal — L(ρ) = 141.46 against √5 = 2.236. So
φ and ρ arrive by different routes and are not two instances of one principle.
The honest statement available:

> Under a conservation constraint, self-similar subdivision of order n selects
> a Pisot number of degree n. Order 2 gives φ. Order 3 gives ρ. The
> *incommensurability* criterion is separate and selects φ alone.

### 4.6 Why Pisot is the relevant class

A base β admits terminating expansions of the integers exactly when β is a
Pisot number — that is, when all Galois conjugates of β lie inside the unit
disc (Pisot ⇒ property (F); Frougny–Solomyak for necessity). Verified across
nine algebraic bases and two transcendentals:

| base | max \|conjugate\| < 1 | integers 1..25 terminating |
|---|---|---|
| φ | yes | 25 / 25 |
| 1 + √2 | yes | 25 / 25 |
| plastic | yes | 25 / 25 |
| tribonacci | yes | 25 / 25 |
| √2 | no | 12 / 25 |
| (1+√13)/2 | no | 2 / 25 |
| e | no conjugates | 2 / 25 |
| π | no conjugates | 3 / 25 |

A transcendental has no conjugates at all, and that absence is the same fact as
non-termination. For φ specifically, the reciprocal and the Galois conjugate
coincide up to sign — true for φ and the silver ratio, false for every other
base tested.

---

## 5. Materials and Methods

The theoretical framework was developed analytically. The conservation law
(§2) is a postulate with its exponent now fixed by §3.1. The EGY correspondence
and the deficit identity (§3.1, §3.2) were verified over 20,000 random pure and
20,000 random mixed qubit states sampled uniformly on and in the Bloch sphere.
The Hurwitz checks (§4.2) were computed from continued-fraction expansions at
exact algebraic values. The Pisot/termination table (§4.6) was computed at 400
decimal digits with a 10⁻³⁰⁰ tolerance.

All scripts: `github.com/0x-auth/darmiyan-fs/review/`.

---

## 6. Withdrawn from V5

### 6.1 The φ×√n simulation evidence

V5 §6.1 reported mean Pearson r ≈ 0.726 between cumulative semantic distance
D(n) and √n, from φ-weighted random walks, as evidence for φ-scaling.

Two problems.

**It is not reproducible from the text.** An independent reimplementation from
the V5 §5.2 description gives r ≈ 0.24, not 0.726. The normalisation, the
distance definition, or the step model must differ from what the prose
specifies. The description is insufficient to rebuild the experiment.

**The φ weighting does no work.** With the weight swapped and nothing else
changed:

| weighting | mean r with √n |
|---|---|
| φ⁻ⁱ (V5's) | 0.2419 |
| e⁻ⁱ | 0.1988 |
| 2⁻ⁱ | 0.2163 |
| 1/i | 0.4404 |
| **uniform (no φ anywhere)** | **0.9950** |
| random | 0.9927 |

√n scaling is a property of the random walk. Geometric decay *degrades* it,
because decaying weights make later steps negligible. The φ-weighted arm is the
worst of six schemes and the arm with no φ in it is the best.

**Status: withdrawn.** V5's own limitation note said the simulations do not
confirm the φ prefactor in physical data. The stronger statement holds: they do
not establish that φ weighting produces √n scaling at all.

### 6.2 The measurement-problem claim

V5 presented the framework as dissolving the measurement problem and the black
hole information paradox.

It does neither. Every quantity in §3 is computable from ρ, and ρ is what the
measurement problem is *about*. The framework gives clean geometric
bookkeeping for the storage–reference trade-off and says nothing about why one
outcome occurs. "TrD → 0 inside the horizon" is a restatement of "no accessible
reference structure", which is the paradox, not its resolution.

**Status: withdrawn.**

---

## 7. Falsifiable Predictions

Predictions 1 and 2 of V5 depended on the linear law and on the ΛG operator
formalism respectively. Prediction 2 was already conservatively retracted in
V5. Prediction 1 is withdrawn here: it asserted Γ_φ/Γ_uniform ≈ 1/φ with no
derivation connecting φ to a decoherence rate.

The V6 law makes one prediction that is sharp, already partially confirmed by
existing interferometry, and would falsify the framework if it failed.

**Prediction: the deficit is the mixedness, with coefficient exactly 2.**

For any two-path interferometer with measurable 𝒟 and 𝒱, and independently
determined state purity:

$$1 - (\mathcal{D}^2 + \mathcal{V}^2) = 2\left(1 - \mathrm{Tr}\,\rho^2\right)$$

A measured coefficient differing from 2 beyond experimental error falsifies the
identification of (TD, TrD) with (𝒟, 𝒱). Note this is a **derived** prediction
of standard quantum mechanics under the V6 identification, not a novel physical
effect. The framework's content is the identification, not new physics.

**This is the honest scope.** V6 makes no prediction that departs from standard
quantum mechanics.

---

## 8. Scope and Limitations

This is a framework, not a proof, and V6 is narrower than V5 in every
direction.

**What survives:** the law TD² + TrD² = 1 is the EGY duality relation for pure
states; the radial deficit is exactly twice the linear entropy; the φ-boundary
follows from Hurwitz's theorem without assuming the golden section; Pisot is
the class for which self-similar subdivision terminates.

**What does not:** three of V5's structural mappings, only one of which is an
identity; the simulation evidence; the measurement-problem and information-
paradox claims; the uniqueness of φ among self-similarity attractors.

**What is unresolved.** Every quantity here is a ratio. TD/TrD fixes a balance
and nothing internal to the framework supplies a scale. The same gap appears in
the author's related work on settlement depth, walker proper time, and
verification, where in each case the structure fixes the shape and something
outside must supply the unit. It is not resolved here either.

**The parsimony remains the primary virtue and the primary risk.** One
postulate, one relation, one boundary. If the identification in §3 is right,
the bookkeeping is explanatory. If it is wrong, the framework is wrong. There
is no intermediate position.

---

## 9. Conclusion

Versions 1 through 5 stated the conservation law as TD + TrD = 1. That equation
places the accessible states on a line, where the framework's claimed mappings
are satisfied by every point and therefore carry no information, and where the
deficit is identically zero.

The correct constraint is TD² + TrD² = 1. It places the states on a quarter
circle, it reproduces the Englert–Greenberger–Yasin duality relation exactly
for pure states, and its radial deficit equals twice the linear entropy — so
the distance from the arc measures how much of a system lives outside itself.
The interior of the disc is unreachable without an environment.

The φ-boundary follows from Hurwitz's theorem rather than from a restatement of
the golden section. φ is the maximally incommensurate storage–reference
balance: the ratio at which the balance never closes on a finite repeat, and
therefore the ratio at which self-reference never terminates.

The operational definition of TrD: the degree to which a system's identity is
constituted by reference rather than storage. A Bell pair: TrD ≈ 1. A classical
bit: TrD ≈ 0. A human brain: intermediate, and the distance from the arc is how
much of it is in other people.

*It was never spooky action. It was always a boundary — and the boundary is a
circle, not a line.*

---

## Data Availability

All verification scripts are at `github.com/0x-auth/darmiyan-fs` under
`review/`: `does_it_bite.py` (§3), `phi_noncircular.py` (§4),
`trd_review.py` (§4.5, §6.1), and `../numbers/mirrors.py` (§4.6). Seed 515.
Dependencies: Python 3, numpy, mpmath.

## Acknowledgments

Developed in dialogue with Claude (Anthropic). Every correction in V6
originated in a test the previous version failed; the tests are published
alongside the paper rather than described. All scientific claims and
conclusions are the sole responsibility of the author. No funding was received.

## References

[1] Bohr N. The quantum postulate and the recent development of atomic theory. *Nature* 1928;121:580–590.
[2] Englert BG. Fringe visibility and which-way information: an inequality. *Phys Rev Lett* 1996;77(11):2154.
[3] Greenberger DM, Yasin A. Simultaneous wave and particle knowledge in a neutron interferometer. *Phys Lett A* 1988;128(8):391–394.
[4] Jaeger G, Shimony A, Vaidman L. Two interferometric complementarities. *Phys Rev A* 1995;51(1):54.
[5] Heisenberg W. Über den anschaulichen Inhalt der quantentheoretischen Kinematik und Mechanik. *Z Phys* 1927;43:172–198.
[6] Zurek WH. Decoherence, einselection, and the quantum origins of the classical. *Rev Mod Phys* 2003;75(3):715.
[7] Hurwitz A. Ueber die angenäherte Darstellung der Irrationalzahlen durch rationale Brüche. *Math Ann* 1891;39:279–284.
[8] Khinchin AYa. *Continued Fractions*. Dover Publications, 1964.
[9] Cassels JWS. *An Introduction to Diophantine Approximation*. Cambridge, 1957.
[10] Bergman G. A number system with an irrational base. *Math Mag* 1957;31(2):98–110.
[11] Frougny C, Solomyak B. Finite beta-expansions. *Ergod Th Dynam Sys* 1992;12(4):713–723.
[12] Siegel CL. Algebraic integers whose conjugates lie in the unit circle. *Duke Math J* 1944;11:597–602.
[13] Srivastava A. The Darmiyan Fixed-Point Theorem. Zenodo, March 2026.
[14] Srivastava A. Self-referential structure, emergent time, and the forward/reverse asymmetry. Zenodo, September 2026. DOI 10.5281/zenodo.22944787.

---

*Seed 515. Dedicated to the space between — where meaning lives.*
