# darmiyan — the undefined is recursion a walker cannot terminate on

    meaning -> meaning

A symlink whose target is its own name. Well formed, present in `ls`, and:

    $ realpath meaning
    realpath: meaning: Too many levels of symbolic links      (ELOOP, errno 40)

Nothing is broken. What fails is the attempt to terminate a walk on a fixed
point. `readlink meaning` returns `meaning` instantly — the information was
always there.

## The three sectors, as filesystem behaviour

A Möbius relation x → (ax+b)/(cx+d) has three kinds, set by Δ = tr² − 4det.
Laid down as symlinks, each fails differently:

| sector | link shape | OS verdict | hop-count finds |
|---|---|---|---|
| parabolic | self-link | ELOOP | 0 hops, self |
| rotation | cycle | ELOOP | n hops, cycle of n |
| boost | open chain | dangling | runs out |

`darmiyan.py` recovers the sector from how the walk ends. The writer lays
down symlinks and records no sector, no Δ, no a b c d.

Recovered correctly: identity (Δ=0, self-link), negrecip (Δ=−4, order 2),
order3 (Δ=−3, order 3), golden (Δ=5), silver (Δ=8).

**Misclassified, and honestly so:** `shift` is x → x+1, parabolic with Δ=0,
but its fixed point is at infinity. A finite walker cannot reach it, so it is
indistinguishable from a boost. The fixed point exists; it is not in this
chart.

## Two things the walker cannot do

**ELOOP conflates order 1 with order 2.** The OS returns the same error for a
self-link and for a two-cycle. Telling them apart needs hop-counting, which
is a finer instrument. That is ε, in the filesystem rather than in a theory.

**A truncated chain looks dangling.** Convergence and escape are the same
thing below a resolution.

## emerge.py — the same point with integers

`emerge.py` lays down chains of directories holding one integer each,
`round(x · scale)`. Nothing records the law. A reader recovers a, b, c, d
from four consecutive values, and Δ from those.

The result that matters is the scale sweep:

| scale | distinct states | closes? |
|---|---|---|
| 10 | 5 | yes |
| 10² | 6 | yes |
| 10⁴ | 12 | yes |
| 10⁶ | 16 | yes |
| 10⁹ | 24 | yes |

The same relation is a short cycle to a coarse walker and a long chain to a
fine one. Nothing put that in — it is what a finite filesystem does to an
infinite process.

And the law recovery fails on rounded values: exact cases (identity, shift)
come back clean, rounded ones return garbage fractions. Rounding destroys
the rational structure the inference needs. That failure is the same ε
result arriving through the solver instead of through the walk.

## The coordinate artifact

x → (ax+b)/(cx+d) is undefined where cx + d = 0. That is not a hole — it is
the point sent to infinity, and on the Riemann sphere infinity is ordinary.

Same structure as Schwarzschild: g_tt blows up at r = r_s while the
Kretschmann scalar stays finite. The horizon is a coordinate singularity;
r = 0 is the real one.

ELOOP is the walker's chart failing. `readlink` is the other chart.

## Files

| file | what it does |
|---|---|
| `darmiyan.py` | self-links, cycles and chains; sector from how the walk fails |
| `emerge.py` | integer states, law inference, the ε sweep |
