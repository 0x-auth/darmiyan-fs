"""
Mirror protocol v0 -- core.

Every transform is registered with its mirror. Every output carries the
round-trip residual: how far mirror(forward(x)) lands from x. A few anchors
(inputs with known-true outputs) set the line between "trusted" and "review".
No labels are needed after that.

    pair = Pair(forward, mirror, compare)
    pair.calibrate(anchors)          # [(x, y_true), ...]
    y, residual, status = pair.route(x)

Three reference pairs live at the bottom of this file:
  exact   compress <-> decompress           (residual is always 0)
  memory  store t - 1/t <-> rebuild t       (fails exactly where |t| = 1)
  ocr     image -> text <-> text -> image   (see ocr_roundtrip.py)

Run:  python3 mirror_protocol.py
"""
import zlib, cmath, random


class Pair:
    def __init__(self, forward, mirror, compare, name=""):
        self.forward, self.mirror, self.compare, self.name = forward, mirror, compare, name
        self.line = None

    def check(self, x):
        y = self.forward(x)
        return y, float(self.compare(x, self.mirror(y)))

    def calibrate(self, anchors, same=lambda a, b: a == b):
        """anchors: [(x, y_true)]. Picks the residual line that best separates
        right outputs from wrong ones (largest true-catch minus false-alarm rate)."""
        rows = []
        for x, y_true in anchors:
            y, r = self.check(x)
            rows.append((r, not same(y, y_true)))
        u = sorted({r for r, _ in rows})
        cands = [(a + b) / 2 for a, b in zip(u, u[1:])] + [float("inf")]   # lines between observed residuals
        nb = sum(b for _, b in rows) or 1
        ng = sum(not b for _, b in rows) or 1
        best = max(cands, key=lambda c: sum(b and r >= c for r, b in rows) / nb
                                       - sum((not b) and r >= c for r, b in rows) / ng)
        self.line = best
        return best

    def route(self, x):
        y, r = self.check(x)
        status = "trusted" if self.line is not None and r < self.line else "review"
        return y, r, status


# ---------------- reference pair 1: exact ----------------
exact = Pair(lambda b: zlib.compress(b), lambda c: zlib.decompress(c),
             lambda a, b: 0.0 if a == b else 1.0, "compress/decompress")


# ---------------- reference pair 2: memory as stored difference ----------------
def store_difference(t):          # forward: keep only t - 1/t
    return t - 1 / t

def rebuild(b, steps=400):        # mirror: the fixed rule S -> b + 1/S, from any start
    S = complex(0.3, 0.7)
    for _ in range(steps):
        S = b + 1 / S
    return S

memory = Pair(store_difference, rebuild, lambda t, t2: abs(t - t2), "stored difference/rebuild")


if __name__ == "__main__":
    rng = random.Random(515)
    data = [bytes(rng.randrange(256) for _ in range(rng.randint(1, 200))) for _ in range(200)]
    print("exact pair, 200 random byte strings: max residual",
          max(exact.check(d)[1] for d in data))

    # memory pair: causes with |t| > 1 rebuild exactly; on |t| = 1 the difference
    # does not decide between t and -1/t (the slit), and the residual says so.
    off = [cmath.rect(rng.uniform(1.05, 3), rng.uniform(-3.1, 3.1)) for _ in range(300)]
    on = [cmath.rect(1.0, rng.uniform(-3.1, 3.1)) for _ in range(300)]
    anchors = [(t, t) for t in off[:150] + on[:150]]
    same = lambda b, t: abs(rebuild(b) - t) < 1e-6      # right = the stored difference rebuilds t
    line = memory.calibrate(anchors, same)
    test = [(t, "off") for t in off[150:]] + [(t, "on") for t in on[150:]]
    routed = [(kind, memory.route(t)[2]) for t, kind in test]
    print(f"memory pair: line {line:.2e}; |t|>1 trusted {sum(k=='off' and s=='trusted' for k,s in routed)}/150;"
          f" |t|=1 sent to review {sum(k=='on' and s=='review' for k,s in routed)}/150")
