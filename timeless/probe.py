import time, os
from fractions import Fraction
print(f"  wall clock at start : {time.time():.6f}")
x = Fraction(1); tau = Fraction(0); prev = None
for i in range(25):
    if prev is not None:
        tau += abs(x - prev)
    prev = x
    x = 1 + 1/x
t = [time.time() for _ in range(5)]
print(f"  wall clock at end   : {time.time():.6f}")
print(f"  five reads in a row : {set(f'{v:.6f}' for v in t)}")
print(f"  monotonic clock     : {time.monotonic():.6f}")
print(f"  loop iterations     : 25")
print(f"  tau = sum|x_n - x_n+1| : {float(tau):.15f}")
