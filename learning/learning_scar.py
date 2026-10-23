"""
Does learning leave a scar?  (darmiyan-fs / learning)
------------------------------------------------------
Question (23 Oct 2026): is what learning leaves behind the same thing as the
Darmiyan V4 scar -- identity displaced, behaviour returns, the change readable
only indirectly?

Setup: a small network (10 inputs, 32 hidden, 2 outputs; numpy only) learns
task A. Then three branches, each followed by the same 4000 steps back on A:
  B-struck : 2000 steps on task B first
  C-struck : 2000 steps on an unrelated task C first
  control  : 2000 more steps on A instead (same total training)
Measured on held-out data, mean over 12 seeds:
  A accuracy                 does behaviour on A come back?
  same A answers             fraction of test inputs answered the same as control
  |W - W_control|            how far the weights ended up from the control
  B accuracy                 is B visible in behaviour after the return?
  relearn B                  steps to reach 85% on B starting from that network

Reading: if B-struck relearns B faster than C-struck, the trace is of B
itself, not just a network loosened by any detour.

Run:  python3 learning_scar.py      (about 20 s)
"""
import numpy as np

D, H = 10, 32


def teacher(rng):
    return rng.normal(size=(D, 16)), rng.normal(size=(16,))


def labels(X, T):
    return (np.tanh(X @ T[0]) @ T[1] > 0).astype(int)


def init(rng):
    return [rng.normal(scale=.3, size=(D, H)), np.zeros(H),
            rng.normal(scale=.3, size=(H, 2)), np.zeros(2)]


def fwd(W, X):
    h = np.tanh(X @ W[0] + W[1])
    z = h @ W[2] + W[3]
    z -= z.max(1, keepdims=True)
    p = np.exp(z)
    return h, p / p.sum(1, keepdims=True)


def acc(W, X, y):
    return (fwd(W, X)[1].argmax(1) == y).mean()


def step(W, X, y, lr=0.2):
    h, p = fwd(W, X)
    g = p.copy()
    g[np.arange(len(y)), y] -= 1
    g /= len(y)
    gh = (g @ W[2].T) * (1 - h * h)
    return [W[0] - lr * X.T @ gh, W[1] - lr * gh.sum(0),
            W[2] - lr * h.T @ g, W[3] - lr * g.sum(0)]


def train(W, X, y, n, rng):
    for _ in range(n):
        i = rng.integers(0, len(y), 64)
        W = step(W, X[i], y[i])
    return W


def flat(W):
    return np.concatenate([w.ravel() for w in W])


def relearn(W, X, y, Xt, yt, target=0.85, cap=6000):
    rng = np.random.default_rng(7)
    for s in range(0, cap + 1, 25):
        if acc(W, Xt, yt) >= target:
            return s
        W = train(W, X, y, 25, rng)
    return cap


def run(seed, strike=2000, back=4000):
    rng = np.random.default_rng(seed)
    TA, TB = teacher(rng), teacher(rng)
    TC = teacher(np.random.default_rng(seed + 999))
    XA, XB, XtA, XtB = [rng.normal(size=(3000, D)) for _ in range(4)]
    XC = np.random.default_rng(seed + 77).normal(size=(3000, D))
    yA, yB, ytA, ytB, yC = (labels(XA, TA), labels(XB, TB), labels(XtA, TA),
                            labels(XtB, TB), labels(XC, TC))
    W1 = train(init(rng), XA, yA, 4000, rng)              # task A learned

    out = {}
    for name, X, y in (("B-struck", XB, yB), ("C-struck", XC, yC), ("control", XA, yA)):
        r = np.random.default_rng(1000 + seed)
        W = train(W1, X, y, strike, r)                    # the detour (or more A)
        out[name] = train(W, XA, yA, back, r)             # return to A
    ctrl = out["control"]
    rows = {}
    for name, W in out.items():
        rows[name] = (acc(W, XtA, ytA),
                      np.mean(fwd(W, XtA)[1].argmax(1) == fwd(ctrl, XtA)[1].argmax(1)),
                      np.linalg.norm(flat(W) - flat(ctrl)),
                      acc(W, XtB, ytB),
                      relearn(W, XB, yB, XtB, ytB))
    rows["fresh net"] = (np.nan, np.nan, np.nan, np.nan,
                         relearn(init(np.random.default_rng(seed + 50)), XB, yB, XtB, ytB))
    return rows


def main(seeds=12):
    names = ("B-struck", "C-struck", "control", "fresh net")
    allr = {n: [] for n in names}
    for s in range(seeds):
        r = run(s)
        for n in names:
            allr[n].append(r[n])
    print(f"{seeds} seeds; strike 2000 steps, then 4000 steps back on A\n")
    print(f"{'branch':>10} {'A acc':>7} {'same A answers':>15} {'|W-Wctrl|':>10} {'B acc':>7} "
          f"{'relearn B mean':>15} {'median':>7}")
    for n in names:
        a = np.array(allr[n], dtype=float)
        m = np.nanmean(a, 0) if n != "fresh net" else [np.nan] * 4 + [a[:, 4].mean()]
        med = np.median(a[:, 4])
        f = lambda v, w, d: (" " * (w - 1) + "-") if np.isnan(v) else f"{v:>{w}.{d}f}"
        print(f"{n:>10} {f(m[0],7,3)} {f(m[1],15,3)} {f(m[2],10,2)} {f(m[3],7,3)} "
              f"{m[4]:>15.0f} {med:>7.0f}")
    b = np.array(allr["B-struck"])[:, 4]
    c = np.array(allr["C-struck"])[:, 4]
    print(f"\nB-struck relearns B faster than C-struck in {(b < c).sum()}/{seeds} seeds, "
          f"ties {(b == c).sum()}, slower {(b > c).sum()}")
    print("per seed (B-struck, C-struck):", list(zip(b.astype(int).tolist(), c.astype(int).tolist())))


if __name__ == "__main__":
    main()
