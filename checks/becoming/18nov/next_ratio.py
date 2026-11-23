import math, cmath
from fractions import Fraction
from mpmath import mp, mpf, sqrt, pi, e as E, phi as PHI, identify
mp.dps=60
print('1. ONE MAP, TWO PERSPECTIVES: w = (t-1)/(t+1)')
for u in (0.5,2,5,20):
    t=math.exp(u); print(f'   boost  t=e^{u:<4}: w = {(t-1)/(t+1):.6f}  = tanh(u/2) {math.tanh(u/2):.6f}   (bounded, -> 1 as u -> inf)')
for th in (90,170,179,179.9):
    r=math.radians(th); t=cmath.exp(1j*r); w=(t-1)/(t+1)
    print(f'   turn   theta={th:<6}: w = {w.imag:+.4f} i  = i tan(theta/2) {math.tan(r/2):+.4f}   (d = 2 tan(theta/2) = {2*math.tan(r/2):.2f})')
print('   -> equal steps on the line = shrinking turns toward 180 deg; infinity sits at t = -1, the mirror point\n')

def seed_seq(p,n,s0=1):
    s=[mpf(s0)]
    for _ in range(n): s.append(p+1/s[-1])
    return s
def convergents(x,n):
    a=[];y=x
    for _ in range(n): k=int(mp.floor(y)); a.append(k); y=1/(y-k)
    h0,h1,k0,k1=1,a[0],0,1; out=[mpf(h1)/k1]
    for ai in a[1:]:
        h0,h1=h1,ai*h1+h0; k0,k1=k1,ai*k1+k0; out.append(mpf(h1)/k1)
    return out
def test(name,seq,target):
    print(f'   {name}')
    for i in (4,8,12):
        x=seq[i-4:i]                       # four past throws: high, low, high, low (alternating)
        dh=x[2]-x[0]; dl=x[3]-x[1]         # change between the two highs, and between the two lows
        nxt=dl/dh                          # the 'next' ratio, from four points, no target known
        guess=x[3]+nxt*(x[3]-x[2])         # next throw = last + next x (last step)
        limit=x[3]+(x[3]-x[2])*nxt/(1-nxt) # every future throw summed: where it ends up
        print(f'      from throws {i-4}-{i-1}: next = {mp.nstr(nxt,10):>14}   next-throw error {mp.nstr(abs(guess-seq[i]),3):>9}   predicted end vs true: {mp.nstr(abs(limit-target),3)}')
print('2. THE NEXT RATIO FROM FOUR THROWS (two highs, two lows)')
for p in (1,2,3,137):
    t=(p+sqrt(p*p+4))/2
    test(f'seed S -> {p} + 1/S, fixed point t = {mp.nstr(t,8)}, mirror of t^2: -1/t^2 = {mp.nstr(-1/t**2,10)}', seed_seq(p,14), t)
for nm,x in (('pi (no repeating pattern)',pi),('e',E)):
    test(f'continued-fraction throws for {nm}', convergents(x,14), x)
print('\n3. PRIME TIME sqrt(p^2+4): its continued fraction repeats (so its next is fixed)')
for p in (2,3,5,7,137):
    y=sqrt(p*p+4); a=[];z=y
    for _ in range(8): k=int(mp.floor(z)); a.append(k); z=1/(z-k)
    print(f'   p={p:3d}: sqrt(p^2+4) = {mp.nstr(y,12)}  continued fraction {a}')
