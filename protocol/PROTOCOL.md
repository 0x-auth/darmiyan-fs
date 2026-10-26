# Mirror protocol v0

Every transform is registered with its mirror. Every output carries how far the
round trip misses. That miss tells you which outputs to trust, without labels.

It comes from the becoming plane: one view alone is two-to-one (z), two views
together fix the cause (z and z′), and the round trip has an invariant
(z² − z′² = 4i). Outside mathematics the invariant is "there and back returns
what you started with", and whatever does not come back is the error.

## The four rules

1. **Pair.** Register every transform f with its mirror g and a way to compare
   inputs, d.
2. **Residual.** Every output y = f(x) carries r = d(x, g(y)). Store it with y.
3. **Anchors.** Once, on a few inputs whose right output is known, place the line
   that best separates right outputs from wrong ones. After that no labels are
   needed: r below the line is trusted, r at or above it goes to review. Keep the
   anchors and re-check them from time to time, because two learned mirrors can
   drift together and still agree with each other.
4. **Second view.** When one view cannot decide (two causes give the same
   output), add the other view. Together they decide.

Memory form: store the difference between a thing and its mirror, and rebuild
the thing with a fixed rule. The residual flags the memories the difference
cannot decide.

```python
from mirror_protocol import Pair
pair = Pair(forward, mirror, compare)
pair.calibrate(anchors)              # [(x, y_true), ...]
y, residual, status = pair.route(x)  # status: "trusted" or "review"
```

## Validated on a real OCR engine (26 Oct 2026)

`ocr_roundtrip.py`: 400 text lines rendered in 3 fonts at 16 to 30 px, degraded
(blur, noise, contrast loss, rotation, JPEG), read by RapidOCR (offline). The
mirror redraws the read text, searching 3 fonts × 7 sizes, and compares with the
original. 30% of reads were wrong, mostly subtly: merged words, swapped letters,
at high engine confidence. Ground truth is used only to score the signals.

| signal (no right answers used) | catches wrong reads, AUC | among equally bad images | wrong reads found in top 20% |
|---|---|---|---|
| **round trip** | **0.964** | **0.973** | **65%** (ceiling 67%) |
| two views disagree | 0.816 | 0.814 | 51% |
| engine's own confidence | 0.739 | 0.740 | 41% |
| image quality alone | 0.561 | 0.559 | 24% |

The round trip is not just detecting bad images: holding image quality fixed, it
stays at 0.973. Combining the three signals (0.953) did not beat the round trip
alone.

`ocr_route.py`, the protocol end to end: the line was set on the first 200 images,
then 200 new images were routed.

- 26% of images sent to review, catching 48 of 56 wrong reads (86%).
- The 147 outputs trusted without review were 94.6% correct, against 72.0% if every output is trusted.

Reference pairs in `mirror_protocol.py`:

- compress ↔ decompress: residual 0 on 200 random inputs.
- memory (store t − 1/t, rebuild with S → b + 1/S):
  - memories the difference can decide: 150 of 150 trusted;
  - memories on |t| = 1, where the difference cannot decide: 148 of 150 sent to review. 2 slipped because the turning iteration landed near t by chance.

## Limits

- The degradations are synthetic, and the mirror's font search included the true
  font. On real scans with unknown fonts the mirror is weaker, and so is the
  residual. A protocol is only as good as its mirror.
- AUC was computed on one run of 400 images; the seed is fixed (515).
- Nothing here trains one side from the other yet. The renderer could generate
  unlimited labelled pages for the reader; that is the next test.
