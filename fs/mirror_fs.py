#!/usr/bin/env python3
"""
================================================================================
MIRROR_FS -- what is the mirror of a reference, and why it is not local
================================================================================

THE QUESTION

A symlink is a name that resolves to another name. Forward:

    readlink(p)  ->  "where does p point?"

What is the reverse?

    who_points_at(p)  ->  "which names resolve to p?"

The claim tested here: the forward direction is LOCAL and O(1). The reverse
direction is GLOBAL and has no bound short of the whole filesystem. They are
not two operations of the same kind. That asymmetry is the mirror, and it is
the reason the mirror is not local.

ALSO TESTED

  - st_nlink stores the MAGNITUDE of the mirror but not its DIRECTION.
    The kernel counts how many names point at an inode. It does not know
    which ones, and cannot be asked.
  - For SYMLINKS there is no magnitude either. st_nlink does not count
    them. The mirror of a symlink is entirely absent from the structure.
  - Time enters only through the reverse direction.

Run:  python3 mirror_fs.py
================================================================================
"""

import os
import shutil
import time

ROOT = "/tmp/mirror_fs"


def build(n_dirs=200, per_dir=40):
    """A filesystem with one target and many references scattered through it."""
    os.makedirs(ROOT, exist_ok=True)
    tgt = os.path.join(ROOT, "target")
    with open(tgt, "w") as f:
        f.write("the thing being pointed at\n")

    hard, soft = [], []
    for d in range(n_dirs):
        sub = os.path.join(ROOT, f"d{d:03d}")
        os.makedirs(sub, exist_ok=True)
        for k in range(per_dir):
            # decoys: most entries point at nothing interesting
            p = os.path.join(sub, f"f{k:02d}")
            if not os.path.lexists(p):
                open(p, "w").close()
        # plant a small number of real references
        if d % 37 == 0:
            h = os.path.join(sub, "hardref")
            if not os.path.lexists(h):
                os.link(tgt, h)
            hard.append(h)
        if d % 53 == 0:
            s = os.path.join(sub, "softref")
            if not os.path.lexists(s):
                os.symlink(os.path.relpath(tgt, sub), s)
            soft.append(s)
    return tgt, hard, soft


def forward(p, reps=20000):
    """readlink: one inode read. Measure it."""
    t0 = time.perf_counter()
    for _ in range(reps):
        os.readlink(p)
    return (time.perf_counter() - t0) / reps


def reverse_hard(tgt):
    """Find every NAME that is a hard link to tgt. Requires a full walk."""
    st = os.stat(tgt)
    found, examined = [], 0
    t0 = time.perf_counter()
    for dp, dn, fn in os.walk(ROOT):
        for f in fn:
            p = os.path.join(dp, f)
            examined += 1
            try:
                s = os.lstat(p)
            except OSError:
                continue
            if s.st_ino == st.st_ino and s.st_dev == st.st_dev and p != tgt:
                found.append(p)
    return found, examined, time.perf_counter() - t0


def reverse_soft(tgt):
    """Find every SYMLINK that resolves to tgt. Also a full walk, and the
    kernel offers no counter at all to shortcut it."""
    real = os.path.realpath(tgt)
    found, examined = [], 0
    t0 = time.perf_counter()
    for dp, dn, fn in os.walk(ROOT):
        for f in fn + dn:
            p = os.path.join(dp, f)
            if not os.path.islink(p):
                continue
            examined += 1
            try:
                if os.path.realpath(p) == real:
                    found.append(p)
            except OSError:
                continue
    return found, examined, time.perf_counter() - t0


def main():
    if os.path.exists(ROOT):
        shutil.rmtree(ROOT)
    tgt, hard, soft = build()

    print("=" * 78)
    print("1. FORWARD IS LOCAL")
    print("=" * 78)
    print()
    s = soft[0]
    per = forward(s)
    print(f"  readlink({os.path.relpath(s, ROOT)})  ->  {os.readlink(s)}")
    print(f"  cost: {per*1e6:.3f} us per call, {20000} calls")
    print()
    print("  one inode. the answer is stored AT the name. nothing is")
    print("  searched. this is why a symlink walk has a proper time at all:")
    print("  each hop costs the same, so hop count is a clock.")
    print()

    print("=" * 78)
    print("2. REVERSE IS GLOBAL")
    print("=" * 78)
    print()
    fh, eh, th = reverse_hard(tgt)
    fs_, es, ts = reverse_soft(tgt)
    print(f"  {'question':>34} {'answer':>8} {'entries examined':>18} "
          f"{'seconds':>10}")
    print("  " + "-" * 74)
    print(f"  {'readlink(p) -- forward':>34} {'1':>8} {'1':>18} "
          f"{per:10.8f}")
    print(f"  {'which names hard-link tgt?':>34} {len(fh):>8} {eh:>18} "
          f"{th:10.6f}")
    print(f"  {'which symlinks resolve to tgt?':>34} {len(fs_):>8} {es:>18} "
          f"{ts:10.6f}")
    print()
    print(f"  forward / reverse cost ratio: {th/per:,.0f}x")
    print()
    print("  the reverse answer is not stored anywhere. it is RECONSTRUCTED")
    print("  by visiting everything. that is not an implementation detail:")
    print("  there is no place in the structure where it could be stored,")
    print("  because a name is free to appear anywhere at any time.")
    print()

    print("=" * 78)
    print("3. THE KERNEL KEEPS THE MAGNITUDE, NOT THE DIRECTION")
    print("=" * 78)
    print()
    st = os.stat(tgt)
    print(f"  st_nlink on the target        : {st.st_nlink}")
    print(f"  hard links actually found     : {len(fh)} (+1 for the target "
          f"itself = {len(fh)+1})")
    print(f"  match                         : {st.st_nlink == len(fh)+1}")
    print()
    print("  so the kernel knows HOW MANY names point here, in O(1), stored")
    print("  in the inode. it does not know WHICH, and there is no call that")
    print("  will tell you. the mirror's magnitude is local; its direction")
    print("  is not.")
    print()
    lst = os.lstat(soft[0])
    print(f"  st_nlink on a symlink itself  : {lst.st_nlink}")
    print(f"  symlinks pointing at target   : {len(fs_)}")
    print(f"  does st_nlink count them?     : "
          f"{st.st_nlink == len(fh)+1+len(fs_)}")
    print()
    print("  for symlinks there is not even a magnitude. a symlink is a")
    print("  reference the target is not told about. it can be created,")
    print("  moved and deleted with the target never knowing.")
    print()

    print("=" * 78)
    print("4. WHERE TIME ENTERS")
    print("=" * 78)
    print()
    print("  forward resolution is time-free in the sense that matters: its")
    print("  cost does not depend on the size of the world. freeze the")
    print("  system clock and a symlink walk is unchanged.")
    print()
    print("  reverse resolution is not. its cost IS the size of the world,")
    print("  and the answer can be invalidated by a write anywhere. it has")
    print("  to be recomputed, and recomputation is where duration lives.")
    print()
    print("  so: the filesystem is timeless in the forward direction and")
    print("  has time only in the reverse one. that is not a metaphor. it")
    print("  is the measured ratio above.")
    print()

    print("=" * 78)
    print("5. THE NON-LOCAL CASE")
    print("=" * 78)
    print()
    print("  what is the cross-host equivalent of a symlink?")
    print()
    print("  structurally: a URI. symlink is to namei() as URI is to DNS")
    print("  plus the network stack. both are 'a name that resolves to")
    print("  another name'. the resolver is the only thing that differs.")
    print()
    print("  the difference that matters: a local resolution's cost is set")
    print("  by a count (SYMLOOP_MAX = 40, a number a human chose). a")
    print("  remote resolution's cost is set by distance, and it has a")
    print("  floor no one chose:")
    print()
    print(f"  {'link':>26} {'distance km':>13} {'RTT floor at c':>16}")
    print("  " + "-" * 58)
    for nm, km in [("same machine", 0.0), ("same rack", 0.002),
                   ("Pune -> Mumbai", 120), ("Pune -> Singapore", 3900),
                   ("Pune -> us-east-1", 13000)]:
        rtt = 2 * km / 299792.458 * 1000
        print(f"  {nm:>26} {km:>13} {rtt:>13.3f} ms")
    print()
    print("  and in fibre it is worse by a factor of about 1.47 (n = 1.47),")
    print("  so multiply the last column by that for a real floor.")
    print()
    print("  THE POINT: locally, reference is free, so hop count works as a")
    print("  clock and the environment can be made timeless without")
    print("  breaking anything. non-locally, reference COSTS, the cost is")
    print("  bounded below by c, and no amount of engineering removes it.")
    print()
    print("  so the mirror of a filesystem is not another filesystem. it is")
    print("  the same structure with the resolver replaced by one that")
    print("  cannot be free. that is where t and 1/t stop being")
    print("  interchangeable.")


if __name__ == "__main__":
    main()
