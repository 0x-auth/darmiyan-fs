#!/usr/bin/env python3
"""darmiyan.fs v1 — a minimal self-recursive universe on a Unix filesystem.
Rules live INSIDE the universe: each node holds its own state; a successor is
created only when an observer looks; closure happens only when the node's own
local error |f(x)-x| falls below the universe's own floor (.ε).
Usage: python3 darmiyan_fs.py [root] [digits]   (creates only under root and /tmp)"""
import os, sys, math, hashlib
from decimal import Decimal as D, getcontext

RULES = {  # Möbius pair: forward and its exact inverse
    "fwd": lambda x: 1 + 1 / x,
    "bwd": lambda x: 1 / (x - 1),
}

def genesis(root, digits, seed="1"):
    os.makedirs(root)
    open(f"{root}/.ε", "w").write(str(digits))              # floor lives inside
    void = f"/tmp/void-{os.getpid()}"                        # transient past
    os.symlink(void, f"{root}/Ø")                            # dangling: undefined
    for arrow in RULES:
        n0 = f"{root}/{arrow}/0"; os.makedirs(n0)
        open(f"{n0}/x", "w").write(seed)
        os.makedirs(f"{root}/{arrow}/.seen")
        os.symlink("../0", f"{root}/{arrow}/.seen/" + hashlib.sha1(seed.encode()).hexdigest())
        os.symlink("../../Ø", f"{n0}/prev")                  # origin -> undefined

def look(node, arrow, root):
    """Observer looks at a node. If its future isn't there, the node makes it."""
    nxt = f"{node}/next"
    if os.path.lexists(nxt):
        return os.path.realpath(nxt)
    getcontext().prec = int(open(f"{root}/.ε").read())
    x = D(open(f"{node}/x").read())
    fx = +RULES[arrow](x)
    if abs(fx - x) < D(10) ** -(getcontext().prec - 1):      # own error below own floor
        os.symlink(".", nxt); return os.path.realpath(node)  # closure
    seen = f"{os.path.dirname(node)}/.seen"; os.makedirs(seen, exist_ok=True)
    key = f"{seen}/{hashlib.sha1(str(fx).encode()).hexdigest()}"
    if os.path.lexists(key):                                  # state already exists: recognize by content
        tgt = os.path.basename(os.readlink(key))
        os.symlink(f"../{tgt}", nxt); return os.path.realpath(nxt)
    k = int(os.path.basename(node)) + 1
    new = f"{os.path.dirname(node)}/{k}"
    os.makedirs(new); open(f"{new}/x", "w").write(str(fx))
    os.symlink(f"../{os.path.basename(node)}", f"{new}/prev")
    os.symlink(f"../{k}", nxt)
    os.symlink(f"../{k}", key)
    return os.path.realpath(new)

def observe(root, arrow):
    node, seen = os.path.realpath(f"{root}/{arrow}/0"), set()
    while node not in seen:                                  # recognizes itself
        seen.add(node); node = look(node, arrow, root)
    return len(seen) - 1, D(open(f"{node}/x").read())

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "darmiyan.fs"
    digits = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    genesis(root, digits, seed="3")
    tf, f = observe(root, "fwd"); tb, b = observe(root, "bwd")
    getcontext().prec = digits
    print(f"ε = 1e-{digits}")
    print(f"forward : {tf:4d} ticks -> {f}")
    print(f"backward: {tb:4d} ticks -> {b}")
    print(f"f*b = {+(f*b)}   f+b = {+(f+b)}   f-b = {+(f-b)}")
    print(f"ticks/digit: fwd {tf/digits:.3f}  bwd {tb/digits:.3f}   theory {1/math.log10(((1+5**.5)/2)**2):.3f}")
    print(f"Ø exists? {os.path.exists(root+'/Ø')}   Ø named? {os.path.lexists(root+'/Ø')}")
