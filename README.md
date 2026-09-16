# darmiyan.fs

A minimal self-recursive universe on a Unix filesystem.
Folders are states, symlinks are relations, observers are walkers, and the floor of distinction (ε) lives inside the universe.

> Time is not fundamental. It is the local error a system registers when it holds its before and after at once, and it vanishes where that error falls below what the system can distinguish.

## Files

| file | what it is |
|---|---|
| `darmiyan_fs.py` | **The model (v1).** Successors are created only when observed; each node closes (`next -> .`) only when its own error `|f(x) - x|` falls below the universe's own `.ε`. States are recognized by content, not name. |
| `reality_fs.py` | The first attempt: a precomputed Planck-to-universe ladder. Kept as the "outside" view, with time imposed from outside (all states built first, links laid afterward). |
| `experiments.py` | Reproduces the relativity results below. |

```bash
python3 darmiyan_fs.py universe 16     # build and observe a universe at 16-digit resolution
python3 experiments.py                 # needs numpy, sympy
```

## Structure of a universe

```
universe/
  .ε              floor of distinction (stored inside)
  Ø -> /tmp/void  named but nonexistent: the undefined origin
  fwd/0 ... fwd/N   each node: x, prev, next     (x -> 1 + 1/x)
      0/prev -> Ø
      N/next -> .   closure
  bwd/0 ... bwd/M   the exact inverse            (x -> 1/(x - 1))
```

## Findings

**Emerges without being put in**
- Forward closes on φ, backward on −1/φ. Product −1, sum 1, difference √5.
- Ticks per digit of resolution → 1/log₁₀(φ²) = 2.3925 (1.3885 bits per tick).
- Hiding a difference (forward) and revealing it (backward) take the same number of ticks.
- Timeless form: the slopes of the rule at its two fixed points multiply to exactly 1 (true for every Möbius rule, and only for them).

**Relativity from x → n + 1/x**
- Each metallic rule is a Lorentz boost with a mirror: v/c = n√(n²+4)/(n²+2), γ = (n²+2)/2 (gold 3/2, silver 3, bronze 11/2).
- Composition reproduces Einstein addition exactly (gold∘gold γ = 7/2; gold∘silver γ = 15/2).
- Non-collinear composition carries a Wigner rotation of ±28.07° = 2·arctan(1/4); reversing order flips its sign.
- Gold relative to silver: γ = 3/2, Wigner rotation 16.26° = 2·arctan(1/7).
- Observers at the same floor disagree by rapidity, not γ: gold/silver tick ratio → 1.8316.
- Silver reading gold's history in its own coordinates sees gold close within one tick of gold's own count (proper time invariance).

**At the floor**
- At high precision the closure can be a 2-cycle (last digit flips forever, error exactly ε), seen identically from other frames.
- Recognizing states by name instead of content turns that jitter into a runaway (v0 created 1.3M folders before the disk filled).

## Origin

A runaway `zip -r` spent 5 CPU-hours walking a self-referential directory (`.cognitive_os/∞/meaning/`, up to 200 self-links per folder) because it could not recognize it was walking in itself. `realpath` resolves the same loop instantly. Everything here grew from that difference.

## Status

Exploratory. The Möbius–Lorentz correspondence is established mathematics; the metallic ladder, the construct, and the reading of time as emergent local error are this project's interpretation.
