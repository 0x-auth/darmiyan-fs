"""
Resolver O -- the outside view.

Reads the link table. Never walks, never follows a link to its end, has no
proper time, and cannot fail. It recovers the law by exact rational algebra
from three node values.

Where the inside resolver reports a terminating failure, this one reports an
ordinary object. The gap between those two reports is the framework's output.
"""

from __future__ import annotations

import math
import os
from fractions import Fraction


class Outside:
    def __init__(self, path: str):
        self.path = path

    # ------------------------------------------------------------ the read

    def table(self) -> list[tuple[str, str]]:
        out = []
        for e in sorted(os.listdir(self.path)):
            link = os.path.join(self.path, e, "to")
            if os.path.islink(link):
                out.append((e, os.path.basename(os.readlink(link))))
        return out

    @staticmethod
    def _val(s: str) -> Fraction | None:
        if s == "inf":
            return None
        n, d = s.split("_")
        return Fraction(int(n), int(d))

    # ----------------------------------------------------------- the solve

    def recover(self) -> tuple[int, int, int, int] | None:
        """
        Solve a x + b - c x y - d y = 0 over the rationals for three finite
        pairs. Exact Gaussian elimination. Returns (a,b,c,d) up to scale.
        """
        pts = []
        for s, t in self.table():
            x, y = self._val(s), self._val(t)
            if x is not None and y is not None and x != y:
                pts.append((x, y))
            if len(pts) == 3:
                break
        if len(pts) < 3:
            return None
        M = [[x, Fraction(1), -x * y, -y] for x, y in pts]
        piv, row = [], 0
        for col in range(4):
            sel = next((r for r in range(row, 3) if M[r][col] != 0), None)
            if sel is None:
                continue
            M[row], M[sel] = M[sel], M[row]
            pv = M[row][col]
            M[row] = [v / pv for v in M[row]]
            for r in range(3):
                if r != row and M[r][col] != 0:
                    f = M[r][col]
                    M[r] = [M[r][k] - f * M[row][k] for k in range(4)]
            piv.append(col)
            row += 1
            if row == 3:
                break
        free = [c for c in range(4) if c not in piv]
        if not free:
            return None
        f = free[0]
        sol = [Fraction(0)] * 4
        sol[f] = Fraction(1)
        for i, c in enumerate(piv):
            sol[c] = -M[i][f]
        den = 1
        for v in sol:
            den = den * v.denominator // math.gcd(den, v.denominator)
        return tuple(int(v * den) for v in sol)  # type: ignore[return-value]

    # ------------------------------------------------------- the invariant

    def invariant(self) -> float | None:
        m = self.recover()
        if m is None:
            return None
        a, b, c, d = m
        det = a * d - b * c
        if det == 0:
            return None
        return (a + d) ** 2 / det

    def fixed_points(self) -> list[str]:
        m = self.recover()
        if m is None:
            return []
        a, b, c, d = m
        if c == 0:
            return ["infinity"] + ([] if a == d else [str(Fraction(b, d - a))])
        disc = (a - d) ** 2 + 4 * b * c
        if disc < 0:
            return ["complex pair (none on the real line)"]
        s = math.sqrt(disc)
        return [f"{(a - d + s) / (2 * c):.10f}", f"{(a - d - s) / (2 * c):.10f}"]
