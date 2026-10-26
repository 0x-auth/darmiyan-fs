"""End-to-end check of the protocol on the OCR results (ocr_rows.npy from ocr_roundtrip.py):
calibrate the residual line on the first 200 images (anchors), then route the other 200."""
import numpy as np
R = np.load("ocr_rows.npy"); resid, bad = R[:, 0], R[:, 5].astype(bool)
cal, test = slice(0, 200), slice(200, 400)
def youden(r, b):
    c = np.r_[np.unique(r), np.inf]
    score = [(b & (r >= x)).sum() / max(1, b.sum()) - ((~b) & (r >= x)).sum() / max(1, (~b).sum()) for x in c]
    return c[int(np.argmax(score))]
line = youden(resid[cal], bad[cal])
r, b = resid[test], bad[test]; review = r >= line
print(f"line set on 200 anchors: residual {line:.4f}")
print(f"200 new images: {b.sum()} read wrong")
print(f"  sent to review: {review.sum()} images ({review.mean():.0%})")
print(f"  wrong reads caught by review: {(b & review).sum()}/{b.sum()} ({(b & review).sum()/b.sum():.0%})")
print(f"  trusted without review: {(~review).sum()}, of which correct: {((~b) & ~review).sum()} ({((~b) & ~review).sum()/max(1,(~review).sum()):.1%})")
print(f"  without the protocol, trusting everything: {(~b).mean():.1%} correct")
