#!/usr/bin/env -S python3.10 -u

import sys
import time
from functools import reduce
from math import ceil
from itertools import takewhile,count,combinations_with_replacement as cwr
from pathos.multiprocessing import ProcessPool as Pool, cpu_count

# -------- find all valid numbers in a given base -------

# encode n in base b
E = lambda n,b: () if n==0 else E(n//b,b) + (n%b,)
# m controls whether 0^0 counts as 1 or 0
sp = lambda d,m: d**d if m else (0 if d==0 else d**d)
# take a vector of digits, raise each to its own power,
# and return the sum encoded in base b
msb = lambda v,b,m: E(sum(map(lambda n:sp(n,m), v)), b)
# predicate to test if a number in base b is valid
P = lambda x,b,m: sorted(msb(x,b,m)) == sorted(x)
# first number x such that x^x is greater than n
fm = lambda n: max(takewhile(lambda x:x**x<n, count()), default=0)+1
# return the digit combinations generator
def gcwr(b,d):
    t = fm(b**(d-1)/d)
    def g():
        for r in range(t, fm(b**d)):
            n = 0 if b==2 else ceil(b**(d-1)/(r**r))
            yield from ((r,)*n + c for c in cwr(range(fm(b**d)),d-n))

    return g()

# search for d-digit munchausen numbers in base b; 1 digit munchausen numbers are 1 and 0
fbdm = lambda b,d,m: (((0,),(1,)),((1,),))[m!=0] if d==1 else tuple(map(lambda v: msb(v,b,m), filter(lambda x: P(x,b,m), gcwr(b,d))))
# search base in all number of digits from 1 to b+1; generalizing the map to allow for use with process pools
fall = lambda b,m,mpr=map: reduce(lambda a,b:a+b, mpr(lambda d: fbdm(b,d,m), range(1,b+1)), ())

# searches all bases from sb to eb inclusive and prints results
# format for result:
#   base:number of found valid numbers:comma separated list of numbers
def search(sb,eb,m=1):
    with Pool(cpu_count()) as p:
        for b in range(sb,eb+1):
            start = time.perf_counter()
            # f = fall(b,m,map)
            f = fall(b,m,p.imap)
            end = time.perf_counter()
            s = ', '.join(map(lambda t: str(t).replace(' ',''), f))
            print(f"{b}:{m}:{len(f)}: {s}")
            print(f"computed base {b} in {end-start} seconds\n", file=sys.stderr)


if __name__ == "__main__":
    search(*map(int, sys.argv[1:]))
