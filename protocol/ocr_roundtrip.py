"""
Mirror protocol, real-world test: does the round trip catch OCR mistakes
without being told the right answer?

forward  f : image -> text        (a real OCR engine, RapidOCR, offline)
mirror   g : text  -> image       (renderer; it searches 3 fonts x 7 sizes for
                                   the best match, so it is not told the font)
residual r : 1 - best correlation between the original image and g(f(image))

Two-view signal (the z / z' idea): read the image a second way (upscaled 2x)
and measure how much the two readings disagree.

Ground truth is used ONLY to score the signals afterwards.
Main question: do the signals catch wrong reads among images of the SAME
quality, or do they only detect bad images? Quality is held fixed by
stratifying on how well the TRUE text re-renders (analysis only).

Run: python3 ocr_roundtrip.py [n_samples]   (about 10 minutes for 400)
"""
import sys, random, re, io, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from rapidocr_onnxruntime import RapidOCR

FONTS = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
SIZES = list(range(14, 34, 3))
rng = random.Random(515); nrng = np.random.default_rng(515)
engine = RapidOCR()


def lines(n):
    import pydoc_data.topics as T
    words = re.findall(r"[A-Za-z][A-Za-z0-9']{1,11}|\d{1,4}", " ".join(T.topics.values()))
    out = []
    while len(out) < n:
        k = rng.randint(3, 6); i = rng.randrange(len(words) - k)
        s = " ".join(words[i:i + k])
        if 12 <= len(s) <= 40: out.append(s)
    return out


def render(text, font, size, pad=40):
    f = ImageFont.truetype(font, size)
    w = int(f.getlength(text)) + 2 * pad
    im = Image.new("L", (max(w, 20), size + 2 * pad), 255)
    ImageDraw.Draw(im).text((pad, pad), text, font=f, fill=0)
    return im


def degrade(im, q):
    """q in [0,1]: 0 clean, 1 very hard."""
    im = im.rotate(rng.uniform(-2.5, 2.5) * q, expand=True, fillcolor=255)
    im = im.filter(ImageFilter.GaussianBlur(2.6 * q * rng.uniform(.5, 1)))
    a = np.asarray(im, np.float32)
    c = 1 - 0.6 * q * rng.uniform(.5, 1)                     # contrast loss
    a = 255 - (255 - a) * c
    a = a + nrng.normal(0, 75 * q * rng.uniform(.5, 1), a.shape)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=int(95 - 87 * q)); buf.seek(0)
    return Image.open(buf).convert("L")


def read(im):
    res, _ = engine(np.asarray(im.convert("RGB")))
    if not res: return "", 0.0
    res = sorted(res, key=lambda r: r[0][0][0])
    return " ".join(r[1] for r in res), float(np.mean([float(r[2]) for r in res]))


def ink_crop(a, thr):
    ys, xs = np.where(a < thr)
    if len(xs) < 5: return None
    return a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def match(orig, text):
    """best correlation between the original and a fresh rendering of text."""
    if not text.strip(): return 0.0
    a = np.asarray(orig.filter(ImageFilter.GaussianBlur(1)), np.float32)
    thr = (a.max() + a.min()) / 2
    oc = ink_crop(a, thr)
    if oc is None: return 0.0
    oc = (oc - oc.mean()) / (oc.std() + 1e-6)
    best = 0.0
    for font in FONTS:
        for size in SIZES:
            r = np.asarray(render(text, font, size).filter(ImageFilter.GaussianBlur(1)), np.float32)
            rc = ink_crop(r, 128)
            if rc is None: continue
            rc = np.asarray(Image.fromarray(rc.astype(np.uint8)).resize((oc.shape[1], oc.shape[0])), np.float32)
            rc = (rc - rc.mean()) / (rc.std() + 1e-6)
            best = max(best, float((oc * rc).mean()))
    return best


def edit(a, b):
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (ca != cb))
    return d[-1]


def norm(s): return " ".join(s.split())


def auc(score, bad):
    s = np.asarray(score); b = np.asarray(bad, bool)
    if b.all() or (~b).all(): return float("nan")
    pos, neg = s[b], s[~b]
    return float(((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()))


def main(n=400):
    rows = []
    for k, text in enumerate(lines(n)):
        font = rng.choice(FONTS); size = rng.choice(range(16, 31)); q = rng.uniform(0.0, 0.55)
        img = degrade(render(text, font, size), q)
        got, conf = read(img)
        got2, _ = read(img.resize((img.width * 2, img.height * 2), Image.LANCZOS))
        resid = 1 - match(img, got)
        twoview = edit(norm(got), norm(got2)) / max(1, len(norm(got)), len(norm(got2)))
        quality = match(img, text)                     # analysis only: uses the truth
        cer = edit(norm(got), norm(text)) / len(norm(text))
        rows.append((resid, 1 - conf, twoview, quality, cer, norm(got) != norm(text)))
        if (k + 1) % 50 == 0: print(f"  {k+1}/{n}", flush=True)
    R = np.array(rows, dtype=float)
    resid, unconf, twov, qual, cer, bad = R.T; bad = bad.astype(bool)
    print(f"\n{n} images; wrong reads: {bad.sum()} ({bad.mean():.0%}); mean character error {cer.mean():.3f}\n")
    rank = lambda x: np.argsort(np.argsort(x)) / len(x)
    combo = rank(resid) + rank(unconf) + rank(twov)
    sig = {"round trip (redraw and compare)": resid, "engine's own confidence": unconf,
           "two views disagree": twov, "all three combined": combo,
           "image quality only (uses truth)": -qual}
    bins = np.quantile(qual, [0, .2, .4, .6, .8, 1.0])
    print(f"{'signal':34}{'AUC overall':>12}{'AUC within same quality':>25}{'catch @ top 20%':>17}")
    for name, s in sig.items():
        within = []
        for lo, hi in zip(bins[:-1], bins[1:]):
            m = (qual >= lo) & (qual <= hi)
            a = auc(s[m], bad[m])
            if not np.isnan(a): within.append(a)
        top = s >= np.quantile(s, .8)
        print(f"{name:34}{auc(s, bad):>12.3f}{np.mean(within):>25.3f}{bad[top].sum()/max(1,bad.sum()):>17.0%}")
    print("\nAUC 0.5 = no better than a coin; 1.0 = perfect. 'catch @ top 20%' = share of all wrong reads"
          "\nfound by checking only the 20% of images the signal ranks most suspicious.")
    np.save("ocr_rows.npy", R)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 400)
