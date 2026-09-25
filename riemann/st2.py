#!/usr/bin/env python3
"""S(T) computed correctly. See st.py header for the framing."""
import mpmath as mp
mp.mp.dps = 30

def smooth_N(T):
    return mp.siegeltheta(T)/mp.pi + 1

print("="*74)
print("S(T) = N(T) - [theta(T)/pi + 1]")
print("="*74)
print()
print(f"  {'T':>8} {'actual N(T)':>12} {'smooth':>14} {'S(T)':>11} {'log T':>9} {'|S|/logT':>10}")
print("  "+"-"*68)
rows=[]
for T in (20,50,100,200,500,1000,2000,5000,10000,20000):
    n = int(mp.nzeros(T))
    sm = float(smooth_N(T))
    S = n - sm
    lt = float(mp.log(T))
    rows.append((T,n,sm,S,lt))
    print(f"  {T:8d} {n:12d} {sm:14.5f} {S:11.6f} {lt:9.4f} {abs(S)/lt:10.5f}")
print()
ss=[r[3] for r in rows]
print(f"  min S      = {min(ss):+.6f}")
print(f"  max S      = {max(ss):+.6f}")
print(f"  mean S     = {sum(ss)/len(ss):+.6f}")
print(f"  max |S|    = {max(abs(s) for s in ss):.6f}")
print()
print("  N(T) grows like T log T. over this range:")
print(f"    N(20) = {rows[0][1]},  N(20000) = {rows[-1][1]}")
print(f"    ratio = {rows[-1][1]/max(rows[0][1],1):.0f}x")
print(f"  and S(T) stays inside [{min(ss):.3f}, {max(ss):.3f}].")
print()
print("  denser sample, to see the oscillation:")
print()
print(f"  {'T':>8} {'S(T)':>11}")
print("  "+"-"*21)
for T in range(1000, 1201, 20):
    n = int(mp.nzeros(T)); sm = float(smooth_N(T))
    print(f"  {T:8d} {n-sm:11.6f}")
