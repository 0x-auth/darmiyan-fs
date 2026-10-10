"""One command. `darmiyan <subcommand>`."""

from __future__ import annotations

import argparse
import json
import sys

from . import __version__, from_text, read, spec
from .selftest import verify
from .bridge import BridgeViolation
from .translate import KeywordTranslator
from . import substrate as sub_mod

CASES = ["golden", "boost", "shift", "parabolic", "rotation",
         "order3", "fixed", "horizon"]


def _row(r) -> str:
    di = f"{r.d_inside:.6f}" if r.d_inside is not None else "--"
    do = f"{r.d_outside:.6f}" if r.d_outside is not None else "--"
    return (f"  {r.name:>10} {di:>12} {do:>12} {r.agreement:>10} "
            f"{r.tau:>14.9f} {r.inside_says:>16}")


def cmd_read(args) -> int:
    r = from_text(args.text) if args.text else read(spec(
        name=args.name, a=args.a, b=args.b, c=args.c, d=args.d,
        seed=args.seed, steps=args.steps))
    if args.json:
        print(json.dumps(r.as_dict(), indent=2))
        return 0
    print(f"\n  relation     {r.name}")
    print(f"  D inside     {r.d_inside if r.d_inside is not None else '--'}")
    print(f"  D outside    {r.d_outside if r.d_outside is not None else '--'}")
    print(f"  agreement    {r.agreement}")
    print(f"  tau          {r.tau:.12f}      (inside only; outside is untimed)")
    print(f"  hops         {r.hops}")
    print(f"  inside says  {r.inside_says}"
          + (f"   errno {r.errno}" if r.errno else ""))
    print(f"  outside says {', '.join(r.outside_says) or '(not recoverable)'}")
    if r.disagreement:
        print(f"\n  {r.disagreement}")
    print()
    return 0


def cmd_suite(args) -> int:
    print("\n" + "=" * 78)
    print("  BRIDGE SUITE -- both charts, disjoint inputs, one invariant")
    print("=" * 78 + "\n")
    print(f"  {'relation':>10} {'D inside':>12} {'D outside':>12} "
          f"{'agreement':>10} {'tau':>14} {'inside says':>16}")
    print("  " + "-" * 76)
    bad = 0
    readings = []
    for name in CASES:
        try:
            r = from_text(name)
            readings.append(r)
            print(_row(r))
        except BridgeViolation as e:
            bad += 1
            print(f"  {name:>10}  BRIDGE VIOLATION: {e}")
    print()
    dis = [r for r in readings if r.disagreement]
    if dis:
        print("  WHERE THE CHARTS DISAGREE -- the payload:\n")
        for r in dis:
            print(f"    {r.disagreement}")
        print()
    print(f"  violations: {bad}")
    print("  a violation means the two charts are not describing the same")
    print("  relation, and the framework returns nothing rather than a")
    print("  number you would have to trust.\n")
    return 1 if bad else 0



def cmd_substrate(args) -> int:
    """The moving substrate. 1.0.0 only moved the walker."""
    W = 78
    if args.scan:
        print("\n" + "=" * W)
        print("  HORIZON SCAN -- p = 0, boundary predicted at D = 1/h")
        print("=" * W + "\n")
        print(f"  {'h':>10} {'1/h':>12} {'last arrives':>14} "
              f"{'first escapes':>15}")
        print("  " + "-" * 56)
        bad = 0
        for h in (0.2, 0.1, 0.05, 0.02, 0.01):
            lastok = firstbad = None
            for D0 in range(1, int(4 / h)):
                o = sub_mod.walk(D0, h, 0.0, ticks=20000)
                if o.outcome == "arrives":
                    lastok = D0
                else:
                    firstbad = D0
                    break
            print(f"  {h:>10.4f} {1/h:>12.2f} {str(lastok):>14} "
                  f"{str(firstbad):>15}")
            if firstbad is None or abs(firstbad - round(1 / h)) > 1:
                bad += 1
        print()
        print("  the boundary sits at 1/h, to the node. a Hubble radius out")
        print("  of nothing but an insertion rate -- and it is NOT a fixed")
        print("  point of a map. the relation never stops; the substrate")
        print("  outruns the walker.\n")
        return 1 if bad else 0

    print("\n" + "=" * W)
    print("  THE THREE OUTCOMES")
    print("=" * W + "\n")
    print(f"  {'p':>7} {'h':>10} {'D0':>8} {'outcome':>9} {'final D':>14} "
          f"{'floor D*':>14} {'stable':>7}")
    print("  " + "-" * 74)
    cases = [(0.0, 0.2, 3), (0.0, 0.2, 10), (1.0, 0.5, 50), (1.0, 2.0, 50),
             (2.0, 10.0, 100), (4 / 3, 100.0, 50), (6.0, 1e4, 50),
             (6.0, 10.0, 50)]
    if args.p is not None:
        cases = [(args.p, args.rate, args.start)]
    for p_, h_, d0 in cases:
        o = sub_mod.walk(d0, h_, p_, ticks=args.ticks)
        fl = f"{o.floor:.6f}" if o.floor is not None else "--"
        st = "--" if o.floor_stable is None else str(o.floor_stable)
        print(f"  {p_:>7.4f} {h_:>10.2f} {d0:>8} {o.outcome:>9} "
              f"{o.final_D:>14.6f} {fl:>14} {st:>7}")
    print()
    print("  ARRIVES   the ordinary case")
    print("  ESCAPES   a horizon; the substrate wins")
    print("  STALLS    a FLOOR -- neither arrival nor horizon. a minimum")
    print("            separation that can never be closed.")
    print()
    print("  the floor is D* = h^(1/(p-1)), stable iff D* > (p-1)/2.")
    print("  relaxation is D*/(p-1), so a SLOW floor and an UNSTABLE floor")
    print("  look identical if you do not run long enough.")
    print()
    print("  p = 0 gives a horizon. p > 1 never does, because a stretch that")
    print("  dilutes cannot outrun a constant step. the sky has a horizon,")
    print("  so the sky has p = 0 -- which is what 'Lambda is constant'")
    print("  means.\n")
    return 0

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="darmiyan",
        description="Two-chart emulator for self-referential relations.")
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("read", help="read one relation through both charts")
    r.add_argument("text", nargs="?", help="plain description, e.g. 'golden'")
    r.add_argument("--name", default="adhoc")
    r.add_argument("-a", type=int, default=1)
    r.add_argument("-b", type=int, default=1)
    r.add_argument("-c", type=int, default=1)
    r.add_argument("-d", type=int, default=0)
    r.add_argument("--seed", default=1)
    r.add_argument("--steps", type=int, default=28)
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_read)

    s = sub.add_parser("suite", help="run every known relation")
    s.set_defaults(func=cmd_suite)

    v = sub.add_parser("verify", help="run the framework's own contract tests")
    v.set_defaults(func=lambda a: verify())


    sb = sub.add_parser("substrate",
                        help="walk against a MOVING substrate (1.1.0)")
    sb.add_argument("--scan", action="store_true",
                    help="scan for the p=0 horizon at D = 1/h")
    sb.add_argument("-p", type=float, default=None, help="dilution exponent")
    sb.add_argument("--rate", type=float, default=1.0, help="stretch rate h")
    sb.add_argument("--start", type=float, default=50.0, help="initial D")
    sb.add_argument("--ticks", type=int, default=200000)
    sb.set_defaults(func=cmd_substrate)

    k = sub.add_parser("known", help="list what the translator understands")
    k.set_defaults(func=lambda a: (print(" ".join(
        sorted(KeywordTranslator.TABLE))), 0)[1])

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
